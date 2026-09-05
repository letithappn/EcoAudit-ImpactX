"""Tests for the AI classification pipeline.

Tests the full flow: raw row → AI classification → validation → ActivityData,
and verifies that validated ActivityData can be fed into the deterministic engine.
"""

from decimal import Decimal
from pathlib import Path

import pytest

from ecoaudit.ai.mock_provider import MockClassifier
from ecoaudit.ai.pipeline import ClassificationPipeline, ClassificationRecord
from ecoaudit.ai.schemas import ActivityCandidate
from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import EmissionFactorRegistry, load_test_factors
from ecoaudit.carbon.models import ActivityData
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


@pytest.fixture
def pipeline() -> ClassificationPipeline:
    return ClassificationPipeline(MockClassifier())


@pytest.fixture
def calculator() -> CarbonCalculator:
    return CarbonCalculator(load_test_factors())


class TestPipelineClassification:
    """Test the classify_and_validate method."""

    def test_electricity_row(self, pipeline: ClassificationPipeline) -> None:
        row = {"Facility": "HQ", "Utility": "Electricity", "Usage Amount": "50000", "UOM": "kWh"}
        record = pipeline.classify_and_validate(row, source_row=2)
        assert record.error is None
        assert record.candidate is not None
        assert record.candidate.activity_type == "grid_electricity"
        assert record.validation_result is not None
        assert record.validation_result.is_valid is True
        assert record.activity_data is not None
        assert record.activity_data.scope == Scope.SCOPE_2

    def test_diesel_generator_row(self, pipeline: ClassificationPipeline) -> None:
        row = {"Facility": "Factory", "Utility": "Diesel Generator", "Usage Amount": "500", "UOM": "Liters"}
        record = pipeline.classify_and_validate(row, source_row=3)
        assert record.activity_data is not None
        assert record.activity_data.scope == Scope.SCOPE_1
        assert record.activity_data.category == Category.STATIONARY_COMBUSTION

    def test_fleet_vehicle_row(self, pipeline: ClassificationPipeline) -> None:
        row = {"Facility": "Delivery Truck", "Utility": "Diesel", "Usage Amount": "120", "UOM": "Liters"}
        record = pipeline.classify_and_validate(row, source_row=4)
        assert record.activity_data is not None
        assert record.activity_data.category == Category.MOBILE_COMBUSTION

    def test_water_row_classified_unknown(self, pipeline: ClassificationPipeline) -> None:
        row = {"Facility": "HQ", "Utility": "Water", "Usage Amount": "100", "UOM": "m3"}
        record = pipeline.classify_and_validate(row, source_row=5)
        assert record.candidate is not None
        assert record.candidate.activity_type == "unknown"
        # Unknown activity → rejected by validation
        assert record.validation_result is not None
        assert record.validation_result.is_valid is False

    def test_ambiguous_gas_flagged_for_review(self, pipeline: ClassificationPipeline) -> None:
        row = {"Facility": "HQ", "Utility": "Gas", "Usage Amount": "250", "UOM": "m3"}
        record = pipeline.classify_and_validate(row, source_row=6)
        assert record.candidate is not None
        assert record.candidate.needs_review is True


class TestPipelineCSV:
    """Test processing a full CSV file."""

    def test_process_synthetic_csv(
        self, pipeline: ClassificationPipeline, tmp_path: Path,
    ) -> None:
        csv = tmp_path / "test.csv"
        csv.write_text(
            "Facility,Utility,Usage Amount,UOM\n"
            "HQ,Electricity,50000,kWh\n"
            "Factory,Diesel Generator,500,Liters\n"
            "HQ,Water,100,m3\n"
        )
        records, stats = pipeline.process_csv(str(csv))
        assert stats.total_rows == 3
        assert stats.validated >= 2  # Electricity and Diesel should pass
        assert stats.rejected >= 1  # Water should be rejected

    def test_get_validated_activities(
        self, pipeline: ClassificationPipeline, tmp_path: Path,
    ) -> None:
        csv = tmp_path / "test.csv"
        csv.write_text(
            "Facility,Utility,Usage Amount,UOM\n"
            "HQ,Electricity,50000,kWh\n"
            "HQ,Water,100,m3\n"
        )
        records, _ = pipeline.process_csv(str(csv))
        activities = pipeline.get_validated_activities(records)
        assert len(activities) == 1
        assert activities[0].scope == Scope.SCOPE_2


class TestEndToEndWithDeterministicEngine:
    """Test that AI-validated ActivityData feeds correctly into
    the existing deterministic carbon calculator.

    This is the CRITICAL integration test: proving that the AI layer
    outputs data that the unchanged deterministic engine can process.
    """

    def test_ai_electricity_through_calculator(
        self, pipeline: ClassificationPipeline, calculator: CarbonCalculator,
    ) -> None:
        row = {"Facility": "Office", "Utility": "Electricity", "Usage Amount": "10000", "UOM": "kWh"}
        record = pipeline.classify_and_validate(row, source_row=2)
        assert record.activity_data is not None

        activity = record.activity_data
        # Look up factor from the test registry
        factor = calculator.registry.lookup(
            activity_type=activity.metadata["activity_type"],
            year=2024,
            country="UK",
            category=activity.category,
        )

        # Calculate using the UNCHANGED deterministic engine
        result = calculator.calculate(activity, factor)

        assert result.emissions_value > Decimal("0")
        assert result.emissions_unit == "kgCO2e"
        assert result.trace is not None
        assert result.trace.emission_factor_source == "UK DESNZ/DEFRA"

    def test_ai_diesel_generator_through_calculator(
        self, pipeline: ClassificationPipeline, calculator: CarbonCalculator,
    ) -> None:
        row = {"Facility": "Site", "Utility": "Diesel Generator", "Usage Amount": "1000", "UOM": "Liters"}
        record = pipeline.classify_and_validate(row, source_row=3)
        assert record.activity_data is not None

        activity = record.activity_data
        factor = calculator.registry.lookup(
            activity_type=activity.metadata["activity_type"],
            year=2024,
            country="UK",
            category=activity.category,
        )

        result = calculator.calculate(activity, factor)

        # 1000 litres × 2.51210 kgCO2e/litre = 2512.10 kgCO2e
        assert result.emissions_value == Decimal("1000") * Decimal("2.51210")

    def test_ai_petrol_through_calculator(
        self, pipeline: ClassificationPipeline, calculator: CarbonCalculator,
    ) -> None:
        row = {"Facility": "Company Car", "Utility": "Petrol", "Usage Amount": "50", "UOM": "Liters"}
        record = pipeline.classify_and_validate(row, source_row=4)
        assert record.activity_data is not None

        activity = record.activity_data
        factor = calculator.registry.lookup(
            activity_type=activity.metadata["activity_type"],
            year=2024,
            country="UK",
            category=activity.category,
        )

        result = calculator.calculate(activity, factor)
        assert result.emissions_value > Decimal("0")
        assert result.trace.scope == Scope.SCOPE_1
