"""
Structured insight generation.

Generates deterministic, evidence-based analytical findings
from the aggregation and hotspot results.

Each insight has:
- A type (scope dominance, concentration, hotspot, etc.)
- A severity (critical, high, medium, low, info)
- A title (short summary)
- Evidence (the numerical facts)

The insights are structured data, not natural-language text.
An LLM may later explain them in human language, but the
numerical content is deterministic.
"""

from __future__ import annotations

from decimal import Decimal

from ecoaudit.intelligence.models import (
    CarbonInsight,
    CategoryBreakdown,
    DataQualitySummary,
    EmissionContribution,
    Hotspot,
    InsightType,
    ParetoResult,
    ScopeBreakdown,
    Severity,
    TrendAnalysis,
)


_ZERO = Decimal("0")
_HUNDRED = Decimal("100")


def generate_insights(
    scope_breakdown: ScopeBreakdown,
    category_breakdowns: tuple[CategoryBreakdown, ...],
    hotspots: tuple[Hotspot, ...],
    pareto: ParetoResult | None,
    trends: TrendAnalysis | None,
    data_quality: DataQualitySummary,
) -> tuple[CarbonInsight, ...]:
    """Generate deterministic, evidence-based insights.

    Args:
        scope_breakdown: Scope-level breakdown.
        category_breakdowns: Category breakdowns per scope.
        hotspots: Identified hotspots.
        pareto: Pareto analysis result.
        trends: Trend analysis result.
        data_quality: Data quality summary.

    Returns:
        Tuple of CarbonInsights, ordered by severity.
    """
    insights: list[CarbonInsight] = []

    # 1. Scope dominance insight
    insight = _scope_dominance_insight(scope_breakdown)
    if insight:
        insights.append(insight)

    # 2. Category concentration insights
    for breakdown in category_breakdowns:
        insight = _category_concentration_insight(breakdown)
        if insight:
            insights.append(insight)

    # 3. Hotspot insights
    for hotspot in hotspots:
        insights.append(_hotspot_insight(hotspot))

    # 4. Single source dominance
    insight = _single_source_dominance_insight(scope_breakdown)
    if insight:
        insights.append(insight)

    # 5. Pareto concentration insight
    if pareto:
        insight = _pareto_insight(pareto)
        if insight:
            insights.append(insight)

    # 6. Trend insight
    if trends and trends.is_sufficient_data:
        insight = _trend_insight(trends)
        if insight:
            insights.append(insight)

    # 7. Data quality insight
    insight = _data_quality_insight(data_quality)
    if insight:
        insights.append(insight)

    # Sort by severity (CRITICAL first)
    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }
    insights.sort(key=lambda i: severity_order.get(i.severity, 99))

    return tuple(insights)


def _scope_dominance_insight(
    breakdown: ScopeBreakdown,
) -> CarbonInsight | None:
    """Generate insight if one scope dominates emissions."""
    if not breakdown.contributions:
        return None

    top = breakdown.contributions[0]
    if top.percentage >= Decimal("60"):
        return CarbonInsight(
            insight_type=InsightType.SCOPE_DOMINANCE,
            severity=Severity.HIGH,
            title=f"{top.label} dominates total emissions",
            evidence=(
                f"{top.label} = {top.emissions:.2f} kgCO2e "
                f"({top.percentage:.1f}% of total {breakdown.total_emissions:.2f} kgCO2e)."
            ),
            detail=(
                f"This concentration means targeted reduction in {top.label} "
                f"could have the largest impact on the company's carbon footprint."
            ),
        )
    return None


def _single_source_dominance_insight(
    breakdown: ScopeBreakdown,
) -> CarbonInsight | None:
    """Generate insight if a single scope accounts for >80% of emissions."""
    if not breakdown.contributions:
        return None

    top = breakdown.contributions[0]
    if top.percentage >= Decimal("80"):
        return CarbonInsight(
            insight_type=InsightType.SINGLE_SOURCE_DOMINANCE,
            severity=Severity.CRITICAL,
            title=f"Emissions are overwhelmingly concentrated in {top.label}",
            evidence=(
                f"{top.label} accounts for {top.percentage:.1f}% of total emissions "
                f"({top.emissions:.2f} kgCO2e out of {breakdown.total_emissions:.2f} kgCO2e)."
            ),
            detail=(
                f"With over 80% concentration, any meaningful emission reduction "
                f"must address {top.label}."
            ),
        )
    return None


def _category_concentration_insight(
    breakdown: CategoryBreakdown,
) -> CarbonInsight | None:
    """Generate insight if a category dominates within its scope."""
    if not breakdown.contributions:
        return None

    top = breakdown.contributions[0]
    if top.percentage >= Decimal("60"):
        return CarbonInsight(
            insight_type=InsightType.CATEGORY_CONCENTRATION,
            severity=Severity.MEDIUM,
            title=(
                f"{top.label} dominates {breakdown.scope.value}"
            ),
            evidence=(
                f"{top.label} = {top.emissions:.2f} kgCO2e "
                f"({top.percentage:.1f}% of {breakdown.scope.value} emissions: "
                f"{breakdown.scope_emissions:.2f} kgCO2e)."
            ),
        )
    return None


