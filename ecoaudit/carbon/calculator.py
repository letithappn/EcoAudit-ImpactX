"""
Deterministic Carbon Calculation Engine.

Core principle: The AI is NOT the calculator.
All emission calculations are performed by deterministic, reproducible
Python code. The same input + same factor version = same result, always.

The engine:
1. Validates inputs
2. Converts units if necessary
3. Applies the formula: emissions = normalized_quantity × factor_value
4. Builds a complete audit trace
5. Returns an immutable CalculationResult

No LLM, no AI, no probabilistic logic is involved in the calculation.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from ecoaudit.carbon.factors import EmissionFactorRegistry
from ecoaudit.carbon.models import (
    ActivityData,
    BatchResult,
    CalculationResult,
    CalculationTrace,
    EmissionFactor,
)
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit, convert
from ecoaudit.carbon.validation import (
    validate_activity,
    validate_compatibility,
    validate_factor,
)


class CalculationError(Exception):
    """Raised when a calculation cannot be performed."""


class CarbonCalculator:
    """Deterministic carbon emission calculator.

    Given structured activity data and a traceable emission factor,
    produces auditable calculation results with full provenance.

    Usage:
        registry = load_test_factors()
        calculator = CarbonCalculator(registry)
        result = calculator.calculate(activity, factor)
    """

    def __init__(self, registry: EmissionFactorRegistry) -> None:
        """Initialize the calculator with a factor registry.

        Args:
            registry: The emission factor registry to use for lookups.
        """
        self._registry = registry

    @property
    def registry(self) -> EmissionFactorRegistry:
        """The emission factor registry used by this calculator."""
        return self._registry

    def calculate(
        self,
        activity: ActivityData,
        factor: EmissionFactor,
    ) -> CalculationResult:
        """Calculate emissions for a single activity.

        Formula: emissions = normalized_quantity × factor.value

        If the activity's unit differs from the factor's per_unit,
        unit conversion is performed first.

        Args:
            activity: The activity data (e.g., 10,000 litres diesel).
            factor: The emission factor to apply.

        Returns:
            A CalculationResult with the emissions value and full
            audit trace.

        Raises:
            ValidationError: If inputs fail validation.
            CalculationError: If the calculation cannot be performed.
        """
        # Step 1: Validate inputs.
        validate_activity(activity)
        validate_factor(factor)
        validate_compatibility(activity, factor)

        # Step 2: Unit normalization.
        if activity.unit != factor.per_unit:
            normalized_quantity, conversion_factor = convert(
                activity.quantity,
                activity.unit,
                factor.per_unit,
            )
            normalized_unit = factor.per_unit
        else:
            normalized_quantity = activity.quantity
            normalized_unit = activity.unit
            conversion_factor = Decimal("1")

        # Step 3: Deterministic calculation.
        emissions_value = normalized_quantity * factor.value

        # Step 4: Build audit trace.
        formula_desc = (
            f"{normalized_quantity} {normalized_unit.value} "
            f"× {factor.value} {factor.unit} "
            f"= {emissions_value} kgCO2e"
        )

        trace = CalculationTrace(
            input_quantity=activity.quantity,
            input_unit=activity.unit,
            normalized_quantity=normalized_quantity,
            normalized_unit=normalized_unit,
            conversion_factor_applied=conversion_factor,
            emission_factor_value=factor.value,
            emission_factor_unit=factor.unit,
            emission_factor_id=factor.factor_id,
            emission_factor_source=factor.source,
            emission_factor_year=factor.year,
            formula_description=formula_desc,
            scope=activity.scope,
            category=activity.category,
        )

        # Step 5: Build result.
        result = CalculationResult(
            result_id=str(uuid.uuid4()),
            activity=activity,
            factor=factor,
            emissions_value=emissions_value,
            emissions_unit="kgCO2e",
            trace=trace,
            calculated_at=datetime.now(timezone.utc),
        )

        return result

    def calculate_with_lookup(
        self,
        activity: ActivityData,
        year: int | None = None,
        source: str | None = None,
        country: str | None = None,
    ) -> CalculationResult:
        """Calculate emissions by looking up the factor from the registry.

        This is a convenience method that combines factor lookup and
        calculation. The activity's description or a mapping must
        resolve to an activity_type for the lookup.

        Args:
            activity: The activity data.
            year: Override year for factor lookup (defaults to current).
            source: Optional source filter for factor lookup.
            country: Optional country filter for factor lookup.

        Returns:
            A CalculationResult.

        Raises:
            FactorNotFoundError: If no matching factor is found.
            ValidationError: If inputs fail validation.
        """
        # For now, activity_type mapping is done via metadata.
        # In Phase 6 (AI Classification), this will be AI-assisted.
        activity_type = (
            activity.metadata.get("activity_type", "")
            if activity.metadata
            else ""
        )
        if not activity_type:
            raise CalculationError(
                "Cannot look up factor: activity.metadata must contain "
                "'activity_type' key (e.g., 'diesel', 'grid_electricity')."
            )

        lookup_year = year
        if lookup_year is None:
            raise CalculationError(
                "Cannot look up factor: 'year' must be specified for "
                "factor lookup (e.g., year=2024). There is no default year."
            )

        factor = self._registry.lookup(
            activity_type=activity_type,
            year=lookup_year,
            source=source,
            country=country,
        )

        return self.calculate(activity, factor)

    def calculate_batch(
        self,
        activities_and_factors: list[tuple[ActivityData, EmissionFactor]],
    ) -> BatchResult:
        """Calculate emissions for multiple activities and aggregate.

        Args:
            activities_and_factors: List of (activity, factor) pairs.

        Returns:
            A BatchResult with individual results, total emissions,
            and breakdowns by scope and category.

        Raises:
            ValidationError: If any input fails validation.
        """
        results: list[CalculationResult] = []
        scope_totals: dict[Scope, Decimal] = defaultdict(Decimal)
        category_totals: dict[Category, Decimal] = defaultdict(Decimal)
        total = Decimal("0")

        for activity, factor in activities_and_factors:
            result = self.calculate(activity, factor)
            results.append(result)
            total += result.emissions_value
            scope_totals[activity.scope] += result.emissions_value
            category_totals[activity.category] += result.emissions_value

        return BatchResult(
            results=tuple(results),
            total_emissions=total,
            scope_totals=dict(scope_totals),
            category_totals=dict(category_totals),
        )
