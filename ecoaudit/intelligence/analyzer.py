"""
Carbon Analyzer — main entry point for carbon intelligence.

Takes a BatchResult from the deterministic carbon calculator and
produces a complete CarbonIntelligenceReport with:
- Scope breakdown
- Category breakdowns
- Activity-level contributions
- Ranked hotspots
- Pareto concentration analysis
- Time trends
- Data quality summary
- Structured insights

All analysis is deterministic. No LLM is involved.
"""

from __future__ import annotations

from decimal import Decimal

from ecoaudit.carbon.models import BatchResult, CalculationResult
from ecoaudit.intelligence.aggregation import (
    aggregate_by_activity_type,
    aggregate_by_category,
    aggregate_by_scope,
)
from ecoaudit.intelligence.hotspots import (
    DEFAULT_HOTSPOT_THRESHOLD,
    identify_hotspots,
    pareto_analysis,
)
from ecoaudit.intelligence.insights import generate_insights
from ecoaudit.intelligence.models import (
    CarbonIntelligenceReport,
    DataQualitySummary,
    ScopeBreakdown,
)
from ecoaudit.intelligence.trends import analyze_trend


_ZERO = Decimal("0")


def _build_data_quality_summary(
    results: tuple[CalculationResult, ...],
) -> DataQualitySummary:
    """Build a data quality summary from calculation results.

    Uses only metadata that actually exists on the results.
    Does NOT invent confidence scores or quality metrics.
    """
    total = len(results)
    ai_classified = 0
    needs_review = 0
    test_factors = 0
    ai_confidences: list[Decimal] = []
    factor_sources: set[str] = set()

    for result in results:
        meta = result.activity.metadata or {}

        # Check for AI classification metadata
        if "ai_confidence" in meta:
            ai_classified += 1
            try:
                conf = Decimal(str(meta["ai_confidence"]))
                ai_confidences.append(conf)
            except Exception:
                pass

        if meta.get("ai_needs_review"):
            needs_review += 1

        # Check factor provenance
        if result.factor.is_test_data:
            test_factors += 1

        factor_sources.add(result.factor.source)

    avg_confidence: Decimal | None = None
    min_confidence: Decimal | None = None
    if ai_confidences:
        avg_confidence = sum(ai_confidences) / Decimal(str(len(ai_confidences)))
        min_confidence = min(ai_confidences)

    return DataQualitySummary(
        total_results=total,
        results_with_ai_classification=ai_classified,
        results_needing_review=needs_review,
        average_ai_confidence=avg_confidence,
        min_ai_confidence=min_confidence,
        results_with_test_factors=test_factors,
        factor_sources=tuple(sorted(factor_sources)),
    )


class CarbonAnalyzer:
    """Main entry point for carbon intelligence analysis.

    Takes a BatchResult and produces a complete CarbonIntelligenceReport.

    Usage:
        batch_result = calculator.calculate_batch(activities_and_factors)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch_result)
    """

    def __init__(
        self,
        hotspot_threshold: Decimal = DEFAULT_HOTSPOT_THRESHOLD,
        hotspot_dimension: str = "category",
    ) -> None:
        """Initialize the analyzer.

        Args:
            hotspot_threshold: Minimum % of total to flag as hotspot.
            hotspot_dimension: Dimension for hotspot analysis.
        """
        self._threshold = hotspot_threshold
        self._hotspot_dimension = hotspot_dimension

    def analyze(self, batch: BatchResult) -> CarbonIntelligenceReport:
        """Perform complete carbon intelligence analysis.

        Args:
            batch: A BatchResult from the carbon calculator.

        Returns:
            A CarbonIntelligenceReport with all analytical outputs.
        """
        # Handle empty batch
        if not batch.results:
            empty_breakdown = ScopeBreakdown(
                total_emissions=_ZERO,
                contributions=(),
            )
            dq = DataQualitySummary(
                total_results=0,
                results_with_ai_classification=0,
                results_needing_review=0,
                average_ai_confidence=None,
                min_ai_confidence=None,
                results_with_test_factors=0,
                factor_sources=(),
            )
            return CarbonIntelligenceReport(
                total_emissions=_ZERO,
                emissions_unit="kgCO2e",
                scope_breakdown=empty_breakdown,
                category_breakdowns=(),
                activity_contributions=(),
                hotspots=(),
                pareto=None,
                trends=None,
                data_quality=dq,
                insights=(),
                result_count=0,
            )

        # 1. Scope breakdown
        scope_breakdown = aggregate_by_scope(batch)

        # 2. Category breakdowns (per scope)
        category_breakdowns = tuple(aggregate_by_category(batch))

        # 3. Activity-type contributions
        activity_contributions = aggregate_by_activity_type(batch)

        # 4. Hotspot identification
        hotspots = identify_hotspots(
            batch,
            dimension=self._hotspot_dimension,
            threshold=self._threshold,
        )

        # 5. Pareto analysis
        pareto = pareto_analysis(batch, dimension=self._hotspot_dimension)

        # 6. Time trend analysis
        trends = analyze_trend(batch)

        # 7. Data quality summary
        data_quality = _build_data_quality_summary(batch.results)

        # 8. Generate insights
        insights = generate_insights(
            scope_breakdown=scope_breakdown,
            category_breakdowns=category_breakdowns,
            hotspots=hotspots,
            pareto=pareto,
            trends=trends,
            data_quality=data_quality,
        )

        return CarbonIntelligenceReport(
            total_emissions=batch.total_emissions,
            emissions_unit="kgCO2e",
            scope_breakdown=scope_breakdown,
            category_breakdowns=category_breakdowns,
            activity_contributions=activity_contributions,
            hotspots=hotspots,
            pareto=pareto,
            trends=trends,
            data_quality=data_quality,
            insights=insights,
            result_count=len(batch.results),
        )
