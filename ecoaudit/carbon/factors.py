"""
Emission Factor Registry.

Stores and retrieves emission factors with support for:
- Lookup by activity_type, year, source, and country
- Factor versioning (same activity, different years)
- Provenance tracking

Phase 1 includes a small set of clearly labelled TEST/EXAMPLE factors
derived from authoritative sources (UK DESNZ/DEFRA 2024, US EPA).
These are NOT production-grade emission factors.

The real emission-factor database will be built in Phase 2.
"""

from __future__ import annotations

import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

from ecoaudit.carbon.models import EmissionFactor
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


class FactorNotFoundError(Exception):
    """Raised when no matching emission factor is found in the registry."""


class EmissionFactorRegistry:
    """Registry for storing and looking up emission factors.

    Factors are indexed by (activity_type, year, source, country).
    """

    def __init__(self) -> None:
        self._factors: dict[str, EmissionFactor] = {}
        # Secondary index: (activity_type, year, source, country) → factor_id
        self._index: dict[tuple[str, int, str, str], str] = {}

    def register(self, factor: EmissionFactor) -> None:
        """Register an emission factor in the registry.

        Args:
            factor: The emission factor to register.

        Raises:
            ValueError: If a factor with the same factor_id already exists.
        """
        if factor.factor_id in self._factors:
            raise ValueError(
                f"Factor with ID '{factor.factor_id}' is already registered."
            )

        self._factors[factor.factor_id] = factor

        key = (
            factor.activity_type.lower(),
            factor.year,
            factor.source.lower(),
            factor.country.lower(),
        )
        self._index[key] = factor.factor_id

    def get_by_id(self, factor_id: str) -> EmissionFactor:
        """Retrieve a factor by its unique ID.

        Args:
            factor_id: The factor's unique identifier.

        Returns:
            The matching EmissionFactor.

        Raises:
            FactorNotFoundError: If no factor with that ID exists.
        """
        if factor_id not in self._factors:
            raise FactorNotFoundError(
                f"No emission factor found with ID '{factor_id}'."
            )
        return self._factors[factor_id]

    def lookup(
        self,
        activity_type: str,
        year: int,
        source: str | None = None,
        country: str | None = None,
        scope: Scope | None = None,
        category: Category | None = None,
    ) -> EmissionFactor:
        """Look up an emission factor by activity type and criteria.

        Args:
            activity_type: The activity type (e.g., "diesel").
            year: The reporting year.
            source: Optional source name filter.
            country: Optional country filter.
            scope: Optional scope filter.
            category: Optional category filter.

        Returns:
            The best matching EmissionFactor.

        Raises:
            FactorNotFoundError: If no matching factor is found.
        """
        candidates = []
        for factor in self._factors.values():
            if factor.activity_type.lower() != activity_type.lower():
                continue
            if factor.year != year:
                continue
            if source and factor.source.lower() != source.lower():
                continue
            if country and factor.country.lower() != country.lower():
                continue
            if scope and factor.scope != scope:
                continue
            if category and factor.category != category:
                continue
                
            candidates.append(factor)

        if not candidates:
            criteria = f"activity_type='{activity_type}', year={year}"
            if source:
                criteria += f", source='{source}'"
            if country:
                criteria += f", country='{country}'"
            if scope:
                criteria += f", scope='{scope.value}'"
            if category:
                criteria += f", category='{category.value}'"
            raise FactorNotFoundError(f"No emission factor found matching: {criteria}")

        if len(candidates) == 1:
            return candidates[0]

        # Multiple matches — warn and return the first one.
        # This indicates the registry needs more specific lookup criteria.
        logger.warning(
            "Multiple emission factors match criteria (%s). "
            "Returning first match: %s. Provide more specific lookup "
            "parameters (source, country, category) to avoid ambiguity.",
            criteria,
            candidates[0].factor_id,
        )
        return candidates[0]

    def list_all(self) -> list[EmissionFactor]:
        """Return all registered factors."""
        return list(self._factors.values())

    def __len__(self) -> int:
        return len(self._factors)


