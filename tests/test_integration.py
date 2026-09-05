"""
Integration tests: multi-activity batch calculation with scope aggregation.

Uses corrected DEFRA 2024 Condensed Set values:
- Diesel (avg biofuel blend): 2.51210 kgCO2e/litre
- Petrol (avg biofuel blend): 2.16802 kgCO2e/litre
- UK electricity (generation): 0.20705 kgCO2e/kWh
"""

from decimal import Decimal

import pytest

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import EmissionFactorRegistry
from ecoaudit.carbon.models import ActivityData, EmissionFactor
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


class TestBatchCalculation:
    """Multi-activity batch calculation and aggregation."""

    def test_batch_scope_totals(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
        electricity_activity: ActivityData,
        electricity_factor_uk: EmissionFactor,
        petrol_activity: ActivityData,
        petrol_factor_2024: EmissionFactor,
    ) -> None:
        """Batch of 3 activities across Scope 1 and Scope 2."""
        batch = calculator.calculate_batch([
            (diesel_activity, diesel_factor_2024),
            (electricity_activity, electricity_factor_uk),
            (petrol_activity, petrol_factor_2024),
        ])

        # Individual expected values (corrected DEFRA 2024).
        diesel_expected = Decimal("10000") * Decimal("2.51210")
        elec_expected = Decimal("50000") * Decimal("0.20705")
        petrol_expected = Decimal("2000") * Decimal("2.16802")
        total_expected = diesel_expected + elec_expected + petrol_expected

        assert batch.total_emissions == total_expected
        assert len(batch.results) == 3

        # Scope totals.
        scope1_expected = diesel_expected + petrol_expected
        scope2_expected = elec_expected
        assert batch.scope_totals[Scope.SCOPE_1] == scope1_expected
        assert batch.scope_totals[Scope.SCOPE_2] == scope2_expected
        assert Scope.SCOPE_3 not in batch.scope_totals

        # Category totals.
        assert batch.category_totals[Category.STATIONARY_COMBUSTION] == diesel_expected
        assert batch.category_totals[Category.PURCHASED_ELECTRICITY] == elec_expected
        assert batch.category_totals[Category.MOBILE_COMBUSTION] == petrol_expected

    def test_batch_all_results_have_traces(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
        electricity_activity: ActivityData,
        electricity_factor_uk: EmissionFactor,
    ) -> None:
        """Every result in a batch must carry a complete trace."""
        batch = calculator.calculate_batch([
            (diesel_activity, diesel_factor_2024),
            (electricity_activity, electricity_factor_uk),
        ])

        for result in batch.results:
            assert result.trace is not None
            assert result.trace.emission_factor_id != ""
            assert result.trace.formula_description != ""
            assert result.trace.emission_factor_source != ""
            assert result.result_id != ""

    def test_batch_emissions_unit_consistent(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        """All results and the batch itself use kgCO2e."""
        batch = calculator.calculate_batch([
            (diesel_activity, diesel_factor_2024),
        ])

        assert batch.emissions_unit == "kgCO2e"
        for result in batch.results:
            assert result.emissions_unit == "kgCO2e"


class TestMultipleScopesEndToEnd:
    """End-to-end: realistic multi-scope company footprint."""

    def test_simulated_company_footprint(
        self,
        calculator: CarbonCalculator,
        registry: EmissionFactorRegistry,
    ) -> None:
        """Simulate a small company with diesel, petrol, electricity."""
        # Scope 1: 5,000L diesel for generator
        diesel = ActivityData(
            activity_id="E2E-001",
            description="Generator diesel",
            quantity=Decimal("5000"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        diesel_factor = registry.get_by_id("TEST-DEFRA-2024-DIESEL-LITRE")

        # Scope 1: 1,500L petrol for fleet
        petrol = ActivityData(
            activity_id="E2E-002",
            description="Fleet petrol",
            quantity=Decimal("1500"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.MOBILE_COMBUSTION,
        )
        petrol_factor = registry.get_by_id("TEST-DEFRA-2024-PETROL-LITRE")

        # Scope 2: 100,000 kWh electricity
        electricity = ActivityData(
            activity_id="E2E-003",
            description="Factory electricity",
            quantity=Decimal("100000"),
            unit=Unit.KWH,
            scope=Scope.SCOPE_2,
            category=Category.PURCHASED_ELECTRICITY,
        )
        elec_factor = registry.get_by_id("TEST-DEFRA-2024-ELEC-UK-KWH")

        batch = calculator.calculate_batch([
            (diesel, diesel_factor),
            (petrol, petrol_factor),
            (electricity, elec_factor),
        ])

        # Verify totals with corrected DEFRA 2024 values.
        d = Decimal("5000") * Decimal("2.51210")
        p = Decimal("1500") * Decimal("2.16802")
        e = Decimal("100000") * Decimal("0.20705")

        assert batch.scope_totals[Scope.SCOPE_1] == d + p
        assert batch.scope_totals[Scope.SCOPE_2] == e
        assert batch.total_emissions == d + p + e

        # Verify all traces are present.
        assert all(r.trace.emission_factor_source == "UK DESNZ/DEFRA"
                    for r in batch.results)
        assert all(r.factor.is_test_data for r in batch.results)
