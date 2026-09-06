"""
Scenario evaluation engine.

Evaluates a ScenarioDefinition against a baseline BatchResult using
the existing CarbonCalculator.
"""

from __future__ import annotations

from decimal import Decimal

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.models import BatchResult, CalculationResult
from ecoaudit.optimization.models import (
    CarbonImpact,
    FinancialImpact,
    ScenarioDefinition,
    ScenarioResult,
)


_ZERO = Decimal("0")
_HUNDRED = Decimal("100")


def _calculate_financial_impact(
    baseline_results: tuple[CalculationResult, ...],
    scenario_results: tuple[CalculationResult, ...],
) -> FinancialImpact:
    """Calculate the financial impact of the intervention.
    
    Relies on 'total_cost' in activity metadata. If any target activity
    is missing cost data in either baseline or scenario, financial impact
    is marked as unavailable.
    """
    baseline_cost = _ZERO
    scenario_cost = _ZERO
    
    # Check baseline costs
    for r in baseline_results:
        meta = r.activity.metadata or {}
        if "total_cost" not in meta:
            return FinancialImpact(
                baseline_cost=None,
                scenario_cost=None,
                absolute_savings=None,
                percentage_savings=None,
                is_available=False,
                missing_reason=f"Baseline activity {r.activity.activity_id} lacks 'total_cost' metadata."
            )
        baseline_cost += Decimal(str(meta["total_cost"]))
        
    # Check scenario costs
    for r in scenario_results:
        meta = r.activity.metadata or {}
        if "total_cost" not in meta:
            return FinancialImpact(
                baseline_cost=None,
                scenario_cost=None,
                absolute_savings=None,
                percentage_savings=None,
                is_available=False,
                missing_reason=f"Scenario activity {r.activity.activity_id} lacks 'total_cost' metadata."
            )
        scenario_cost += Decimal(str(meta["total_cost"]))
        
    absolute_savings = baseline_cost - scenario_cost
    
    percentage_savings = _ZERO
    if baseline_cost > _ZERO:
        percentage_savings = (absolute_savings / baseline_cost) * _HUNDRED
        
    return FinancialImpact(
        baseline_cost=baseline_cost,
        scenario_cost=scenario_cost,
        absolute_savings=absolute_savings,
        percentage_savings=percentage_savings,
        is_available=True,
    )


class ScenarioEngine:
    """Evaluates scenarios deterministically using the CarbonCalculator."""

    def __init__(self, calculator: CarbonCalculator) -> None:
        """Initialize with an existing CarbonCalculator.
        
        This ensures scenario calculations use the exact same methodology
        and factor registry as the baseline calculations.
        """
        self.calculator = calculator

    def evaluate(self, definition: ScenarioDefinition, baseline_batch: BatchResult) -> ScenarioResult:
        """Evaluate a scenario definition against a baseline batch.
        
        Args:
            definition: The scenario to evaluate.
            baseline_batch: The pre-calculated baseline batch.
            
        Returns:
            ScenarioResult containing carbon and financial impacts.
        """
        target_ids = definition.target_activity_ids
        
        # 1. Identify baseline results that are targeted
        baseline_results = tuple(r for r in baseline_batch.results if r.activity.activity_id in target_ids)
        if not baseline_results:
            raise ValueError("None of the target activity IDs were found in the baseline batch.")
            
        # 2. Apply intervention to target activities
        scenario_activities = []
        for r in baseline_results:
            new_activity = definition.intervention.apply(r.activity)
            scenario_activities.append(new_activity)
            
        # 3. Recalculate scenario activities using the existing engine
        scenario_results = []
        for act in scenario_activities:
            # We must lookup the factor again in case it's a FuelSubstitution
            activity_type = (act.metadata or {}).get("activity_type", "unknown")
            # For simplicity, we use the year and country from the original factor if possible,
            # but ideally we just do a standard lookup.
            # We'll assume year 2024, UK for now, but really we should look at the original factor's year/country.
            # Let's find the corresponding baseline result to match its year/country.
            original_result = next(r for r in baseline_results if r.activity.activity_id == act.activity_id.replace("-SCENARIO", ""))
            
            # Lookup factor
            factor = self.calculator.registry.lookup(
                activity_type=activity_type,
                year=original_result.factor.year,
                country=original_result.factor.country,
                category=act.category,
            )
            
            # Calculate deterministically
            calc_result = self.calculator.calculate(act, factor)
            scenario_results.append(calc_result)
            
        scenario_results = tuple(scenario_results)
        
        # 4. Compute Carbon Impact
        baseline_emissions = sum((r.emissions_value for r in baseline_results), _ZERO)
        scenario_emissions = sum((r.emissions_value for r in scenario_results), _ZERO)
        
        absolute_reduction = baseline_emissions - scenario_emissions
        percentage_reduction = _ZERO
        if baseline_emissions > _ZERO:
            percentage_reduction = (absolute_reduction / baseline_emissions) * _HUNDRED
            
        carbon_impact = CarbonImpact(
            baseline_emissions=baseline_emissions,
            scenario_emissions=scenario_emissions,
            absolute_reduction=absolute_reduction,
            percentage_reduction=percentage_reduction,
        )
        
        # 5. Compute Financial Impact
        financial_impact = _calculate_financial_impact(baseline_results, scenario_results)
        
        return ScenarioResult(
            definition=definition,
            baseline_results=baseline_results,
            scenario_results=scenario_results,
            carbon_impact=carbon_impact,
            financial_impact=financial_impact,
        )