def _hotspot_insight(hotspot: Hotspot) -> CarbonInsight:
    """Generate an insight for each identified hotspot."""
    scope_info = ""
    if hotspot.percentage_of_scope is not None and hotspot.parent_scope is not None:
        scope_info = (
            f" ({hotspot.percentage_of_scope:.1f}% of {hotspot.parent_scope.value})"
        )

    return CarbonInsight(
        insight_type=InsightType.HOTSPOT_IDENTIFIED,
        severity=hotspot.severity,
        title=f"Hotspot: {hotspot.label}",
        evidence=(
            f"{hotspot.emissions:.2f} kgCO2e = "
            f"{hotspot.percentage_of_total:.1f}% of total emissions{scope_info}. "
            f"Based on {hotspot.contributing_activities} activity record(s). "
            f"Actionability: {hotspot.actionability.value}."
        ),
        related_hotspots=(hotspot,),
    )


def _pareto_insight(pareto: ParetoResult) -> CarbonInsight | None:
    """Generate insight from Pareto analysis."""
    if not pareto.concentration_points:
        return None

    # Find: how many sources account for >= 80% of emissions?
    for top_n, cumulative_pct in pareto.concentration_points:
        if cumulative_pct >= Decimal("80"):
            proportion_of_sources = (
                Decimal(str(top_n)) / Decimal(str(pareto.total_sources)) * _HUNDRED
            )
            return CarbonInsight(
                insight_type=InsightType.PARETO_CONCENTRATION,
                severity=Severity.HIGH if proportion_of_sources <= Decimal("30") else Severity.MEDIUM,
                title=f"Top {top_n} {pareto.dimension}(s) account for {cumulative_pct:.1f}% of emissions",
                evidence=(
                    f"{top_n} out of {pareto.total_sources} {pareto.dimension}(s) "
                    f"({proportion_of_sources:.1f}% of sources) account for "
                    f"{cumulative_pct:.1f}% of total emissions "
                    f"({pareto.total_emissions:.2f} kgCO2e)."
                ),
                detail=(
                    f"Emissions are {'highly' if proportion_of_sources <= Decimal('30') else 'moderately'} "
                    f"concentrated. Targeting these top sources would address the majority of the footprint."
                ),
            )

    # If we never reach 80%, report the max
    last_n, last_pct = pareto.concentration_points[-1]
    return CarbonInsight(
        insight_type=InsightType.PARETO_CONCENTRATION,
        severity=Severity.INFO,
        title=f"All {last_n} {pareto.dimension}(s) contribute to emissions",
        evidence=(
            f"All {last_n} {pareto.dimension}(s) account for "
            f"{last_pct:.1f}% of total emissions."
        ),
    )


def _trend_insight(trends: TrendAnalysis) -> CarbonInsight | None:
    """Generate insight from trend analysis."""
    if trends.percentage_change is None:
        return None

    pct = trends.percentage_change
    if pct < _ZERO:
        return CarbonInsight(
            insight_type=InsightType.TREND_CHANGE,
            severity=Severity.INFO,
            title=f"Emissions decreased {abs(pct):.1f}% ({trends.earliest_period} to {trends.latest_period})",
            evidence=(
                f"Emissions changed by {trends.total_change:.2f} kgCO2e "
                f"({pct:.1f}%) from {trends.earliest_period} to {trends.latest_period}."
            ),
        )
    elif pct > _ZERO:
        severity = Severity.HIGH if pct >= Decimal("10") else Severity.MEDIUM
        return CarbonInsight(
            insight_type=InsightType.TREND_CHANGE,
            severity=severity,
            title=f"Emissions increased {pct:.1f}% ({trends.earliest_period} to {trends.latest_period})",
            evidence=(
                f"Emissions increased by {trends.total_change:.2f} kgCO2e "
                f"({pct:.1f}%) from {trends.earliest_period} to {trends.latest_period}."
            ),
        )
    else:
        return CarbonInsight(
            insight_type=InsightType.TREND_CHANGE,
            severity=Severity.INFO,
            title=f"Emissions unchanged ({trends.earliest_period} to {trends.latest_period})",
            evidence="No change in emissions between periods.",
        )


def _data_quality_insight(
    dq: DataQualitySummary,
) -> CarbonInsight | None:
    """Generate insight about data quality."""
    if dq.total_results == 0:
        return None

    issues: list[str] = []

    if dq.results_needing_review > 0:
        review_pct = (Decimal(str(dq.results_needing_review)) / Decimal(str(dq.total_results))) * _HUNDRED
        issues.append(
            f"{dq.results_needing_review}/{dq.total_results} results "
            f"({review_pct:.1f}%) are flagged for human review."
        )

    if dq.results_with_test_factors > 0:
        test_pct = (Decimal(str(dq.results_with_test_factors)) / Decimal(str(dq.total_results))) * _HUNDRED
        issues.append(
            f"{dq.results_with_test_factors}/{dq.total_results} results "
            f"({test_pct:.1f}%) use test/example emission factors."
        )

    if dq.min_ai_confidence is not None and dq.min_ai_confidence < Decimal("0.5"):
        issues.append(
            f"Minimum AI classification confidence is {dq.min_ai_confidence:.2f} "
            f"(some classifications may be unreliable)."
        )

    if not issues:
        return CarbonInsight(
            insight_type=InsightType.DATA_QUALITY,
            severity=Severity.INFO,
            title="Data quality appears adequate",
            evidence=(
                f"All {dq.total_results} results processed. "
                f"Factor sources: {', '.join(dq.factor_sources)}."
            ),
        )

    severity = Severity.MEDIUM if dq.results_needing_review > 0 else Severity.LOW
    return CarbonInsight(
        insight_type=InsightType.DATA_QUALITY,
        severity=severity,
        title="Data quality issues detected",
        evidence=" ".join(issues),
        detail=(
            "These findings should be validated before using results "
            "for external reporting or audit submission."
        ),
    )
