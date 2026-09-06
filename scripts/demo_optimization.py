"""
Demonstration of the Optimization & Scenario Engine.

Usage:
    python scripts/demo_optimization.py
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
from ecoaudit.optimization.comparison import rank_scenarios
from ecoaudit.optimization.engine import ScenarioEngine
from ecoaudit.optimization.interventions import (
    FuelSubstitution,
    PercentageReduction,
)
from ecoaudit.optimization.models import ScenarioComparison, ScenarioDefinition


def main() -> None:
    registry = load_test_factors()
    calculator = CarbonCalculator(registry)

    # 1. Setup Baseline
    # A company uses 10,000 L of diesel in a generator (cost: $1.50/L)
    # Total cost = $15,000
    diesel_activity = ActivityData(
        activity_id="GEN-01",
        description="Factory Backup Generator",
        quantity=Decimal("10000"),
        unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        metadata={"activity_type": "diesel", "total_cost": Decimal("15000.00")}
    )
    factor = registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
    baseline_batch = calculator.calculate_batch([(diesel_activity, factor)])

    # 2. Setup Scenarios
    engine = ScenarioEngine(calculator)

    # Scenario A: Reduce generator usage by 20% through efficiency
    scen_a = ScenarioDefinition(
        name="Scenario A: 20% Efficiency Improvement",
        description="Reduce generator runtime through load balancing.",
        target_activity_ids=frozenset(["GEN-01"]),
        intervention=PercentageReduction(Decimal("20")),
    )

    # Scenario B: Switch entirely to grid electricity
    # Assume 1 L diesel = 10 kWh. So 100,000 kWh.
    # Assume grid electricity costs $0.15 / kWh.
    scen_b = ScenarioDefinition(
        name="Scenario B: Electrification",
        description="Replace diesel generator with grid electricity.",
        target_activity_ids=frozenset(["GEN-01"]),
        intervention=FuelSubstitution(
            new_activity_type="grid_electricity",
            new_unit=Unit.KWH,
            new_scope=Scope.SCOPE_2,
            new_category=Category.PURCHASED_ELECTRICITY,
            conversion_multiplier=Decimal("10"),
            new_unit_price=Decimal("0.15")
        ),
    )

    # 3. Evaluate Scenarios
    result_a = engine.evaluate(scen_a, baseline_batch)
    result_b = engine.evaluate(scen_b, baseline_batch)

    # 4. Compare Scenarios
    comparison = ScenarioComparison(
        baseline_emissions=baseline_batch.total_emissions,
        scenarios=(result_a, result_b)
    )

    # Print Report
    print("=" * 60)
    print("EcoAudit Optimization & Scenario Analysis")
    print("=" * 60)
    
    baseline_result = baseline_batch.results[0]
    baseline_cost = baseline_result.activity.metadata["total_cost"]
    
    print("BASELINE:")
    print(f"  Activity: {baseline_result.activity.description}")
    print(f"  Quantity: {baseline_result.activity.quantity} {baseline_result.activity.unit.value}")
    print(f"  Emissions: {baseline_result.emissions_value:.2f} {baseline_result.emissions_unit}")
    print(f"  Cost: ${baseline_cost:.2f}")
    print()

    # Rank by carbon reduction
    ranked = rank_scenarios(comparison, by="carbon_reduction")
    
    for i, res in enumerate(ranked, 1):
        print(f"--- Rank {i}: {res.definition.name} ---")
        print(f"  Description: {res.definition.description}")
        print("  Assumptions:")
        for a in res.definition.intervention.get_assumptions():
            print(f"    - {a}")
            
        print("\  Impact:")
        c_impact = res.carbon_impact
        print(f"    Carbon: {c_impact.baseline_emissions:.2f} -> {c_impact.scenario_emissions:.2f} kgCO2e")
        print(f"    Reduction: {c_impact.absolute_reduction:.2f} kgCO2e ({c_impact.percentage_reduction:.1f}%)")
        
        f_impact = res.financial_impact
        if f_impact.is_available:
            print(f"    Cost: ${f_impact.baseline_cost:.2f} -> ${f_impact.scenario_cost:.2f}")
            sign = "-" if f_impact.absolute_savings > 0 else "+"
            print(f"    Savings: {sign}${abs(f_impact.absolute_savings):.2f} ({f_impact.percentage_savings:.1f}%)")
        else:
            print("    Cost: Unavailable")
            
        print("\n  Trace (First Target Activity):")
        trace = res.scenario_results[0].trace
        print(f"    New Quantity: {trace.input_quantity} {trace.input_unit.value}")
        print(f"    New Factor: {trace.emission_factor_value} {trace.emission_factor_unit} ({trace.emission_factor_source})")
        print(f"    Formula: {trace.formula_description}")
        print()


if __name__ == "__main__":
    main()
