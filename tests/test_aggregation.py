"""Tests for aggregation engine — scope, category, activity breakdown."""

from decimal import Decimal

import pytest

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import load_test_factors
from ecoaudit.carbon.models import ActivityData, BatchResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.intelligence.aggregation import (
    aggregate_by_activity_type,
    aggregate_by_category,
    aggregate_by_facility,
    aggregate_by_scope,
)


def _make_batch(calculator: CarbonCalculator) -> BatchResult:
    """Build a multi-scope batch for testing.

    Activities:
    - 10,000 L diesel (Scope 1, Stationary) = 25,121.00 kgCO2e
    - 50,000 kWh electricity (Scope 2, Purchased Elec) = 10,352.50 kgCO2e
    - 2,000 L petrol (Scope 1, Mobile) = 4,336.04 kgCO2e
    Total = 39,809.54 kgCO2e
    """
    registry = calculator.registry
    diesel_act = ActivityData(
        activity_id="A1", description="Factory - Diesel generator",
        quantity=Decimal("10000"), unit=Unit.LITRE,
        scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
        metadata={"activity_type": "diesel"},
    )
    elec_act = ActivityData(
        activity_id="A2", description="Office - Grid electricity",
        quantity=Decimal("50000"), unit=Unit.KWH,
        scope=Scope.SCOPE_2, category=Category.PURCHASED_ELECTRICITY,
        metadata={"activity_type": "grid_electricity"},
    )
    petrol_act = ActivityData(
        activity_id="A3", description="Fleet - Company car petrol",
        quantity=Decimal("2000"), unit=Unit.LITRE,
        scope=Scope.SCOPE_1, category=Category.MOBILE_COMBUSTION,
        metadata={"activity_type": "petrol"},
    )

    diesel_f = registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
    elec_f = registry.lookup("grid_electricity", 2024, country="UK")
    petrol_f = registry.lookup("petrol", 2024, country="UK")

    return calculator.calculate_batch([
        (diesel_act, diesel_f),
        (elec_act, elec_f),
        (petrol_act, petrol_f),
    ])


@pytest.fixture
def batch(calculator: CarbonCalculator) -> BatchResult:
    return _make_batch(calculator)


class TestScopeAggregation:
    def test_scope_breakdown_totals(self, batch: BatchResult) -> None:
        breakdown = aggregate_by_scope(batch)
        assert breakdown.total_emissions == batch.total_emissions
        # Sum of all contributions must equal total
        total_from_contributions = sum(c.emissions for c in breakdown.contributions)
        assert total_from_contributions == batch.total_emissions

    def test_scope_breakdown_percentages_sum_to_100(self, batch: BatchResult) -> None:
        breakdown = aggregate_by_scope(batch)
        total_pct = sum(c.percentage for c in breakdown.contributions)
        assert abs(total_pct - Decimal("100")) < Decimal("0.1")

    def test_scope_breakdown_ranking(self, batch: BatchResult) -> None:
        breakdown = aggregate_by_scope(batch)
        # Scope 1 has diesel + petrol = larger than Scope 2
        assert breakdown.contributions[0].label == "Scope 1"
        assert breakdown.contributions[0].rank == 1
        assert breakdown.contributions[1].label == "Scope 2"
        assert breakdown.contributions[1].rank == 2

    def test_scope_1_emissions_value(self, batch: BatchResult) -> None:
        breakdown = aggregate_by_scope(batch)
        scope1 = breakdown.contributions[0]
        # 10000 * 2.51210 + 2000 * 2.16802 = 25121.00 + 4336.04 = 29457.04
        expected = Decimal("10000") * Decimal("2.51210") + Decimal("2000") * Decimal("2.16802")
        assert scope1.emissions == expected

    def test_scope_2_emissions_value(self, batch: BatchResult) -> None:
        breakdown = aggregate_by_scope(batch)
        scope2 = breakdown.contributions[1]
        # 50000 * 0.20705 = 10352.50
        expected = Decimal("50000") * Decimal("0.20705")
        assert scope2.emissions == expected


class TestCategoryAggregation:
    def test_category_breakdowns_per_scope(self, batch: BatchResult) -> None:
        breakdowns = aggregate_by_category(batch)
        # Should have 2 scopes: Scope 1, Scope 2
        assert len(breakdowns) == 2

    def test_scope1_has_two_categories(self, batch: BatchResult) -> None:
        breakdowns = aggregate_by_category(batch)
        scope1_bd = [b for b in breakdowns if b.scope == Scope.SCOPE_1][0]
        assert len(scope1_bd.contributions) == 2  # Stationary + Mobile

    def test_scope1_ranking_diesel_first(self, batch: BatchResult) -> None:
        breakdowns = aggregate_by_category(batch)
        scope1_bd = [b for b in breakdowns if b.scope == Scope.SCOPE_1][0]
        # Diesel (25121) > Petrol (4336)
        assert scope1_bd.contributions[0].label == "Stationary Combustion"
        assert scope1_bd.contributions[1].label == "Mobile Combustion"

    def test_scope1_percentages_sum_to_100(self, batch: BatchResult) -> None:
        breakdowns = aggregate_by_category(batch)
        scope1_bd = [b for b in breakdowns if b.scope == Scope.SCOPE_1][0]
        total_pct = sum(c.percentage for c in scope1_bd.contributions)
        assert abs(total_pct - Decimal("100")) < Decimal("0.1")

    def test_filter_by_scope(self, batch: BatchResult) -> None:
        breakdowns = aggregate_by_category(batch, scope=Scope.SCOPE_2)
        assert len(breakdowns) == 1
        assert breakdowns[0].scope == Scope.SCOPE_2
        assert len(breakdowns[0].contributions) == 1


class TestActivityTypeAggregation:
    def test_three_activity_types(self, batch: BatchResult) -> None:
        contribs = aggregate_by_activity_type(batch)
        labels = {c.label for c in contribs}
        assert labels == {"diesel", "grid_electricity", "petrol"}

    def test_ranked_by_emissions(self, batch: BatchResult) -> None:
        contribs = aggregate_by_activity_type(batch)
        assert contribs[0].label == "diesel"
        assert contribs[1].label == "grid_electricity"
        assert contribs[2].label == "petrol"

    def test_drill_down_to_results(self, batch: BatchResult) -> None:
        contribs = aggregate_by_activity_type(batch)
        diesel = contribs[0]
        assert diesel.result_count == 1
        assert len(diesel.source_results) == 1
        assert diesel.source_results[0].activity.activity_id == "A1"


class TestFacilityAggregation:
    def test_three_facilities(self, batch: BatchResult) -> None:
        contribs = aggregate_by_facility(batch)
        labels = {c.label for c in contribs}
        assert labels == {"Factory", "Office", "Fleet"}


class TestEmptyBatch:
    def test_empty_scope_breakdown(self, calculator: CarbonCalculator) -> None:
        empty = BatchResult(results=(), total_emissions=Decimal("0"), scope_totals={}, category_totals={})
        breakdown = aggregate_by_scope(empty)
        assert breakdown.total_emissions == Decimal("0")
        assert breakdown.contributions == ()
