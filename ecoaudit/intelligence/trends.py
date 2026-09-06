"""
Time-based trend analysis.

Analyzes emissions over time periods (year, quarter, month).
Detects period information from activity metadata and descriptions.

All calculations are deterministic. The module explicitly identifies
when data is insufficient for trend analysis rather than guessing.

No LLM is involved in trend calculations.
"""

from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal

from ecoaudit.carbon.models import BatchResult, CalculationResult
from ecoaudit.intelligence.models import TrendAnalysis, TrendPoint


_ZERO = Decimal("0")
_HUNDRED = Decimal("100")

# Minimum number of distinct periods required for trend analysis
MIN_PERIODS_FOR_TREND = 2


def _extract_period(result: CalculationResult) -> str | None:
    """Extract a time period from a CalculationResult.

    Checks (in order):
    1. metadata["period"] — explicit period label
    2. metadata["year"] — explicit year
    3. metadata["date"] — parseable date string
    4. activity description — year pattern (4 digits)
    5. factor.year — emission factor year (last resort)

    Returns:
        Period string (e.g., "2024", "2024-Q1", "2024-05"), or None.
    """
    meta = result.activity.metadata or {}

    # 1. Explicit period
    if "period" in meta:
        return str(meta["period"]).strip()

    # 2. Explicit year
    if "year" in meta:
        return str(meta["year"]).strip()

    # 3. Date string
    if "date" in meta:
        return _parse_date_to_period(str(meta["date"]))

    # 4. Description year pattern
    desc = result.activity.description
    year_match = re.search(r"\b(20\d{2})\b", desc)
    if year_match:
        return year_match.group(1)

    # 5. Factor year (very rough — same year for all activities using same factors)
    if result.factor.year:
        return str(result.factor.year)

    return None


def _parse_date_to_period(date_str: str) -> str | None:
    """Parse a date string into a year period.

    Handles common formats:
    - YYYY-MM-DD
    - YYYY/MM/DD
    - MM/DD/YYYY
    - YYYY

    Returns year string, or None if unparseable.
    """
    date_str = date_str.strip()

    # YYYY-MM-DD or YYYY/MM/DD
    match = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", date_str)
    if match:
        return match.group(1)

    # MM/DD/YYYY
    match = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", date_str)
    if match:
        return match.group(3)

    # Just a year
    match = re.match(r"^(20\d{2})$", date_str)
    if match:
        return match.group(1)

    return None


def analyze_trend(
    batch: BatchResult,
    min_periods: int = MIN_PERIODS_FOR_TREND,
) -> TrendAnalysis:
    """Analyze emission trends over time.

    Groups results by period, calculates per-period totals,
    and computes period-over-period change.

    Explicitly identifies insufficient data rather than guessing trends.

    Args:
        batch: A BatchResult from the carbon calculator.
        min_periods: Minimum distinct periods required for trend analysis.

    Returns:
        A TrendAnalysis with trend points and change calculations.
    """
    if not batch.results:
        return TrendAnalysis(
            points=(),
            earliest_period="",
            latest_period="",
            total_change=None,
            percentage_change=None,
            is_sufficient_data=False,
            insufficient_reason="No calculation results to analyze.",
        )

    # Group results by period
    period_groups: dict[str, list[CalculationResult]] = defaultdict(list)
    unclassified = 0

    for result in batch.results:
        period = _extract_period(result)
        if period:
            period_groups[period].append(result)
        else:
            unclassified += 1

    if not period_groups:
        return TrendAnalysis(
            points=(),
            earliest_period="",
            latest_period="",
            total_change=None,
            percentage_change=None,
            is_sufficient_data=False,
            insufficient_reason="No time-period information found in any result.",
        )

    # Build trend points sorted by period
    points: list[TrendPoint] = []
    for period in sorted(period_groups.keys()):
        results = period_groups[period]
        emissions = sum((r.emissions_value for r in results), _ZERO)
        points.append(TrendPoint(
            period=period,
            emissions=emissions,
            result_count=len(results),
        ))

    earliest = points[0].period
    latest = points[-1].period
    distinct_periods = len(points)

    # Check sufficiency
    if distinct_periods < min_periods:
        return TrendAnalysis(
            points=tuple(points),
            earliest_period=earliest,
            latest_period=latest,
            total_change=None,
            percentage_change=None,
            is_sufficient_data=False,
            insufficient_reason=(
                f"Only {distinct_periods} distinct period(s) found. "
                f"Minimum {min_periods} required for trend analysis."
            ),
        )

    # Calculate change
    first_emissions = points[0].emissions
    last_emissions = points[-1].emissions
    total_change = last_emissions - first_emissions

    percentage_change: Decimal | None = None
    if first_emissions > _ZERO:
        percentage_change = (total_change / first_emissions) * _HUNDRED

    return TrendAnalysis(
        points=tuple(points),
        earliest_period=earliest,
        latest_period=latest,
        total_change=total_change,
        percentage_change=percentage_change,
        is_sufficient_data=True,
    )
