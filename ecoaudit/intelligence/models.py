"""
Analytical data models for Carbon Intelligence.

All models are frozen dataclasses with Decimal arithmetic.
These represent the OUTPUT of deterministic analysis — no LLM
is involved in producing any values in these models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any

from ecoaudit.carbon.models import CalculationResult
from ecoaudit.carbon.scopes import Category, Scope


# --- Enums ---


class Severity(Enum):
    """Severity level for insights and hotspots."""
    CRITICAL = "critical"  # >= 25% of total
    HIGH = "high"          # >= 10% of total
    MEDIUM = "medium"      # >= 5% of total
    LOW = "low"            # < 5% of total
    INFO = "info"          # Informational only


class Actionability(Enum):
    """Whether a source is potentially actionable or informational."""
    ACTIONABLE = "actionable"
    PARTIALLY_ACTIONABLE = "partially_actionable"
    INFORMATIONAL = "informational"


class InsightType(Enum):
    """Type of analytical insight."""
    SCOPE_DOMINANCE = "scope_dominance"
    CATEGORY_CONCENTRATION = "category_concentration"
    HOTSPOT_IDENTIFIED = "hotspot_identified"
    PARETO_CONCENTRATION = "pareto_concentration"
    TREND_CHANGE = "trend_change"
    DATA_QUALITY = "data_quality"
    SINGLE_SOURCE_DOMINANCE = "single_source_dominance"


# --- Core Contribution Model ---


@dataclass(frozen=True)
class EmissionContribution:
    """A single source's contribution to total emissions.

    This is the generic building block for all breakdown analyses.
    It represents one row in a scope/category/activity breakdown.

    Attributes:
        label: Human-readable name of the source.
        emissions: Absolute emissions in kgCO2e.
        percentage: Percentage of the relevant total (0-100).
        rank: Position in the ranked list (1 = highest emitter).
        result_count: Number of calculation results contributing to this.
        source_results: The underlying CalculationResults (for drill-down).
    """
    label: str
    emissions: Decimal
    percentage: Decimal
    rank: int
    result_count: int = 0
    source_results: tuple[CalculationResult, ...] = ()


# --- Scope & Category Breakdowns ---


@dataclass(frozen=True)
class ScopeBreakdown:
    """Emission breakdown by GHG Protocol scope.

    Attributes:
        total_emissions: Total emissions across all scopes (kgCO2e).
        contributions: List of scope contributions, ranked by emissions.
        emissions_unit: Always "kgCO2e".
    """
    total_emissions: Decimal
    contributions: tuple[EmissionContribution, ...]
    emissions_unit: str = "kgCO2e"


@dataclass(frozen=True)
class CategoryBreakdown:
    """Emission breakdown by category within a scope.

    Attributes:
        scope: The scope this breakdown belongs to.
        scope_emissions: Total emissions for this scope.
        contributions: List of category contributions, ranked by emissions.
    """
    scope: Scope
    scope_emissions: Decimal
    contributions: tuple[EmissionContribution, ...]


# --- Hotspot Models ---


@dataclass(frozen=True)
class Hotspot:
    """An identified emission hotspot.

    A hotspot is a source that contributes a significant share of
    total emissions, identified by deterministic threshold analysis.

    Attributes:
        label: Human-readable name.
        dimension: The analytical dimension (e.g., "scope", "category", "activity_type").
        emissions: Absolute emissions (kgCO2e).
        percentage_of_total: Percentage of company-wide total.
        percentage_of_scope: Percentage within the relevant scope (if applicable).
        severity: Severity classification based on contribution.
        rank: Global rank among all sources in this dimension.
        actionability: Whether this source is potentially actionable.
        contributing_activities: Number of activities behind this hotspot.
        source_results: The underlying CalculationResults for drill-down.
        parent_scope: The scope this hotspot falls under (if applicable).
        parent_category: The category this hotspot falls under (if applicable).
    """
    label: str
    dimension: str
    emissions: Decimal
    percentage_of_total: Decimal
    percentage_of_scope: Decimal | None
    severity: Severity
    rank: int
    actionability: Actionability
    contributing_activities: int
    source_results: tuple[CalculationResult, ...] = ()
    parent_scope: Scope | None = None
    parent_category: Category | None = None


@dataclass(frozen=True)
class ParetoResult:
    """Result of Pareto/concentration analysis.

    Answers: "What share of emissions comes from the top N sources?"

    Attributes:
        dimension: The analytical dimension analyzed.
        total_sources: Total number of distinct sources.
        total_emissions: Total emissions (kgCO2e).
        concentration_points: List of (top_n, cumulative_percentage) pairs.
    """
    dimension: str
    total_sources: int
    total_emissions: Decimal
    concentration_points: tuple[tuple[int, Decimal], ...]


# --- Time Analysis ---


@dataclass(frozen=True)
class TrendPoint:
    """A single data point in a time trend.

    Attributes:
        period: The time period label (e.g., "2024", "2024-Q1", "2024-01").
        emissions: Total emissions for this period (kgCO2e).
        result_count: Number of calculations in this period.
    """
    period: str
    emissions: Decimal
    result_count: int


@dataclass(frozen=True)
class TrendAnalysis:
    """Time-based trend analysis.

    Attributes:
        points: Ordered list of trend points.
        earliest_period: The first period in the dataset.
        latest_period: The last period in the dataset.
        total_change: Absolute change from first to last period (kgCO2e).
        percentage_change: Percentage change from first to last.
        is_sufficient_data: Whether there are enough periods for trend analysis.
        insufficient_reason: If not sufficient, why.
    """
    points: tuple[TrendPoint, ...]
    earliest_period: str
    latest_period: str
    total_change: Decimal | None
    percentage_change: Decimal | None
    is_sufficient_data: bool
    insufficient_reason: str = ""


# --- Data Quality ---


@dataclass(frozen=True)
class DataQualitySummary:
    """Aggregated data quality information across results.

    Uses only metadata that actually exists on the results —
    does not invent confidence scores.

    Attributes:
        total_results: Total number of calculation results.
        results_with_ai_classification: Results that were AI-classified.
        results_needing_review: Results flagged for human review.
        average_ai_confidence: Mean AI confidence (None if no AI results).
        min_ai_confidence: Minimum AI confidence (None if no AI results).
        results_with_test_factors: Results using is_test_data=True factors.
        factor_sources: Distinct factor sources used.
    """
    total_results: int
    results_with_ai_classification: int
    results_needing_review: int
    average_ai_confidence: Decimal | None
    min_ai_confidence: Decimal | None
    results_with_test_factors: int
    factor_sources: tuple[str, ...]


# --- Insights ---


@dataclass(frozen=True)
class CarbonInsight:
    """A structured, evidence-based analytical finding.

    The insight itself is deterministic — the severity and evidence
    are calculated, not generated by an LLM.

    Attributes:
        insight_type: The type of insight.
        severity: How important this finding is.
        title: Short summary (e.g., "Scope 2 dominates emissions").
        evidence: The numerical evidence supporting this insight.
        detail: More detailed structured explanation.
        related_hotspots: Hotspots related to this insight.
    """
    insight_type: InsightType
    severity: Severity
    title: str
    evidence: str
    detail: str = ""
    related_hotspots: tuple[Hotspot, ...] = ()


# --- Top-Level Report ---


@dataclass(frozen=True)
class CarbonIntelligenceReport:
    """Complete carbon intelligence report.

    This is the top-level output of the analytical layer.
    Contains all breakdowns, hotspots, insights, and data quality info.

    Attributes:
        total_emissions: Total emissions (kgCO2e).
        emissions_unit: Always "kgCO2e".
        scope_breakdown: Scope-level breakdown.
        category_breakdowns: Category breakdown per scope.
        activity_contributions: Activity-type level contributions.
        hotspots: Identified hotspots, ranked.
        pareto: Pareto concentration analysis.
        trends: Time-based analysis (if time data exists).
        data_quality: Data quality summary.
        insights: Structured analytical insights.
        result_count: Total number of calculation results analyzed.
    """
    total_emissions: Decimal
    emissions_unit: str
    scope_breakdown: ScopeBreakdown
    category_breakdowns: tuple[CategoryBreakdown, ...]
    activity_contributions: tuple[EmissionContribution, ...]
    hotspots: tuple[Hotspot, ...]
    pareto: ParetoResult | None
    trends: TrendAnalysis | None
    data_quality: DataQualitySummary
    insights: tuple[CarbonInsight, ...]
    result_count: int
