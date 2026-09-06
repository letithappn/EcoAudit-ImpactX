"""
Comparison and ranking of multiple scenario results.
"""

from __future__ import annotations

from ecoaudit.optimization.models import ScenarioComparison, ScenarioResult


def rank_scenarios(
    comparison: ScenarioComparison,
    by: str = "carbon_reduction",
) -> tuple[ScenarioResult, ...]:
    """Rank scenarios in a comparison by a specific metric.

    Args:
        comparison: The ScenarioComparison to rank.
        by: The metric to sort by. Supported:
            - "carbon_reduction": Sort by highest absolute carbon reduction.
            - "financial_savings": Sort by highest absolute financial savings.
              (Scenarios with unavailable financial data will be sorted to the bottom).

    Returns:
        A tuple of ScenarioResult sorted according to the criteria.
    """
    scenarios = list(comparison.scenarios)
    
    if by == "carbon_reduction":
        # Sort descending by absolute carbon reduction
        scenarios.sort(key=lambda s: s.carbon_impact.absolute_reduction, reverse=True)
    elif by == "financial_savings":
        # Sort descending by financial savings. None values go to the bottom.
        def _savings_key(s: ScenarioResult) -> float:
            if s.financial_impact.is_available and s.financial_impact.absolute_savings is not None:
                return float(s.financial_impact.absolute_savings)
            return float("-inf")
            
        scenarios.sort(key=_savings_key, reverse=True)
    else:
        raise ValueError(f"Unsupported ranking metric: {by}")
        
    return tuple(scenarios)
