"""Tests for time-based trend analysis."""

from decimal import Decimal

import pytest

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import load_test_factors
from ecoaudit.carbon.models import ActivityData, BatchResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.intelligence.trends import analyze_trend


def _make_multi_year_batch(calculator: CarbonCalculator) -> BatchResult:
    """Build a batch with activities across 2 years.

    2023: 5000 kWh electricity
    2024: 8000 kWh electricity
    """
    registry = calculator.registry
    act_2023 = ActivityData(
        activity_id="T1", description="Office Electricity 2023",
        quantity=Decimal("5000"), unit=Unit.KWH,
        scope=Scope.SCOPE_2, category=Category.PURCHASED_ELECTRICITY,
        metadata={"activity_type": "grid_electricity", "year": "2023"},
    )
    act_2024 = ActivityData(
        activity_id="T2", description="Office Electricity 2024",
        quantity=Decimal("8000"), unit=Unit.KWH,
        scope=Scope.SCOPE_2, category=Category.PURCHASED_ELECTRICITY,
        metadata={"activity_type": "grid_electricity", "year": "2024"},
    )
    f_2023 = registry.lookup("grid_electricity", 2023, country="Egypt")
    f_2024 = registry.lookup("grid_electricity", 2024, country="UK")

    return calculator.calculate_batch([
        (act_2023, f_2023),
        (act_2024, f_2024),
    ])


def _make_single_period_batch(calculator: CarbonCalculator) -> BatchResult:
    """Build a batch with activities in a single period."""
    registry = calculator.registry
    act = ActivityData(
        activity_id="S1", description="Diesel 2024",
        quantity=Decimal("100"), unit=Unit.LITRE,
        scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
        metadata={"activity_type": "diesel", "year": "2024"},
    )
    f = registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
    return calculator.calculate_batch([(act, f)])


@pytest.fixture
def multi_year_batch(calculator: CarbonCalculator) -> BatchResult:
    return _make_multi_year_batch(calculator)


@pytest.fixture
def single_period_batch(calculator: CarbonCalculator) -> BatchResult:
    return _make_single_period_batch(calculator)


class TestTrendAnalysis:
    def test_multi_year_has_two_points(self, multi_year_batch: BatchResult) -> None:
        trend = analyze_trend(multi_year_batch)
        assert trend.is_sufficient_data is True
        assert len(trend.points) == 2

    def test_multi_year_periods_correct(self, multi_year_batch: BatchResult) -> None:
        trend = analyze_trend(multi_year_batch)
        assert trend.earliest_period == "2023"
        assert trend.latest_period == "2024"

    def test_multi_year_change_calculated(self, multi_year_batch: BatchResult) -> None:
        trend = analyze_trend(multi_year_batch)
        assert trend.total_change is not None
        assert trend.percentage_change is not None
        # 2023: 5000 * 0.50000 = 2500.00
        # 2024: 8000 * 0.20705 = 1656.40
        # Change: 1656.40 - 2500.00 = -843.60 (decrease)
        expected_2023 = Decimal("5000") * Decimal("0.50000")
        expected_2024 = Decimal("8000") * Decimal("0.20705")
        expected_change = expected_2024 - expected_2023
        assert trend.total_change == expected_change

    def test_multi_year_percentage_is_negative(self, multi_year_batch: BatchResult) -> None:
        trend = analyze_trend(multi_year_batch)
        # Emissions decreased from 2500 to 1656.40
        assert trend.percentage_change is not None
        assert trend.percentage_change < Decimal("0")

    def test_single_period_insufficient(self, single_period_batch: BatchResult) -> None:
        trend = analyze_trend(single_period_batch)
        assert trend.is_sufficient_data is False
        assert "1 distinct period" in trend.insufficient_reason

    def test_single_period_still_has_points(self, single_period_batch: BatchResult) -> None:
        trend = analyze_trend(single_period_batch)
        assert len(trend.points) == 1
        assert trend.points[0].period == "2024"

    def test_empty_batch(self, calculator: CarbonCalculator) -> None:
        empty = BatchResult(results=(), total_emissions=Decimal("0"), scope_totals={}, category_totals={})
        trend = analyze_trend(empty)
        assert trend.is_sufficient_data is False
        assert trend.points == ()

    def test_date_extraction_from_description(self, calculator: CarbonCalculator) -> None:
        """Period extracted from description when metadata lacks date."""
        registry = calculator.registry
        act = ActivityData(
            activity_id="D1", description="Q1 2024 Diesel Usage",
            quantity=Decimal("100"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
            metadata={"activity_type": "diesel"},
        )
        f = registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
        batch = calculator.calculate_batch([(act, f)])
        trend = analyze_trend(batch)
        assert len(trend.points) == 1
        assert trend.points[0].period == "2024"