def load_test_factors() -> EmissionFactorRegistry:
    """Create a registry pre-loaded with TEST/EXAMPLE emission factors.

    ⚠️ WARNING: These are TEST DATA ONLY. ⚠️
    Values are derived from the DEFRA 2024 Condensed Set for illustration.
    They have been cross-referenced against the official publication but
    have NOT been independently audited for production use.
    The real emission-factor database will be built in Phase 2.

    Sources referenced:
    - UK DESNZ/DEFRA 2024 GHG Conversion Factors (Condensed Set)
      https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024
    - UK DESNZ/DEFRA 2023 GHG Conversion Factors (Condensed Set)
      https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2023

    Returns:
        An EmissionFactorRegistry loaded with test factors.
    """
    registry = EmissionFactorRegistry()

    # ---- Scope 1: Stationary Combustion ----

    # Diesel (average biofuel blend) — DEFRA 2024 Condensed Set, Fuels sheet
    # Corrected to actual DEFRA 2024 value: 2.51210 kgCO2e/litre
    # (NOT 100% mineral diesel which is 2.66155)
    registry.register(EmissionFactor(
        factor_id="TEST-DEFRA-2024-DIESEL-LITRE",
        activity_type="diesel",
        value=Decimal("2.51210"),
        unit="kgCO2e/litre",
        per_unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        country="UK",
        year=2024,
        source="UK DESNZ/DEFRA",
        source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        methodology="GHG Protocol / IPCC AR5 GWPs",
        version="DEFRA 2024 Condensed Set",
        gas_basis="CO2E",
        fuel_type_detail="Diesel (average biofuel blend)",
        dataset_name="Fuels",
        applicability_notes="Average biofuel blend as sold at UK forecourts. "
            "Use for general diesel consumption unless fuel is known to be "
            "100% mineral or a specific biodiesel blend.",
        is_test_data=True,
    ))

    # Diesel — DEFRA 2023 (to test versioning)
    # Approximate DEFRA 2023 value for average biofuel blend
    registry.register(EmissionFactor(
        factor_id="TEST-DEFRA-2023-DIESEL-LITRE",
        activity_type="diesel",
        value=Decimal("2.51260"),
        unit="kgCO2e/litre",
        per_unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        country="UK",
        year=2023,
        source="UK DESNZ/DEFRA",
        source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2023",
        methodology="GHG Protocol / IPCC AR5 GWPs",
        version="DEFRA 2023 Condensed Set",
        gas_basis="CO2E",
        fuel_type_detail="Diesel (average biofuel blend)",
        dataset_name="Fuels",
        applicability_notes="Average biofuel blend for 2023 reporting year.",
        is_test_data=True,
    ))

    # Natural gas — DEFRA 2024 (per kWh, Net Calorific Value)
    # Corrected to actual DEFRA 2024 value: 0.18316 kgCO2e/kWh
    registry.register(EmissionFactor(
        factor_id="TEST-DEFRA-2024-NATGAS-KWH",
        activity_type="natural_gas",
        value=Decimal("0.18316"),
        unit="kgCO2e/kWh",
        per_unit=Unit.KWH,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        country="UK",
        year=2024,
        source="UK DESNZ/DEFRA",
        source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        methodology="GHG Protocol / IPCC AR5 GWPs",
        version="DEFRA 2024 Condensed Set",
        gas_basis="CO2E",
        fuel_type_detail="Natural Gas",
        dataset_name="Fuels",
        applicability_notes="Net Calorific Value (NCV) basis. "
            "If activity data is in Gross CV, apply NCV/GCV ratio first.",
        is_test_data=True,
    ))

    # ---- Scope 1: Mobile Combustion ----

    # Petrol (average biofuel blend) — DEFRA 2024 Condensed Set
    # Corrected to actual DEFRA 2024 value: 2.16802 kgCO2e/litre
    registry.register(EmissionFactor(
        factor_id="TEST-DEFRA-2024-PETROL-LITRE",
        activity_type="petrol",
        value=Decimal("2.16802"),
        unit="kgCO2e/litre",
        per_unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.MOBILE_COMBUSTION,
        country="UK",
        year=2024,
        source="UK DESNZ/DEFRA",
        source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        methodology="GHG Protocol / IPCC AR5 GWPs",
        version="DEFRA 2024 Condensed Set",
        gas_basis="CO2E",
        fuel_type_detail="Petrol (average biofuel blend)",
        dataset_name="Fuels",
        applicability_notes="Average biofuel blend as sold at UK forecourts. "
            "For company-owned or controlled vehicles.",
        is_test_data=True,
    ))

    # ---- Scope 2: Purchased Electricity ----

    # UK grid electricity — DEFRA 2024 (location-based, generation only)
    # Corrected to actual DEFRA 2024 value: 0.20705 kgCO2e/kWh
    registry.register(EmissionFactor(
        factor_id="TEST-DEFRA-2024-ELEC-UK-KWH",
        activity_type="grid_electricity",
        value=Decimal("0.20705"),
        unit="kgCO2e/kWh",
        per_unit=Unit.KWH,
        scope=Scope.SCOPE_2,
        category=Category.PURCHASED_ELECTRICITY,
        country="UK",
        year=2024,
        source="UK DESNZ/DEFRA",
        source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        methodology="Location-based / GHG Protocol Scope 2 Guidance",
        version="DEFRA 2024 Condensed Set",
        gas_basis="CO2E",
        fuel_type_detail="UK Electricity (generation)",
        dataset_name="UK Electricity",
        applicability_notes="Location-based Scope 2 factor for UK grid "
            "electricity generation. Does NOT include T&D losses "
            "(report T&D losses separately under Scope 3).",
        is_test_data=True,
    ))

    # Egypt grid electricity — approximate test factor
    # Egypt does not have a DEFRA-equivalent official database.
    # Academic literature suggests ~0.50 kgCO2/kWh based on Egypt's
    # gas-heavy generation mix (~88% fossil fuels, primarily natural gas).
    # Source: EgyptERA and IEA country data (paywalled).
    # This value MUST be replaced with an authoritative source in Phase 2.
    registry.register(EmissionFactor(
        factor_id="TEST-APPROX-2023-ELEC-EG-KWH",
        activity_type="grid_electricity",
        value=Decimal("0.50000"),
        unit="kgCO2e/kWh",
        per_unit=Unit.KWH,
        scope=Scope.SCOPE_2,
        category=Category.PURCHASED_ELECTRICITY,
        country="Egypt",
        year=2023,
        source="Approximate (EgyptERA / IEA country data)",
        source_url="https://www.iea.org/countries/egypt",
        methodology="Location-based / Approximate grid intensity",
        version="Estimate based on 2022-2023 data",
        gas_basis="CO2E",
        fuel_type_detail="Egypt national grid electricity",
        dataset_name="N/A — estimated",
        applicability_notes="APPROXIMATE VALUE. Egypt's grid is ~88% "
            "natural gas with growing renewables. This factor must be "
            "replaced with an authoritative source (IEA or EgyptERA) "
            "before production use. Not suitable for audited reports.",
        is_test_data=True,
    ))

    return registry
