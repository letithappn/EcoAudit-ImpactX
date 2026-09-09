"""Reusable orchestration for the EcoAudit end-to-end pipeline.

The CLI and the web API share this composition layer. Domain calculations
remain in their existing engines; this module only coordinates them and keeps
the complete run state available to presentation layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ecoaudit.ai.gemini_provider import GeminiClient, GeminiClassifier
from ecoaudit.ai.mock_provider import MockClassifier
from ecoaudit.ai.pipeline import ClassificationPipeline, ClassificationRecord, PipelineStats
from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.data_loader import load_factors_from_json
from ecoaudit.carbon.factors import EmissionFactorRegistry, FactorNotFoundError
from ecoaudit.carbon.models import ActivityData, BatchResult
from ecoaudit.carbon.validation import ValidationError
from ecoaudit.ingestion.normalizer import read_csv_rows
from ecoaudit.intelligence.analyzer import CarbonAnalyzer
from ecoaudit.intelligence.models import CarbonIntelligenceReport
from ecoaudit.recommendation.engine import RecommendationEngine
from ecoaudit.recommendation.models import Recommendation
from ecoaudit.optimization.engine import ScenarioEngine


PipelineProgress = Callable[[str], None]


@dataclass
class PipelineExecution:
    """All authoritative outputs needed by the API and presentation layers."""

    input_path: str
    provider: str
    year: int
    country: str
    raw_rows: list[dict[str, str]]
    classification_records: list[ClassificationRecord]
    classification_stats: PipelineStats
    validated_activities: list[ActivityData]
    batch_result: BatchResult
    intelligence: CarbonIntelligenceReport
    recommendations: list[Recommendation]
    scenario_engine: ScenarioEngine
    factor_count: int
    calculation_rejections: list[dict[str, str]] = field(default_factory=list)

    @property
    def statistics(self) -> dict[str, int | float]:
        supported_recommendations = sum(
            1 for rec in self.recommendations
            if rec.status.value in {"supported", "requires_review"}
        )
        rejected_recommendations = sum(
            1 for rec in self.recommendations
            if rec.status.value == "rejected"
        )
        total_rows = self.classification_stats.total_rows
        calculated_rows = {
            result.activity.source_row
            for result in self.batch_result.results
            if result.activity.source_row is not None
        }
        validated_rows = {
            record.source_row
            for record in self.classification_records
            if record.activity_data is not None
        }
        classified_rows = {
            record.source_row
            for record in self.classification_records
            if record.candidate is not None
            and record.candidate.activity_type.lower().strip() != "unknown"
        }
        review_rows = {
            record.source_row
            for record in self.classification_records
            if (
                record.candidate is not None
                and record.candidate.needs_review
            )
            or record.validation_result is not None
            and not record.validation_result.is_valid
        }
        unsupported_rows = {
            record.source_row
            for record in self.classification_records
            if record.candidate is not None
            and record.candidate.activity_type.lower().strip() == "unknown"
        }
        calculation_failure_rows = {
            int(item["source_row"])
            for item in self.calculation_rejections
            if item.get("source_row", "").isdigit()
        }
        coverage = (len(calculated_rows) / total_rows * 100) if total_rows else 0.0
        return {
            "total_rows": total_rows,
            "successfully_parsed": self.classification_stats.successfully_parsed,
            "activity_records": self.classification_stats.activity_records,
            "ai_classified": len(classified_rows),
            "validated": len(self.validated_activities),
            "validated_rows": len(validated_rows),
            "rejected_ai": self.classification_stats.rejected,
            "needs_review": len(review_rows),
            "unsupported": len(unsupported_rows),
            "calculated": len(self.batch_result.results),
            "calculated_rows": len(calculated_rows),
            "rejected_calculation": len(self.calculation_rejections),
            "calculation_failures": len(self.calculation_rejections),
            "calculation_failure_rows": len(calculation_failure_rows),
            "coverage_percentage": round(coverage, 2),
            "recommendations_generated": len(self.recommendations),
            "recommendations_supported": supported_recommendations,
            "recommendations_rejected": rejected_recommendations,
        }


def execute_pipeline(
    input_path: str | Path,
    provider: str = "mock",
    year: int = 2024,
    country: str = "UK",
    progress: PipelineProgress | None = None,
) -> PipelineExecution:
    """Execute all backend phases and retain their complete typed results."""
    path = Path(input_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    def report(stage: str) -> None:
        if progress:
            progress(stage)

    report("Uploading")
    registry = EmissionFactorRegistry()
    factors_dir = Path(__file__).resolve().parent.parent / "data" / "factors"
    load_factors_from_json(factors_dir / "defra_2024.json", registry, is_test_data=False)
    load_factors_from_json(factors_dir / "egypt_mena_proxy.json", registry, is_test_data=False)
    calculator = CarbonCalculator(registry)

    report("Parsing")
    raw_rows = read_csv_rows(path)

    if provider == "gemini":
        classifier = GeminiClassifier()
        recommendation_provider = GeminiClient()
    elif provider == "mock":
        classifier = MockClassifier()
        recommendation_provider = classifier
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    report("AI Classification")
    classification_pipeline = ClassificationPipeline(classifier)
    classification_records, classification_stats = classification_pipeline.process_rows(raw_rows)
    validated_activities = classification_pipeline.get_validated_activities(classification_records)

    report("Validation")
    calculable_pairs: list[tuple[ActivityData, object]] = []
    calculation_rejections: list[dict[str, str]] = []
    for activity in validated_activities:
        # Structurally valid but low-confidence classifications are retained
        # for review and evidence, but never enter authoritative totals.
        if (activity.metadata or {}).get("ai_needs_review"):
            continue
        activity_type = (activity.metadata or {}).get("activity_type", "")
        try:
            factor = registry.lookup(
                activity_type=activity_type,
                year=year,
                country=country,
                category=activity.category,
            )
        except FactorNotFoundError:
            try:
                factor = registry.lookup(
                    activity_type=activity_type,
                    year=year,
                    country=country,
                )
            except FactorNotFoundError as error:
                calculation_rejections.append({
                    "activity_id": activity.activity_id,
                    "source_row": str(activity.source_row or ""),
                    "reason": str(error),
                    "status": "rejected",
                })
                continue

        try:
            calculator.calculate(activity, factor)
            calculable_pairs.append((activity, factor))
        except ValidationError as error:
            calculation_rejections.append({
                "activity_id": activity.activity_id,
                "source_row": str(activity.source_row or ""),
                "reason": str(error),
                "status": "rejected",
            })

    report("Carbon Calculation")
    batch_result = calculator.calculate_batch(calculable_pairs)

    report("Carbon Intelligence")
    intelligence = CarbonAnalyzer().analyze(batch_result)

    report("Scenario Analysis")
    scenario_engine = ScenarioEngine(calculator)

    report("Recommendations")
    recommendations: list[Recommendation] = []
    if batch_result.results:
        recommendations = RecommendationEngine(
            recommendation_provider,
            scenario_engine,
        ).generate_recommendations(intelligence, batch_result)

    return PipelineExecution(
        input_path=str(path),
        provider=provider,
        year=year,
        country=country,
        raw_rows=raw_rows,
        classification_records=classification_records,
        classification_stats=classification_stats,
        validated_activities=validated_activities,
        batch_result=batch_result,
        intelligence=intelligence,
        recommendations=recommendations,
        scenario_engine=scenario_engine,
        factor_count=len(registry),
        calculation_rejections=calculation_rejections,
    )
