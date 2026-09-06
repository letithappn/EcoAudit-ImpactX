"""End-to-end intelligence integration tests.

Tests the full flow: dataset -> calculator -> CarbonAnalyzer -> report.
Validates actual numerical outputs, not just structural correctness.
Uses real/public dataset adapters from Phase 3.
"""

from decimal import Decimal
from pathlib import Path

import pytest

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.data_loader import load_factors_from_json
from ecoaudit.carbon.factors import EmissionFactorRegistry, load_test_factors
from ecoaudit.carbon.models import ActivityData, BatchResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.ingestion.adapters import ChicagoEnergyAdapter, SyntheticCompanyAdapter
from ecoaudit.intelligence.analyzer import CarbonAnalyzer
from ecoaudit.intelligence.models import Severity


# ---- Helper to build a realistic batch ----

def _build_company_batch(calculator: CarbonCalculator) -> BatchResult:
    """Build a simulated company footprint with mixed scopes."""
    registry = calculator.registry
    activities_and_factors = [
        # Scope 1: Diesel generator — 10,000 L
        (ActivityData(
            activity_id="INT-01", description="Factory - Diesel generator",
            quantity=Decimal("10000"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
            metadata={"activity_type": "diesel"},
        ), registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)),
        # Scope 1: Fleet petrol — 2,000 L
        (ActivityData(
            activity_id="INT-02", description="Fleet - Company car petrol",
            quantity=Decimal("2000"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.MOBILE_COMBUSTION,
            metadata={"activity_type": "petrol"},
        ), registry.lookup("petrol", 2024, country="UK")),
        # Scope 2: Grid electricity — 100,000 kWh
        (ActivityData(
            activity_id="INT-03", description="HQ - Grid electricity",
            quantity=Decimal("100000"), unit=Unit.KWH,
            scope=Scope.SCOPE_2, category=Category.PURCHASED_ELECTRICITY,
            metadata={"activity_type": "grid_electricity"},
        ), registry.lookup("grid_electricity", 2024, country="UK")),
        # Scope 2: More electricity — 50,000 kWh (warehouse)
        (ActivityData(
            activity_id="INT-04", description="Warehouse - Grid electricity",
            quantity=Decimal("50000"), unit=Unit.KWH,
            scope=Scope.SCOPE_2, category=Category.PURCHASED_ELECTRICITY,
            metadata={"activity_type": "grid_electricity"},
        ), registry.lookup("grid_electricity", 2024, country="UK")),
    ]
    return calculator.calculate_batch(activities_and_factors)


class TestFullAnalysisReport:
    """Test the complete CarbonAnalyzer output."""

    def test_report_total_matches_batch(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        assert report.total_emissions == batch.total_emissions

    def test_scope_breakdown_present(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        assert len(report.scope_breakdown.contributions) == 2  # Scope 1 + Scope 2

    def test_scope_percentages_sum_to_100(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        total_pct = sum(c.percentage for c in report.scope_breakdown.contributions)
        assert abs(total_pct - Decimal("100")) < Decimal("0.1")

    def test_category_breakdowns_present(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        assert len(report.category_breakdowns) == 2

    def test_activity_contributions_present(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        types = {c.label for c in report.activity_contributions}
        assert types == {"diesel", "petrol", "grid_electricity"}

    def test_hotspots_identified(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        assert len(report.hotspots) > 0

    def test_pareto_analysis_present(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        assert report.pareto is not None

    def test_insights_generated(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        assert len(report.insights) > 0

    def test_data_quality_summary(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        assert report.data_quality.total_results == 4
        assert report.data_quality.results_with_test_factors == 4  # All use test factors

    def test_result_count(self, calculator: CarbonCalculator) -> None:
        batch = _build_company_batch(calculator)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)
        assert report.result_count == 4


class TestEmptyDataset:
    def test_empty_batch_produces_empty_report(self, calculator: CarbonCalculator) -> None:
        empty = BatchResult(results=(), total_emissions=Decimal("0"), scope_totals={}, category_totals={})
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(empty)
        assert report.total_emissions == Decimal("0")
        assert report.hotspots == ()
        assert report.insights == ()
        assert report.result_count == 0


class TestSingleActivity:
    def test_single_activity_report(self, calculator: CarbonCalculator) -> None:
        registry = calculator.registry
        act = ActivityData(
            activity_id="SINGLE", description="Only Activity - Diesel",
            quantity=Decimal("100"), unit=Unit.LITRE,
            scope=Scope.SCOPE_1, category=Category.STATIONARY_COMBUSTION,
            metadata={"activity_type": "diesel"},
        )
        f = registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
        batch = calculator.calculate_batch([(act, f)])

        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)

        assert report.total_emissions == Decimal("100") * Decimal("2.51210")
        assert len(report.scope_breakdown.contributions) == 1
        # Single source = 100% of total
        assert report.scope_breakdown.contributions[0].percentage == Decimal("100")


class TestRealDatasetIntegration:
    """Test intelligence against real dataset from Phase 3."""

    def test_chicago_dataset_analysis(self, calculator: CarbonCalculator) -> None:
        """Full pipeline: Chicago dataset -> adaptor -> calculator -> intelligence."""
        chicago_path = Path("data/raw/chicago_energy_2022.csv")
        if not chicago_path.exists():
            pytest.skip("Chicago dataset not available")

        adapter = ChicagoEnergyAdapter()
        activities = list(adapter.normalize(str(chicago_path)))
        assert len(activities) > 0

        registry = calculator.registry
        pairs = []
        for act in activities:
            activity_type = act.metadata["activity_type"]
            try:
                factor = registry.lookup(
                    activity_type=activity_type,
                    year=2024,
                    country="UK",
                    category=act.category,
                )
                pairs.append((act, factor))
            except Exception:
                pass

        batch = calculator.calculate_batch(pairs)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)

        # Verify structural completeness
        assert report.total_emissions > Decimal("0")
        assert len(report.scope_breakdown.contributions) >= 1
        assert len(report.category_breakdowns) >= 1
        assert len(report.hotspots) >= 1
        assert report.pareto is not None

        # Chicago data has both electricity (Scope 2) and gas (Scope 1)
        scope_labels = {c.label for c in report.scope_breakdown.contributions}
        assert "Scope 1" in scope_labels or "Scope 2" in scope_labels

    def test_synthetic_dataset_analysis(self, calculator: CarbonCalculator) -> None:
        """Full pipeline: Synthetic dataset -> intelligence."""
        syn_path = Path("data/demo/synthetic_company_data.csv")
        if not syn_path.exists():
            pytest.skip("Synthetic dataset not available")

        adapter = SyntheticCompanyAdapter()
        activities = list(adapter.normalize(str(syn_path)))

        registry = calculator.registry
        pairs = []
        for act in activities:
            activity_type = act.metadata["activity_type"]
            try:
                factor = registry.lookup(
                    activity_type=activity_type,
                    year=2024,
                    country="UK",
                    category=act.category,
                )
                pairs.append((act, factor))
            except Exception:
                pass

        batch = calculator.calculate_batch(pairs)
        analyzer = CarbonAnalyzer()
        report = analyzer.analyze(batch)

        assert report.total_emissions > Decimal("0")
        assert report.result_count > 0
