"""
Demonstration of the AI Recommendation Engine.

Usage:
    python scripts/demo_recommendation.py
"""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ecoaudit.ai.mock_provider import MockClassifier
from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import load_test_factors
from ecoaudit.carbon.models import ActivityData
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.intelligence.analyzer import CarbonAnalyzer
from ecoaudit.optimization.engine import ScenarioEngine
from ecoaudit.recommendation.engine import RecommendationEngine


def main() -> None:
    # 1. Setup Data & Base Engine
    registry = load_test_factors()
    calculator = CarbonCalculator(registry)

    # A company uses 10,000 L of diesel
    diesel_activity = ActivityData(
        activity_id="ACT-TEST",
        description="Factory Backup Generator",
        quantity=Decimal("10000"),
        unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        metadata={"activity_type": "diesel", "total_cost": Decimal("15000.00")}
    )
    factor = registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
    batch = calculator.calculate_batch([(diesel_activity, factor)])

    # 2. Phase 5: Carbon Intelligence
    analyzer = CarbonAnalyzer()
    report = analyzer.analyze(batch)

    # 3. Phase 7: AI Recommendation
    # We use MockClassifier which implements the AIClient interface and
    # returns a dummy JSON payload matching our scenario.
    # In a real environment, you would use:
    # from ecoaudit.ai.gemini_provider import GeminiClient
    # ai_client = GeminiClient()
    ai_client = MockClassifier()
    
    scenario_engine = ScenarioEngine(calculator)
    rec_engine = RecommendationEngine(ai_client, scenario_engine)
    
    # Generate and evaluate recommendations
    recommendations = rec_engine.generate_recommendations(report, batch)

    # Print Report
    print("=" * 60)
    print("EcoAudit AI Recommendation Engine")
    print("=" * 60)
    print("BASELINE REPORT:")
    print(f"  Total emissions: {report.total_emissions:.2f} kgCO2e")
    print(f"  Top Hotspot: {report.hotspots[0].label} ({report.hotspots[0].percentage_of_total:.1f}%)\n")
    
    print("GENERATED RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"--- Recommendation {i}: {rec.title} ---")
        print(f"  Status: {rec.status.value.upper()}")
        print(f"  Rationale: {rec.rationale}")
        print("  AI Explanation:")
        print(f"    {rec.explanation}")
        
        if rec.scenario_result:
            c_impact = rec.scenario_result.carbon_impact
            f_impact = rec.scenario_result.financial_impact
            print("  Deterministic Verification:")
            print(f"    Carbon Reduction: {c_impact.absolute_reduction:.2f} kgCO2e ({c_impact.percentage_reduction:.1f}%)")
            if f_impact.is_available:
                print(f"    Cost Savings: ${f_impact.absolute_savings:.2f} ({f_impact.percentage_savings:.1f}%)")
            else:
                print("    Cost Savings: Unavailable")
            print("    Assumptions:")
            for a in rec.scenario_result.definition.assumptions:
                print(f"      - {a}")
        else:
            print("  Verification Failed:")
            for e in rec.validation_errors:
                print(f"    - {e}")
        print()


if __name__ == "__main__":
    main()
