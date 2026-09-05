"""
Domain models for the EcoAudit carbon calculation engine.

All models are frozen (immutable) dataclasses to ensure calculation
inputs and outputs cannot be mutated after creation. This supports
auditability and reproducibility.

Numeric fields use Decimal to avoid IEEE 754 floating-point errors.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


@dataclass(frozen=True)
class ActivityData:
    """A single activity record representing an emission source.

    Represents one line of operational data, e.g.,
    "10,000 litres of diesel consumed in factory generator".

    Attributes:
        activity_id: Unique identifier for this activity record.
        description: Human-readable description of the activity.
        quantity: Numeric amount of the activity (must be > 0).
        unit: Physical unit of the quantity.
        scope: GHG Protocol scope (1, 2, or 3).
        category: Emission category within the scope.
        source_file: Optional original source file path (for traceability).
        source_row: Optional row number in the source file.
        metadata: Optional dict for additional context (e.g., department,
            location, reporting period).
    """

    activity_id: str
    description: str
    quantity: Decimal
    unit: Unit
    scope: Scope
    category: Category
    source_file: str | None = None
    source_row: int | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class EmissionFactor:
    """An emission conversion factor with full provenance metadata.

    Every factor must be traceable to an authoritative source.
    The system must be able to answer:
    "Where did this factor come from?" and
    "Why was this factor used?"

    Attributes:
        factor_id: Unique identifier for this factor.
        activity_type: What activity this factor applies to
            (e.g., "diesel", "grid_electricity", "petrol").
        value: The numeric factor value (e.g., 2.51210 kgCO2e/litre).
        unit: The factor's unit expression
            (e.g., "kgCO2e/litre", "kgCO2e/kWh").
        per_unit: The Unit enum representing the denominator unit.
            This is used for unit compatibility checks.
        scope: The GHG Protocol scope this factor applies to.
        category: The emission category.
        country: Country or geography (e.g., "UK", "Egypt", "Global").
        year: The reporting year this factor applies to.
        source: Name of the authoritative source
            (e.g., "UK DESNZ/DEFRA", "US EPA").
        source_url: URL to the source publication.
        methodology: Methodology description
            (e.g., "GHG Protocol", "IPCC AR5").
        version: Version or edition identifier of the source
            (e.g., "2024 v1.0").
        gas_basis: Whether the factor represents CO2 only or CO2 equivalent
            including CH4 and N2O. One of "CO2E" or "CO2_ONLY".
            Default "CO2E" (most DEFRA factors are already CO2e).
        fuel_type_detail: Detailed fuel type descriptor from the source
            (e.g., "Diesel (average biofuel blend)",
            "Diesel (100% mineral diesel)"). Distinguishes sub-types
            that share the same activity_type.
        dataset_name: Name of the specific table/worksheet within the
            source publication (e.g., "Fuels", "UK Electricity",
            "WTT- fuels").
        applicability_notes: Free-text notes about when this factor
            should or should not be used (e.g., "Use for UK road
            transport only", "Not applicable to off-road vehicles").
        is_test_data: Whether this factor is test/example data only.
            MUST be True for all Phase 1 factors. Production factors
            from authoritative sources should set this to False.
    """

    factor_id: str
    activity_type: str
    value: Decimal
    unit: str
    per_unit: Unit
    scope: Scope
    category: Category
    country: str
    year: int
    source: str
    source_url: str
    methodology: str
    version: str
    gas_basis: str = "CO2E"
    fuel_type_detail: str = ""
    dataset_name: str = ""
    applicability_notes: str = ""
    is_test_data: bool = True


@dataclass(frozen=True)
class CalculationTrace:
    """Complete audit trace for a single emission calculation.

    Every field needed to fully reconstruct the calculation:
    input → unit conversion → emission factor → formula → result.

    Attributes:
        input_quantity: Original quantity from the activity data.
        input_unit: Original unit from the activity data.
        normalized_quantity: Quantity after unit conversion (if any).
        normalized_unit: Unit after conversion (matches factor's per_unit).
        conversion_factor_applied: The unit conversion multiplier used
            (Decimal("1") if no conversion was needed).
        emission_factor_value: The emission factor value used.
        emission_factor_unit: The emission factor unit string.
        emission_factor_id: The factor_id for traceability.
        emission_factor_source: The source name of the factor.
        emission_factor_year: The year of the factor.
        formula_description: Human-readable formula string
            (e.g., "10000 litre × 2.706 kgCO2e/litre = 27060.000 kgCO2e").
        scope: The GHG Protocol scope.
        category: The emission category.
    """

    input_quantity: Decimal
    input_unit: Unit
    normalized_quantity: Decimal
    normalized_unit: Unit
    conversion_factor_applied: Decimal
    emission_factor_value: Decimal
    emission_factor_unit: str
    emission_factor_id: str
    emission_factor_source: str
    emission_factor_year: int
    formula_description: str
    scope: Scope
    category: Category


@dataclass(frozen=True)
class CalculationResult:
    """The result of a single emission calculation with full audit trail.

    Attributes:
        result_id: Unique UUID for this result.
        activity: The input activity data.
        factor: The emission factor used.
        emissions_value: Calculated emissions in kgCO2e.
        emissions_unit: Always "kgCO2e" for consistency.
        trace: Complete audit trace for this calculation.
        calculated_at: UTC timestamp of when the calculation was performed.
    """

    result_id: str
    activity: ActivityData
    factor: EmissionFactor
    emissions_value: Decimal
    emissions_unit: str
    trace: CalculationTrace
    calculated_at: datetime


@dataclass(frozen=True)
class BatchResult:
    """Aggregated results from calculating multiple activities.

    Attributes:
        results: List of individual CalculationResults.
        total_emissions: Total emissions across all activities (kgCO2e).
        scope_totals: Emissions broken down by scope.
        category_totals: Emissions broken down by category.
        emissions_unit: Always "kgCO2e".
    """

    results: tuple[CalculationResult, ...]
    total_emissions: Decimal
    scope_totals: dict[Scope, Decimal]
    category_totals: dict[Category, Decimal]
    emissions_unit: str = "kgCO2e"
