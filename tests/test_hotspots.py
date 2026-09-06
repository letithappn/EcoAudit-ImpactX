"""Tests for hotspot identification and Pareto analysis."""

from decimal import Decimal

import pytest

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import load_test_factors
from ecoaudit.carbon.models import ActivityData, BatchResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.intelligence.hotspots import (
    DEFAULT_HOTSPOT_THRESHOLD,
    drill_down,
    identify_hotspots,
    pareto_analysis,
)
from ecoaudit.intelligence.models import Actionability, Severity


def _make_batch(calculator: CarbonCalculator) -> BatchResult:
    """Build a multi-scope batch: diesel (63%), electricity (26%), petrol (11%)."""
    registry = calculator.registry
    acts_and_factors = [
        (ActivityData(
            activity_id="A1", description="Factory - Diesel generator",
            quantity=Decimal("10000"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
            metadata={"activity_type": "diesel"},
        ), registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)),
        (ActivityData(
            activity_id="A2", description="Office - Grid electricity",
            quantity=Decimal("50000"), unit=Unit.KWH,
            scope=Scope.SCOPE_2, category=Category.PURCHASED_ELECTRICITY,
            metadata={"activity_type": "grid_electricity"},
        ), registry.lookup("grid_electricity", 2024, country="UK")),
        (ActivityData(
            activity_id="A3", description="Fleet - Company car petrol",
            quantity=Decimal("2000"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.MOBILE_COMBUSTION,
            metadata={"activity_type": "petrol"},
        ), registry.lookup("petrol", 2024, country="UK")),
    ]
    return calculator.calculate_batch(acts_and_factors)


@pytest.fixture
def batch(calculator: CarbonCalculator) -> BatchResult:
    return _make_batch(calculator)


class TestHotspotIdentification:
    def test_default_threshold_finds_hotspots(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="category")
        # All 3 categories are > 5% of total
        assert len(hotspots) == 3

    def test_high_threshold_fewer_hotspots(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="category", threshold=Decimal("20"))
        # Only Stationary Combustion (63%) and Purchased Electricity (26%) are > 20%
        assert len(hotspots) == 2
        labels = {h.label for h in hotspots}
        assert "Stationary Combustion" in labels
        assert "Purchased Electricity" in labels

    def test_hotspot_ranking(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="category")
        assert hotspots[0].rank == 1
        assert hotspots[0].label == "Stationary Combustion"

    def test_hotspot_severity_classification(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="category")
        # Stationary = ~63% → CRITICAL
        assert hotspots[0].severity == Severity.CRITICAL
        # Electricity = ~26% → CRITICAL
        assert hotspots[1].severity == Severity.CRITICAL
        # Mobile = ~11% → HIGH
        assert hotspots[2].severity == Severity.HIGH

    def test_hotspot_actionability(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="category")
        # All are Scope 1 or 2 → ACTIONABLE
        for h in hotspots:
            assert h.actionability == Actionability.ACTIONABLE

    def test_hotspot_percentage_of_scope(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="category")
        stationary = hotspots[0]
        assert stationary.percentage_of_scope is not None
        # Stationary is within Scope 1, which also contains Mobile
        # Stationary should be ~85% of Scope 1
        assert stationary.percentage_of_scope > Decimal("80")

    def test_hotspot_by_scope_dimension(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="scope")
        assert len(hotspots) >= 2
        assert hotspots[0].label == "Scope 1"

    def test_empty_batch_no_hotspots(self, calculator: CarbonCalculator) -> None:
        empty = BatchResult(results=(), total_emissions=Decimal("0"), scope_totals={}, category_totals={})
        hotspots = identify_hotspots(empty, dimension="category")
        assert hotspots == ()


class TestParetoAnalysis:
    def test_pareto_result_structure(self, batch: BatchResult) -> None:
        result = pareto_analysis(batch, dimension="category")
        assert result is not None
        assert result.total_sources == 3
        assert result.total_emissions == batch.total_emissions
        assert len(result.concentration_points) == 3

    def test_pareto_cumulative_reaches_100(self, batch: BatchResult) -> None:
        result = pareto_analysis(batch, dimension="category")
        assert result is not None
        last_n, last_pct = result.concentration_points[-1]
        assert last_n == 3
        assert abs(last_pct - Decimal("100")) < Decimal("0.1")

    def test_pareto_monotonically_increasing(self, batch: BatchResult) -> None:
        result = pareto_analysis(batch, dimension="category")
        assert result is not None
        prev_pct = Decimal("0")
        for _, pct in result.concentration_points:
            assert pct >= prev_pct
            prev_pct = pct

    def test_pareto_empty_batch(self, calculator: CarbonCalculator) -> None:
        empty = BatchResult(results=(), total_emissions=Decimal("0"), scope_totals={}, category_totals={})
        result = pareto_analysis(empty, dimension="category")
        assert result is None


class TestDrillDown:
    def test_drill_down_activity_type(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="scope")
        scope1_hotspot = [h for h in hotspots if h.label == "Scope 1"][0]
        sub = drill_down(scope1_hotspot, batch, sub_dimension="activity_type")
        assert len(sub) == 2  # diesel + petrol
        labels = {c.label for c in sub}
        assert labels == {"diesel", "petrol"}

    def test_drill_down_preserves_total(self, batch: BatchResult) -> None:
        hotspots = identify_hotspots(batch, dimension="scope")
        scope1_hotspot = [h for h in hotspots if h.label == "Scope 1"][0]
        sub = drill_down(scope1_hotspot, batch, sub_dimension="activity_type")
        sub_total = sum(c.emissions for c in sub)
        assert sub_total == scope1_hotspot.emissions
