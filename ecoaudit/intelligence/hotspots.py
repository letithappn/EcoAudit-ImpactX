"""
Hotspot identification and Pareto/concentration analysis.

A hotspot is an emission source contributing a significant share
of total emissions. Identification is fully deterministic:
threshold-based with configurable parameters.

Methodology:
- Default threshold: >= 5% of total emissions
- Severity: Critical (>=25%), High (>=10%), Medium (>=5%), Low (<5%)
- Hotspots are ranked by absolute emissions descending
- Pareto analysis shows cumulative contribution of top N sources

No LLM is involved in hotspot identification.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from ecoaudit.carbon.models import BatchResult, CalculationResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.intelligence.aggregation import (
    _HUNDRED,
    _ZERO,
    _percentage,
    aggregate_by_dimension,
)
from ecoaudit.intelligence.models import (
    Actionability,
    EmissionContribution,
    Hotspot,
    ParetoResult,
    Severity,
)


# Default threshold: a source is a hotspot if it contributes >= 5%
DEFAULT_HOTSPOT_THRESHOLD = Decimal("5")


def _classify_severity(percentage: Decimal) -> Severity:
    """Classify severity based on percentage of total.

    Thresholds:
        >= 25%: CRITICAL — dominant emission source
        >= 10%: HIGH — major contributor
        >= 5%:  MEDIUM — significant contributor
        < 5%:   LOW — minor contributor
    """
    if percentage >= Decimal("25"):
        return Severity.CRITICAL
    elif percentage >= Decimal("10"):
        return Severity.HIGH
    elif percentage >= Decimal("5"):
        return Severity.MEDIUM
    else:
        return Severity.LOW


def _classify_actionability(
    scope: Scope | None,
    category: Category | None,
) -> Actionability:
    """Classify actionability based on scope and category.

    Methodology:
    - Scope 1 (direct emissions): ACTIONABLE — company controls the source.
    - Scope 2 (purchased energy): ACTIONABLE — company can switch suppliers,
      improve efficiency, or self-generate.
    - Scope 3 (value chain): PARTIALLY_ACTIONABLE — company can influence
      but does not directly control.
    - Unknown scope: INFORMATIONAL.
    """
    if scope is None:
        return Actionability.INFORMATIONAL

    if scope == Scope.SCOPE_1:
        return Actionability.ACTIONABLE
    elif scope == Scope.SCOPE_2:
        return Actionability.ACTIONABLE
    elif scope == Scope.SCOPE_3:
        return Actionability.PARTIALLY_ACTIONABLE
    else:
        return Actionability.INFORMATIONAL


def _infer_scope_category(
    results: tuple[CalculationResult, ...],
) -> tuple[Scope | None, Category | None]:
    """Infer the scope and category from a set of results.

    Returns the scope/category if all results share the same one,
    otherwise None (mixed).
    """
    scopes = {r.activity.scope for r in results}
    categories = {r.activity.category for r in results}

    scope = scopes.pop() if len(scopes) == 1 else None
    category = categories.pop() if len(categories) == 1 else None

    return scope, category


def identify_hotspots(
    batch: BatchResult,
    dimension: str = "category",
    threshold: Decimal = DEFAULT_HOTSPOT_THRESHOLD,
) -> tuple[Hotspot, ...]:
    """Identify emission hotspots in the given dimension.

    A hotspot is any source contributing >= threshold% of total emissions.

    Args:
        batch: A BatchResult from the carbon calculator.
        dimension: The dimension to analyze (scope, category, activity_type, facility).
        threshold: Minimum percentage of total to qualify as a hotspot.

    Returns:
        Tuple of Hotspots, ranked by emissions descending.
    """
    if batch.total_emissions <= _ZERO:
        return ()

    contributions = aggregate_by_dimension(batch, dimension)

    hotspots: list[Hotspot] = []
    for contrib in contributions:
        if contrib.percentage < threshold:
            continue  # Below threshold

        scope, category = _infer_scope_category(contrib.source_results)

        # Calculate percentage within scope if applicable
        pct_of_scope: Decimal | None = None
        if scope is not None:
            scope_total = batch.scope_totals.get(scope, _ZERO)
            if scope_total > _ZERO:
                pct_of_scope = _percentage(contrib.emissions, scope_total)

        hotspots.append(Hotspot(
            label=contrib.label,
            dimension=dimension,
            emissions=contrib.emissions,
            percentage_of_total=contrib.percentage,
            percentage_of_scope=pct_of_scope,
            severity=_classify_severity(contrib.percentage),
            rank=contrib.rank,
            actionability=_classify_actionability(scope, category),
            contributing_activities=contrib.result_count,
            source_results=contrib.source_results,
            parent_scope=scope,
            parent_category=category,
        ))

    return tuple(hotspots)


def pareto_analysis(
    batch: BatchResult,
    dimension: str = "category",
) -> ParetoResult | None:
    """Perform Pareto/concentration analysis.

    Calculates cumulative emission contribution of ranked sources.
    E.g., "Top 3 sources account for 72% of total emissions."

    Args:
        batch: A BatchResult from the carbon calculator.
        dimension: The dimension to analyze.

    Returns:
        A ParetoResult, or None if no data.
    """
    if batch.total_emissions <= _ZERO or not batch.results:
        return None

    contributions = aggregate_by_dimension(batch, dimension)
    if not contributions:
        return None

    # Build cumulative contribution points
    cumulative = _ZERO
    points: list[tuple[int, Decimal]] = []

    for i, contrib in enumerate(contributions, start=1):
        cumulative += contrib.emissions
        cumulative_pct = _percentage(cumulative, batch.total_emissions)
        points.append((i, cumulative_pct))

    return ParetoResult(
        dimension=dimension,
        total_sources=len(contributions),
        total_emissions=batch.total_emissions,
        concentration_points=tuple(points),
    )


def drill_down(
    hotspot: Hotspot,
    batch: BatchResult,
    sub_dimension: str = "activity_type",
) -> tuple[EmissionContribution, ...]:
    """Drill down into a hotspot to see its sub-components.

    Takes a hotspot and breaks it down by a sub-dimension.

    Args:
        hotspot: The hotspot to drill into.
        batch: The full BatchResult for context.
        sub_dimension: The dimension to drill down by.

    Returns:
        Tuple of EmissionContributions within the hotspot.
    """
    from collections import defaultdict

    if not hotspot.source_results:
        return ()

    hotspot_emissions = hotspot.emissions
    if hotspot_emissions <= _ZERO:
        return ()

    # Group the hotspot's results by sub_dimension
    groups: dict[str, list[CalculationResult]] = defaultdict(list)

    for result in hotspot.source_results:
        if sub_dimension == "activity_type":
            key = (result.activity.metadata or {}).get("activity_type", "unknown")
        elif sub_dimension == "facility":
            desc = result.activity.description
            key = desc.split(" - ", 1)[0].strip() if " - " in desc else desc.strip()
        elif sub_dimension == "scope":
            key = result.activity.scope.value
        elif sub_dimension == "category":
            key = result.activity.category.value
        else:
            key = "unknown"

        groups[key].append(result)

    # Rank within the hotspot
    entries: list[tuple[str, Decimal, int, tuple[CalculationResult, ...]]] = []
    for label, results in groups.items():
        emissions = sum((r.emissions_value for r in results), _ZERO)
        entries.append((label, emissions, len(results), tuple(results)))

    entries.sort(key=lambda e: (-e[1], e[0]))

    return tuple(
        EmissionContribution(
            label=label,
            emissions=emissions,
            percentage=_percentage(emissions, hotspot_emissions),
            rank=rank,
            result_count=count,
            source_results=results,
        )
        for rank, (label, emissions, count, results) in enumerate(entries, start=1)
    )
