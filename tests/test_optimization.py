"""Tests for the Optimization & Scenario Engine."""

from decimal import Decimal

import pytest

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.models import ActivityData, BatchResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.optimization.comparison import rank_scenarios
from ecoaudit.optimization.engine import ScenarioEngine
from ecoaudit.optimization.interventions import (
    AbsoluteReduction,
    FuelSubstitution,
    PercentageReduction,
)
from ecoaudit.optimization.models import (
    ScenarioComparison,
    ScenarioDefinition,
    ScenarioResult,
)


@pytest.fixture
def activity_with_cost() -> ActivityData:
    return ActivityData(
        activity_id="ACT-COST",
        description="Diesel with cost",
        quantity=Decimal("1000"),
        unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        metadata={"activity_type": "diesel", "total_cost": Decimal("1500.00")}
    )


@pytest.fixture
def baseline_batch(calculator: CarbonCalculator, activity_with_cost: ActivityData) -> BatchResult:
    registry = calculator.registry
    factor = registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
    return calculator.calculate_batch([(activity_with_cost, factor)])


class TestInterventions:
    def test_percentage_reduction_logic(self, activity_with_cost: ActivityData) -> None:
        intervention = PercentageReduction(Decimal("20"))
        mod_act = intervention.apply(activity_with_cost)
        
        # 1000 * 0.8 = 800
        assert mod_act.quantity == Decimal("800")
        assert mod_act.unit == Unit.LITRE
        # 1500 * 0.8 = 1200
        assert mod_act.metadata is not None
        assert mod_act.metadata["total_cost"] == Decimal("1200.00")
        
    def test_percentage_bounds(self) -> None:
        with pytest.raises(ValueError):
            PercentageReduction(Decimal("-1"))
        with pytest.raises(ValueError):
            PercentageReduction(Decimal("101"))

    def test_absolute_reduction_logic(self, activity_with_cost: ActivityData) -> None:
        intervention = AbsoluteReduction(Decimal("250"))
        mod_act = intervention.apply(activity_with_cost)
        
        # 1000 - 250 = 750
        assert mod_act.quantity == Decimal("750")
        # Cost should be scaled: 1500 * (750/1000) = 1125
        assert mod_act.metadata is not None
        assert mod_act.metadata["total_cost"] == Decimal("1125.00")
        
    def test_absolute_reduction_below_zero(self, activity_with_cost: ActivityData) -> None:
        intervention = AbsoluteReduction(Decimal("1500")) # More than exists
        mod_act = intervention.apply(activity_with_cost)
        
        assert mod_act.quantity == Decimal("0")
        assert mod_act.metadata is not None
        assert mod_act.metadata["total_cost"] == Decimal("0")

    def test_fuel_substitution(self, activity_with_cost: ActivityData) -> None:
        # Switch from diesel (L) to electricity (kWh), assume 10 kWh per L.
        # Assume new cost is 0.15 per kWh.
        intervention = FuelSubstitution(
            new_activity_type="grid_electricity",
            new_unit=Unit.KWH,
            new_scope=Scope.SCOPE_2,
            new_category=Category.PURCHASED_ELECTRICITY,
            conversion_multiplier=Decimal("10"),
            new_unit_price=Decimal("0.15")
        )
        mod_act = intervention.apply(activity_with_cost)
        
        # 1000 * 10 = 10000 kWh
        assert mod_act.quantity == Decimal("10000")
        assert mod_act.unit == Unit.KWH
        assert mod_act.scope == Scope.SCOPE_2
        assert mod_act.category == Category.PURCHASED_ELECTRICITY
        assert mod_act.metadata is not None
        assert mod_act.metadata["activity_type"] == "grid_electricity"
        # Cost: 10000 * 0.15 = 1500
        assert mod_act.metadata["total_cost"] == Decimal("1500.00")

    def test_fuel_substitution_no_cost(self, activity_with_cost: ActivityData) -> None:
        intervention = FuelSubstitution(
            new_activity_type="petrol",
            new_unit=Unit.LITRE,
            new_scope=Scope.SCOPE_1,
            new_category=Category.MOBILE_COMBUSTION,
        )
        mod_act = intervention.apply(activity_with_cost)
        # Cost should be stripped since we don't know the new price
        assert mod_act.metadata is not None
        assert "total_cost" not in mod_act.metadata


