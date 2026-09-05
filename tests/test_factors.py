"""
Tests for the emission factor registry.

Covers:
- Registration and retrieval by ID
- Lookup by (activity_type, year, source, country)
- Factor versioning (same activity, different years)
- Missing factor raises FactorNotFoundError
- Duplicate ID rejection
- Factor provenance metadata
- New metadata fields (gas_basis, fuel_type_detail, dataset_name)
- All test factors carry is_test_data=True
"""

from decimal import Decimal

import pytest

from ecoaudit.carbon.factors import (
    EmissionFactorRegistry,
    FactorNotFoundError,
    load_test_factors,
)
from ecoaudit.carbon.models import EmissionFactor
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


class TestRegistryBasics:
    """Basic registration and retrieval."""

    def test_register_and_get_by_id(self, registry: EmissionFactorRegistry) -> None:
        factor = registry.get_by_id("TEST-DEFRA-2024-DIESEL-LITRE")
        assert factor.activity_type == "diesel"
        assert factor.year == 2024
        assert factor.is_test_data is True

    def test_get_unknown_id_raises(self, registry: EmissionFactorRegistry) -> None:
        with pytest.raises(FactorNotFoundError, match="NONEXISTENT"):
            registry.get_by_id("NONEXISTENT")

    def test_duplicate_id_rejected(self, registry: EmissionFactorRegistry) -> None:
        factor = registry.get_by_id("TEST-DEFRA-2024-DIESEL-LITRE")
        with pytest.raises(ValueError, match="already registered"):
            registry.register(factor)

    def test_registry_length(self, registry: EmissionFactorRegistry) -> None:
        # We registered 6 test factors in load_test_factors.
        assert len(registry) == 6

    def test_list_all(self, registry: EmissionFactorRegistry) -> None:
        all_factors = registry.list_all()
        assert len(all_factors) == 6
        assert all(f.is_test_data for f in all_factors)


class TestFactorLookup:
    """Lookup by activity_type, year, source, country."""

    def test_exact_lookup(self, registry: EmissionFactorRegistry) -> None:
        factor = registry.lookup(
            activity_type="diesel",
            year=2024,
            source="UK DESNZ/DEFRA",
            country="UK",
        )
        assert factor.factor_id == "TEST-DEFRA-2024-DIESEL-LITRE"

    def test_lookup_by_activity_and_year(self, registry: EmissionFactorRegistry) -> None:
        factor = registry.lookup(activity_type="petrol", year=2024)
        assert factor.factor_id == "TEST-DEFRA-2024-PETROL-LITRE"

    def test_lookup_case_insensitive(self, registry: EmissionFactorRegistry) -> None:
        factor = registry.lookup(
            activity_type="DIESEL",
            year=2024,
            source="uk desnz/defra",
            country="uk",
        )
        assert factor.factor_id == "TEST-DEFRA-2024-DIESEL-LITRE"

    def test_lookup_missing_activity_raises(self, registry: EmissionFactorRegistry) -> None:
        with pytest.raises(FactorNotFoundError):
            registry.lookup(activity_type="hydrogen", year=2024)

    def test_lookup_missing_year_raises(self, registry: EmissionFactorRegistry) -> None:
        with pytest.raises(FactorNotFoundError):
            registry.lookup(activity_type="diesel", year=2020)


class TestFactorVersioning:
    """Same activity type, different years → different factors."""

    def test_diesel_2024_vs_2023(self, registry: EmissionFactorRegistry) -> None:
        f2024 = registry.lookup(activity_type="diesel", year=2024)
        f2023 = registry.lookup(activity_type="diesel", year=2023)

        assert f2024.factor_id != f2023.factor_id
        assert f2024.year == 2024
        assert f2023.year == 2023
        # Values should differ between years.
        assert f2024.value != f2023.value

    def test_versioned_factors_same_source(self, registry: EmissionFactorRegistry) -> None:
        f2024 = registry.lookup(activity_type="diesel", year=2024)
        f2023 = registry.lookup(activity_type="diesel", year=2023)
        assert f2024.source == f2023.source == "UK DESNZ/DEFRA"


class TestFactorProvenance:
    """Every factor must carry full provenance metadata."""

    def test_provenance_fields_populated(self, registry: EmissionFactorRegistry) -> None:
        factor = registry.get_by_id("TEST-DEFRA-2024-DIESEL-LITRE")

        assert factor.source == "UK DESNZ/DEFRA"
        assert "gov.uk" in factor.source_url
        assert factor.methodology != ""
        assert factor.version != ""
        assert factor.country == "UK"
        assert factor.year == 2024
        assert factor.is_test_data is True

    def test_all_factors_have_provenance(self, registry: EmissionFactorRegistry) -> None:
        for factor in registry.list_all():
            assert factor.source, f"{factor.factor_id} missing source"
            assert factor.source_url, f"{factor.factor_id} missing source_url"
            assert factor.methodology, f"{factor.factor_id} missing methodology"
            assert factor.version, f"{factor.factor_id} missing version"
            assert factor.is_test_data is True, (
                f"{factor.factor_id} must be labelled as test data"
            )

    def test_gas_basis_populated(self, registry: EmissionFactorRegistry) -> None:
        """All factors should have gas_basis set."""
        for factor in registry.list_all():
            assert factor.gas_basis in ("CO2E", "CO2_ONLY"), (
                f"{factor.factor_id} has invalid gas_basis: {factor.gas_basis}"
            )


class TestElectricityFactorsByCountry:
    """Different countries should have different electricity factors."""

    def test_uk_vs_egypt_electricity(self, registry: EmissionFactorRegistry) -> None:
        uk = registry.lookup(
            activity_type="grid_electricity",
            year=2024,
            country="UK",
        )
        egypt = registry.lookup(
            activity_type="grid_electricity",
            year=2023,
            country="Egypt",
        )
        assert uk.value != egypt.value
        assert uk.country == "UK"
        assert egypt.country == "Egypt"


class TestCorrectedFactorValues:
    """Verify factor values match the DEFRA 2024 Condensed Set."""

    def test_diesel_is_avg_biofuel_blend(self, registry: EmissionFactorRegistry) -> None:
        """Diesel should be 2.51210 (avg biofuel), NOT 2.66155 (100% mineral)."""
        factor = registry.get_by_id("TEST-DEFRA-2024-DIESEL-LITRE")
        assert factor.value == Decimal("2.51210")
        assert "biofuel blend" in factor.fuel_type_detail.lower()

    def test_petrol_is_avg_biofuel_blend(self, registry: EmissionFactorRegistry) -> None:
        """Petrol should be 2.16802 (avg biofuel), NOT mineral value."""
        factor = registry.get_by_id("TEST-DEFRA-2024-PETROL-LITRE")
        assert factor.value == Decimal("2.16802")
        assert "biofuel blend" in factor.fuel_type_detail.lower()

    def test_uk_electricity_generation_only(self, registry: EmissionFactorRegistry) -> None:
        """UK electricity should be 0.20705 (generation only, no T&D losses)."""
        factor = registry.get_by_id("TEST-DEFRA-2024-ELEC-UK-KWH")
        assert factor.value == Decimal("0.20705")

    def test_natural_gas_net_cv(self, registry: EmissionFactorRegistry) -> None:
        """Natural gas should be 0.18316 (Net CV, DEFRA 2024)."""
        factor = registry.get_by_id("TEST-DEFRA-2024-NATGAS-KWH")
        assert factor.value == Decimal("0.18316")
