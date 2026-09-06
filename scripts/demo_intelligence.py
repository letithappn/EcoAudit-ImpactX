"""
Generate example analytical output for documentation.

Usage:
    python scripts/demo_intelligence.py
"""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import load_test_factors
from ecoaudit.carbon.models import ActivityData
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.intelligence.analyzer import CarbonAnalyzer


def main() -> None:
    registry = load_test_factors()
    calculator = CarbonCalculator(registry)

    # Build a realistic company footprint
    activities_and_factors = [
        (ActivityData(
            activity_id="D1", description="Factory A - Diesel generator",
            quantity=Decimal("10000"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
            metadata={"activity_type": "diesel"},
        ), registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)),
        (ActivityData(
            activity_id="D2", description="Factory B - Diesel boiler",
            quantity=Decimal("5000"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
            metadata={"activity_type": "diesel"},
        ), registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)),
        (ActivityData(
            activity_id="P1", description="Fleet - Company cars petrol",
            quantity=Decimal("3000"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.MOBILE_COMBUSTION,
            metadata={"activity_type": "petrol"},
        ), registry.lookup("petrol", 2024, country="UK")),
        (ActivityData(
            activity_id="E1", description="HQ Office - Grid electricity",
            quantity=Decimal("200000"), unit=Unit.KWH,
            scope=Scope.SCOPE_2, category=Category.PURCHASED_ELECTRICITY,
            metadata={"activity_type": "grid_electricity"},
        ), registry.lookup("grid_electricity", 2024, country="UK")),
        (ActivityData(
            activity_id="E2", description="Warehouse - Grid electricity",
            quantity=Decimal("80000"), unit=Unit.KWH,
            scope=Scope.SCOPE_2, category=Category.PURCHASED_ELECTRICITY,
            metadata={"activity_type": "grid_electricity"},
        ), registry.lookup("grid_electricity", 2024, country="UK")),
    ]

    batch = calculator.calculate_batch(activities_and_factors)

    analyzer = CarbonAnalyzer()
    report = analyzer.analyze(batch)

    # Print report
    print("=" * 60)
    print("EcoAudit Carbon Intelligence Report")
    print("=" * 60)
    print(f"Total emissions: {report.total_emissions:.2f} {report.emissions_unit}")
    print(f"Activities analyzed: {report.result_count}")
    print()

    print("--- Scope Breakdown ---")
    for c in report.scope_breakdown.contributions:
        print(f"  {c.label}: {c.emissions:.2f} kgCO2e ({c.percentage:.1f}%)")
    print()

    print("--- Category Breakdowns ---")
    for bd in report.category_breakdowns:
        print(f"  {bd.scope.value} ({bd.scope_emissions:.2f} kgCO2e):")
        for c in bd.contributions:
            print(f"    {c.label}: {c.emissions:.2f} kgCO2e ({c.percentage:.1f}%)")
    print()

    print("--- Activity Contributions ---")
    for c in report.activity_contributions:
        print(f"  {c.label}: {c.emissions:.2f} kgCO2e ({c.percentage:.1f}%)")
    print()

    print("--- Hotspots ---")
    for h in report.hotspots:
        print(f"  [{h.severity.value.upper()}] {h.label}")
        print(f"    {h.emissions:.2f} kgCO2e = {h.percentage_of_total:.1f}% of total")
        if h.percentage_of_scope:
            print(f"    {h.percentage_of_scope:.1f}% within {h.parent_scope.value}")
        print(f"    Actionability: {h.actionability.value}")
        print(f"    Based on {h.contributing_activities} activity(s)")
    print()

    if report.pareto:
        print("--- Pareto Analysis ---")
        for top_n, cum_pct in report.pareto.concentration_points:
            print(f"  Top {top_n} {report.pareto.dimension}(s): {cum_pct:.1f}% of emissions")
    print()

    print("--- Data Quality ---")
    dq = report.data_quality
    print(f"  Total results: {dq.total_results}")
    print(f"  Using test factors: {dq.results_with_test_factors}")
    print(f"  Factor sources: {', '.join(dq.factor_sources)}")
    print()

    print("--- Insights ---")
    for insight in report.insights:
        print(f"  [{insight.severity.value.upper()}] {insight.title}")
        print(f"    {insight.evidence}")
        if insight.detail:
            print(f"    {insight.detail}")
    print()


if __name__ == "__main__":
    main()
