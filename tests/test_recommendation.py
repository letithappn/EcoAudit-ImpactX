"""
Tests for the AI Recommendation Engine.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from ecoaudit.ai.providers import AIClient
from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.models import ActivityData, BatchResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.intelligence.analyzer import CarbonAnalyzer
from ecoaudit.intelligence.models import CarbonIntelligenceReport
from ecoaudit.optimization.engine import ScenarioEngine
from ecoaudit.recommendation.engine import RecommendationEngine
from ecoaudit.recommendation.models import RecommendationStatus


class DummyAIClient(AIClient):
    """A configurable dummy AI client for testing specific scenarios."""
    def __init__(self, structured_response: Any):
        self._response = structured_response
        self.text_calls = 0
        
    def generate_structured(self, prompt: str) -> dict[str, Any] | list[dict[str, Any]]:
        if isinstance(self._response, Exception):
            raise self._response
        return self._response
        
    def generate_text(self, prompt: str) -> str:
        self.text_calls += 1
        return "AI Explanation."


@pytest.fixture
def test_batch(calculator: CarbonCalculator) -> BatchResult:
    act = ActivityData(
        activity_id="ACT-1",
        description="Diesel generator",
        quantity=Decimal("100"),
        unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        metadata={"activity_type": "diesel"}
    )
    factor = calculator.registry.lookup("diesel", 2024, country="UK", category=Category.STATIONARY_COMBUSTION)
    return calculator.calculate_batch([(act, factor)])


@pytest.fixture
def test_report(test_batch: BatchResult) -> CarbonIntelligenceReport:
    analyzer = CarbonAnalyzer()
    return analyzer.analyze(test_batch)


class TestRecommendationEngine:
    def test_successful_recommendation(
        self,
        calculator: CarbonCalculator,
        test_batch: BatchResult,
        test_report: CarbonIntelligenceReport
    ) -> None:
        # Mock LLM returns a valid PercentageReduction
        llm_response = {
            "recommendations": [
                {
                    "title": "Reduce Diesel 10%",
                    "target_hotspot": "Stationary Combustion",
                    "intervention_type": "PercentageReduction",
                    "target_activity_ids": ["ACT-1"],
                    "parameters": {"reduction_percentage": "10"},
                    "rationale": "Saves 10%",
                    "needs_review": False
                }
            ]
        }
        ai = DummyAIClient(llm_response)
        scenario_engine = ScenarioEngine(calculator)
        engine = RecommendationEngine(ai, scenario_engine)
        
        recs = engine.generate_recommendations(test_report, test_batch)
        
        assert len(recs) == 1
        rec = recs[0]
        assert rec.status == RecommendationStatus.SUPPORTED
        assert rec.scenario_result is not None
        assert rec.scenario_result.carbon_impact.percentage_reduction == Decimal("10")
        assert rec.explanation == "AI Explanation."
        assert ai.text_calls == 1

    def test_candidate_invalid_intervention_parameters(
        self,
        calculator: CarbonCalculator,
        test_batch: BatchResult,
        test_report: CarbonIntelligenceReport
    ) -> None:
        # Missing required parameter "reduction_percentage"
        llm_response = {
            "recommendations": [
                {
                    "title": "Bad Params",
                    "target_hotspot": "Stationary Combustion",
                    "intervention_type": "PercentageReduction",
                    "target_activity_ids": ["ACT-1"],
                    "parameters": {},
                    "rationale": "",
                }
            ]
        }
        ai = DummyAIClient(llm_response)
        scenario_engine = ScenarioEngine(calculator)
        engine = RecommendationEngine(ai, scenario_engine)
        
        recs = engine.generate_recommendations(test_report, test_batch)
        
        assert len(recs) == 1
        rec = recs[0]
        assert rec.status == RecommendationStatus.REJECTED
        assert rec.scenario_result is None
        assert len(rec.validation_errors) == 1
        assert "requires 'reduction_percentage'" in rec.validation_errors[0]
        assert ai.text_calls == 0

    def test_candidate_targets_missing_activity(
        self,
        calculator: CarbonCalculator,
        test_batch: BatchResult,
        test_report: CarbonIntelligenceReport
    ) -> None:
        # Targets an activity not in the batch
        llm_response = {
            "recommendations": [
                {
                    "title": "Missing Act",
                    "target_hotspot": "Stationary Combustion",
                    "intervention_type": "PercentageReduction",
                    "target_activity_ids": ["NON-EXISTENT"],
                    "parameters": {"reduction_percentage": "10"},
                    "rationale": "",
                }
            ]
        }
        ai = DummyAIClient(llm_response)
        scenario_engine = ScenarioEngine(calculator)
        engine = RecommendationEngine(ai, scenario_engine)
        
        recs = engine.generate_recommendations(test_report, test_batch)
        
        assert len(recs) == 1
        rec = recs[0]
        assert rec.status == RecommendationStatus.REJECTED
        assert "None of the target activity IDs were found" in rec.validation_errors[0]
        
    def test_candidate_invalid_schema(
        self,
        calculator: CarbonCalculator,
        test_batch: BatchResult,
        test_report: CarbonIntelligenceReport
    ) -> None:
        # Missing root 'recommendations' list
        ai = DummyAIClient({"foo": "bar"})
        scenario_engine = ScenarioEngine(calculator)
        engine = RecommendationEngine(ai, scenario_engine)
        
        recs = engine.generate_recommendations(test_report, test_batch)
        assert len(recs) == 0  # Fails at parsing stage entirely
        
    def test_candidate_needs_review(
        self,
        calculator: CarbonCalculator,
        test_batch: BatchResult,
        test_report: CarbonIntelligenceReport
    ) -> None:
        llm_response = {
            "recommendations": [
                {
                    "title": "Review me",
                    "target_hotspot": "Stationary Combustion",
                    "intervention_type": "PercentageReduction",
                    "target_activity_ids": ["ACT-1"],
                    "parameters": {"reduction_percentage": "10"},
                    "rationale": "",
                    "needs_review": True
                }
            ]
        }
        ai = DummyAIClient(llm_response)
        scenario_engine = ScenarioEngine(calculator)
        engine = RecommendationEngine(ai, scenario_engine)
        
        recs = engine.generate_recommendations(test_report, test_batch)
        assert recs[0].status == RecommendationStatus.REQUIRES_REVIEW
