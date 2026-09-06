"""
Deterministic emission aggregation engine.

Aggregates CalculationResults by scope, category, activity type,
and facility. All arithmetic uses Decimal. All percentages are
calculated deterministically.

No LLM is involved in any aggregation.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from ecoaudit.carbon.models import BatchResult, CalculationResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.intelligence.models import (
    CategoryBreakdown,
    EmissionContribution,
    ScopeBreakdown,
)


_ZERO = Decimal("0")
_HUNDRED = Decimal("100")


def _percentage(part: Decimal, total: Decimal) -> Decimal:
    """Calculate percentage safely, returning 0 if total is zero."""
    if total <= _ZERO:
        return _ZERO
    return (part / total) * _HUNDRED


def _rank_contributions(
    groups: dict[str, list[CalculationResult]],
    total_emissions: Decimal,
) -> tuple[EmissionContribution, ...]:
    """Rank groups by emissions and build EmissionContribution tuples.

    Args:
        groups: Mapping of label -> list of CalculationResults.
        total_emissions: The total to compute percentages against.

    Returns:
        Tuple of EmissionContributions sorted by emissions descending.
    """
    entries: list[tuple[str, Decimal, int, tuple[CalculationResult, ...]]] = []
    for label, results in groups.items():
        emissions = sum((r.emissions_value for r in results), _ZERO)
        entries.append((label, emissions, len(results), tuple(results)))

    # Sort by emissions descending, then by label for stability
    entries.sort(key=lambda e: (-e[1], e[0]))

    return tuple(
        EmissionContribution(
            label=label,
            emissions=emissions,
            percentage=_percentage(emissions, total_emissions),
            rank=rank,
            result_count=count,
            source_results=results,
        )
        for rank, (label, emissions, count, results) in enumerate(entries, start=1)
    )


def aggregate_by_scope(batch: BatchResult) -> ScopeBreakdown:
    """Aggregate emissions by GHG Protocol scope.

    Args:
        batch: A BatchResult from the carbon calculator.

    Returns:
        A ScopeBreakdown with scope-level contributions and percentages.
    """
    # Group results by scope
    scope_groups: dict[str, list[CalculationResult]] = defaultdict(list)
    for result in batch.results:
        scope_groups[result.activity.scope.value].append(result)

    contributions = _rank_contributions(scope_groups, batch.total_emissions)

    return ScopeBreakdown(
        total_emissions=batch.total_emissions,
        contributions=contributions,
    )


def aggregate_by_category(
    batch: BatchResult,
    scope: Scope | None = None,
) -> list[CategoryBreakdown]:
    """Aggregate emissions by category, optionally within a scope.

    Args:
        batch: A BatchResult from the carbon calculator.
        scope: If provided, only analyze this scope. Otherwise, analyze all.

    Returns:
        List of CategoryBreakdowns, one per scope present in the data.
    """
    # Group results by (scope, category)
    scope_cat_groups: dict[
        Scope, dict[str, list[CalculationResult]]
    ] = defaultdict(lambda: defaultdict(list))

    for result in batch.results:
        s = result.activity.scope
        if scope is not None and s != scope:
            continue
        cat_label = result.activity.category.value
        scope_cat_groups[s][cat_label].append(result)

    breakdowns: list[CategoryBreakdown] = []

    for s in sorted(scope_cat_groups.keys(), key=lambda x: x.value):
        cat_groups = scope_cat_groups[s]
        scope_emissions = sum(
            (r.emissions_value for results in cat_groups.values() for r in results),
            _ZERO,
        )
        contributions = _rank_contributions(cat_groups, scope_emissions)
        breakdowns.append(CategoryBreakdown(
            scope=s,
            scope_emissions=scope_emissions,
            contributions=contributions,
        ))

    return breakdowns


def aggregate_by_activity_type(
    batch: BatchResult,
) -> tuple[EmissionContribution, ...]:
    """Aggregate emissions by activity type (e.g., diesel, grid_electricity).

    Uses the 'activity_type' key from activity metadata.

    Args:
        batch: A BatchResult from the carbon calculator.

    Returns:
        Tuple of EmissionContributions ranked by emissions.
    """
    groups: dict[str, list[CalculationResult]] = defaultdict(list)
    for result in batch.results:
        activity_type = "unknown"
        if result.activity.metadata:
            activity_type = result.activity.metadata.get("activity_type", "unknown")
        groups[activity_type].append(result)

    return _rank_contributions(groups, batch.total_emissions)


def aggregate_by_facility(
    batch: BatchResult,
) -> tuple[EmissionContribution, ...]:
    """Aggregate emissions by facility (extracted from activity description).

    Uses the activity description prefix (before ' - ') as the facility name.
    Falls back to the full description if no separator exists.

    Args:
        batch: A BatchResult from the carbon calculator.

    Returns:
        Tuple of EmissionContributions ranked by emissions.
    """
    groups: dict[str, list[CalculationResult]] = defaultdict(list)
    for result in batch.results:
        desc = result.activity.description
        # Convention: "Facility - Description" or just "Description"
        if " - " in desc:
            facility = desc.split(" - ", 1)[0].strip()
        else:
            facility = desc.strip()
        groups[facility].append(result)

    return _rank_contributions(groups, batch.total_emissions)


def aggregate_by_dimension(
    batch: BatchResult,
    dimension: str,
) -> tuple[EmissionContribution, ...]:
    """Generic aggregation by a named dimension.

    Supported dimensions: scope, category, activity_type, facility.

    Args:
        batch: A BatchResult from the carbon calculator.
        dimension: The dimension to aggregate by.

    Returns:
        Tuple of EmissionContributions ranked by emissions.

    Raises:
        ValueError: If the dimension is not supported.
    """
    if dimension == "scope":
        breakdown = aggregate_by_scope(batch)
        return breakdown.contributions
    elif dimension == "category":
        groups: dict[str, list[CalculationResult]] = defaultdict(list)
        for result in batch.results:
            groups[result.activity.category.value].append(result)
        return _rank_contributions(groups, batch.total_emissions)
    elif dimension == "activity_type":
        return aggregate_by_activity_type(batch)
    elif dimension == "facility":
        return aggregate_by_facility(batch)
    else:
        raise ValueError(
            f"Unsupported dimension: '{dimension}'. "
            f"Supported: scope, category, activity_type, facility"
        )
