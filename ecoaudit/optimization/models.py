"""
Data models for the Optimization & Scenario Engine.

All scenario models are deterministic and immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Protocol

from ecoaudit.carbon.models import ActivityData, CalculationResult


@dataclass(frozen=True)
class CarbonImpact:
    """The carbon emission impact of a scenario relative to a baseline.

    Attributes:
        baseline_emissions: Total emissions of the targeted activities before intervention.
        scenario_emissions: Total emissions of the targeted activities after intervention.
        absolute_reduction: Baseline minus scenario emissions (positive means reduction).
        percentage_reduction: (absolute_reduction / baseline_emissions) * 100.
        emissions_unit: Always "kgCO2e".
    """
    baseline_emissions: Decimal
    scenario_emissions: Decimal
    absolute_reduction: Decimal
    percentage_reduction: Decimal
    emissions_unit: str = "kgCO2e"


@dataclass(frozen=True)
class FinancialImpact:
    """The financial impact of a scenario relative to a baseline.

    Attributes:
        baseline_cost: Total cost of the targeted activities before intervention.
        scenario_cost: Total cost of the targeted activities after intervention.
        absolute_savings: Baseline cost minus scenario cost.
        percentage_savings: (absolute_savings / baseline_cost) * 100.
        is_available: True if all necessary cost data was present, False otherwise.
        missing_reason: Explanation if financial impact could not be calculated.
    """
    baseline_cost: Decimal | None
    scenario_cost: Decimal | None
    absolute_savings: Decimal | None
    percentage_savings: Decimal | None
    is_available: bool
    missing_reason: str = ""


class Intervention(Protocol):
    """Protocol for a deterministic intervention (modification) to ActivityData."""
    
    @property
    def intervention_type(self) -> str:
        """Name of the intervention type (e.g., 'PercentageReduction')."""
        ...
        
    def apply(self, activity: ActivityData) -> ActivityData:
        """Apply the intervention to a single ActivityData record.
        
        Must return a new ActivityData instance (ActivityData is frozen).
        """
        ...
        
    def get_assumptions(self) -> tuple[str, ...]:
        """Return explicit assumptions made by this intervention."""
        ...


@dataclass(frozen=True)
class ScenarioDefinition:
    """Explicit definition of a scenario to be evaluated.

    Attributes:
        name: Human-readable name.
        description: Detailed explanation of the scenario.
        target_activity_ids: The specific activity IDs this scenario modifies.
        intervention: The deterministic logic applied to the target activities.
        assumptions: High-level assumptions for the entire scenario.
    """
    name: str
    description: str
    target_activity_ids: frozenset[str]
    intervention: Intervention
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScenarioResult:
    """The complete result of evaluating a scenario.

    Attributes:
        definition: The ScenarioDefinition that was evaluated.
        baseline_results: The CalculationResults for the unmodified target activities.
        scenario_results: The CalculationResults for the modified target activities.
        carbon_impact: The calculated carbon reduction.
        financial_impact: The calculated financial savings (if available).
    """
    definition: ScenarioDefinition
    baseline_results: tuple[CalculationResult, ...]
    scenario_results: tuple[CalculationResult, ...]
    carbon_impact: CarbonImpact
    financial_impact: FinancialImpact


@dataclass(frozen=True)
class ScenarioComparison:
    """Comparison of multiple evaluated scenarios.

    Attributes:
        baseline_emissions: The total emissions of the baseline activities.
        scenarios: Tuple of ScenarioResult objects.
    """
    baseline_emissions: Decimal
    scenarios: tuple[ScenarioResult, ...]