class TestScenarioEngine:
    def test_successful_percentage_reduction_scenario(
        self,
        calculator: CarbonCalculator,
        baseline_batch: BatchResult,
    ) -> None:
        engine = ScenarioEngine(calculator)
        
        # Scenario: Reduce diesel by 10%
        definition = ScenarioDefinition(
            name="10% Diesel Reduction",
            description="Reduce generator usage by 10%",
            target_activity_ids=frozenset(["ACT-COST"]),
            intervention=PercentageReduction(Decimal("10"))
        )
        
        result = engine.evaluate(definition, baseline_batch)
        
        # Baseline emissions: 1000 L * 2.51210 = 2512.10
        # Scenario emissions: 900 L * 2.51210 = 2260.89
        # Reduction: 251.21
        assert result.carbon_impact.baseline_emissions == Decimal("2512.10")
        assert result.carbon_impact.scenario_emissions == Decimal("2260.89")
        assert result.carbon_impact.absolute_reduction == Decimal("251.21")
        assert result.carbon_impact.percentage_reduction == Decimal("10")
        
        # Financial impact
        # Baseline cost: 1500
        # Scenario cost: 1350
        # Savings: 150
        assert result.financial_impact.is_available is True
        assert result.financial_impact.baseline_cost == Decimal("1500.00")
        assert result.financial_impact.scenario_cost == Decimal("1350.00")
        assert result.financial_impact.absolute_savings == Decimal("150.00")
        assert result.financial_impact.percentage_savings == Decimal("10")

    def test_missing_target_activity(
        self,
        calculator: CarbonCalculator,
        baseline_batch: BatchResult,
    ) -> None:
        engine = ScenarioEngine(calculator)
        definition = ScenarioDefinition(
            name="Invalid Target",
            description="Targets unknown activity",
            target_activity_ids=frozenset(["UNKNOWN-ACT"]),
            intervention=PercentageReduction(Decimal("10"))
        )
        
        with pytest.raises(ValueError, match="None of the target activity IDs were found"):
            engine.evaluate(definition, baseline_batch)

    def test_missing_financial_data(
        self,
        calculator: CarbonCalculator,
    ) -> None:
        # Create an activity without cost metadata
        act_no_cost = ActivityData(
            activity_id="ACT-NO-COST", description="Diesel no cost",
            quantity=Decimal("1000"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
            metadata={"activity_type": "diesel"}
        )
        factor = calculator.registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
        batch = calculator.calculate_batch([(act_no_cost, factor)])
        
        engine = ScenarioEngine(calculator)
        definition = ScenarioDefinition(
            name="Reduction without cost",
            description="Reduce",
            target_activity_ids=frozenset(["ACT-NO-COST"]),
            intervention=PercentageReduction(Decimal("50"))
        )
        
        result = engine.evaluate(definition, batch)
        
        # Carbon impact should still be calculated
        assert result.carbon_impact.percentage_reduction == Decimal("50")
        # Financial impact should be unavailable
        assert result.financial_impact.is_available is False
        assert result.financial_impact.absolute_savings is None
        assert "lacks 'total_cost'" in result.financial_impact.missing_reason


class TestScenarioComparison:
    def test_ranking_by_carbon_reduction(self, calculator: CarbonCalculator, baseline_batch: BatchResult) -> None:
        engine = ScenarioEngine(calculator)
        
        def1 = ScenarioDefinition("10%", "", frozenset(["ACT-COST"]), PercentageReduction(Decimal("10")))
        def2 = ScenarioDefinition("50%", "", frozenset(["ACT-COST"]), PercentageReduction(Decimal("50")))
        def3 = ScenarioDefinition("30%", "", frozenset(["ACT-COST"]), PercentageReduction(Decimal("30")))
        
        r1 = engine.evaluate(def1, baseline_batch)
        r2 = engine.evaluate(def2, baseline_batch)
        r3 = engine.evaluate(def3, baseline_batch)
        
        comparison = ScenarioComparison(baseline_emissions=baseline_batch.total_emissions, scenarios=(r1, r2, r3))
        
        ranked = rank_scenarios(comparison, by="carbon_reduction")
        assert ranked[0].definition.name == "50%"
        assert ranked[1].definition.name == "30%"
        assert ranked[2].definition.name == "10%"

    def test_ranking_by_financial_savings(self, calculator: CarbonCalculator, baseline_batch: BatchResult) -> None:
        engine = ScenarioEngine(calculator)
        
        def1 = ScenarioDefinition("10%", "", frozenset(["ACT-COST"]), PercentageReduction(Decimal("10")))
        def2 = ScenarioDefinition("50%", "", frozenset(["ACT-COST"]), PercentageReduction(Decimal("50")))
        
        r1 = engine.evaluate(def1, baseline_batch)
        r2 = engine.evaluate(def2, baseline_batch)
        
        comparison = ScenarioComparison(baseline_emissions=baseline_batch.total_emissions, scenarios=(r1, r2))
        
        ranked = rank_scenarios(comparison, by="financial_savings")
        assert ranked[0].definition.name == "50%"
        assert ranked[1].definition.name == "10%"
