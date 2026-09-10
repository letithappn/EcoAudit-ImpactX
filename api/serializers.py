"""Convert internal immutable domain objects into stable public DTOs."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from ecoaudit.ai.pipeline import ClassificationRecord
from ecoaudit.carbon.models import CalculationResult, EmissionFactor
from ecoaudit.intelligence.models import (
    CarbonInsight,
    CarbonIntelligenceReport,
    DataQualitySummary,
    EmissionContribution,
    Hotspot,
)
from ecoaudit.optimization.models import ScenarioResult
from ecoaudit.recommendation.models import Recommendation

from api.schemas import (
    ActivityDTO,
    CalculationTraceDTO,
    ContributionDTO,
    DataQualityDTO,
    EvidenceDTO,
    FactorDTO,
    FinancialImpactDTO,
    HotspotDTO,
    ImpactDTO,
    InsightDTO,
    RecommendationDTO,
    ScenarioDTO,
)


def decimal(value: Decimal | int | float | None) -> str | None:
    return None if value is None else format(value, "f")


def factor_dto(factor: EmissionFactor) -> FactorDTO:
    return FactorDTO(
        factor_id=factor.factor_id,
        source=factor.source,
        dataset=factor.dataset_name,
        year=factor.year,
        version=factor.version,
        methodology=factor.methodology,
        applicability_notes=factor.applicability_notes,
        country=factor.country,
        factor_value=decimal(factor.value) or "0",
        factor_unit=factor.unit,
        is_proxy=("proxy" in factor.methodology.lower() or "approx" in factor.applicability_notes.lower()),
    )


def evidence_dto(
    result: CalculationResult,
    original_row: dict[str, str] | None = None,
) -> EvidenceDTO:
    trace = result.trace
    return EvidenceDTO(
        result_id=result.result_id,
        activity_id=result.activity.activity_id,
        activity_description=result.activity.description,
        original_row=original_row or {},
        emissions_value=decimal(result.emissions_value) or "0",
        emissions_unit=result.emissions_unit,
        factor=factor_dto(result.factor),
        trace=CalculationTraceDTO(
            input_quantity=decimal(trace.input_quantity) or "0",
            input_unit=trace.input_unit.value,
            normalized_quantity=decimal(trace.normalized_quantity) or "0",
            normalized_unit=trace.normalized_unit.value,
            conversion_factor_applied=decimal(trace.conversion_factor_applied) or "0",
            emission_factor_value=decimal(trace.emission_factor_value) or "0",
            emission_factor_unit=trace.emission_factor_unit,
            emission_factor_id=trace.emission_factor_id,
            emission_factor_source=trace.emission_factor_source,
            emission_factor_year=trace.emission_factor_year,
            formula_description=trace.formula_description,
            scope=trace.scope.value,
            category=trace.category.value,
        ),
        source_row=result.activity.source_row,
    )


def _candidate_activity(record: ClassificationRecord) -> ActivityDTO:
    candidate = record.candidate
    activity = record.activity_data
    validation = record.validation_result
    if activity is not None:
        metadata = activity.metadata or {}
        needs_review = bool(metadata.get("ai_needs_review", False))
        return ActivityDTO(
            source_row=record.source_row,
            original_row=record.raw_row,
            activity_id=activity.activity_id,
            activity_type=str(metadata.get("activity_type", candidate.activity_type if candidate else "")),
            description=activity.description,
            quantity=decimal(activity.quantity),
            unit=activity.unit.value,
            scope=activity.scope.value,
            category=activity.category.value,
            confidence=decimal(candidate.confidence if candidate else None),
            needs_review=needs_review,
            validation_status="review" if needs_review else "validated",
            validation_errors=[],
            validation_warnings=list(validation.warnings if validation else ()),
            reasoning=candidate.reasoning if candidate else None,
        )

    return ActivityDTO(
        source_row=record.source_row,
        original_row=record.raw_row,
        activity_id=None,
        activity_type=candidate.activity_type if candidate else None,
        description=candidate.description if candidate else None,
        quantity=candidate.quantity if candidate else None,
        unit=candidate.unit if candidate else None,
        scope=candidate.scope if candidate else None,
        category=candidate.category if candidate else None,
        confidence=decimal(candidate.confidence if candidate else None),
        needs_review=bool(candidate.needs_review) if candidate else False,
        validation_status="rejected",
        validation_errors=list(validation.errors if validation else ([record.error] if record.error else [])),
        validation_warnings=list(validation.warnings if validation else ()),
        reasoning=candidate.reasoning if candidate else (record.error if record else None),
    )


def activities_dto(records: list[ClassificationRecord]) -> list[ActivityDTO]:
    return [_candidate_activity(record) for record in records]


def contribution_dto(item: EmissionContribution) -> ContributionDTO:
    return ContributionDTO(
        label=item.label,
        emissions=decimal(item.emissions) or "0",
        percentage=decimal(item.percentage) or "0",
        rank=item.rank,
        result_count=item.result_count,
        result_ids=[result.result_id for result in item.source_results],
    )


def hotspot_dto(item: Hotspot) -> HotspotDTO:
    return HotspotDTO(
        label=item.label,
        dimension=item.dimension,
        emissions=decimal(item.emissions) or "0",
        percentage_of_total=decimal(item.percentage_of_total) or "0",
        percentage_of_scope=decimal(item.percentage_of_scope),
        severity=item.severity.value,
        rank=item.rank,
        actionability=item.actionability.value,
        contributing_activities=item.contributing_activities,
        result_ids=[result.result_id for result in item.source_results],
        parent_scope=item.parent_scope.value if item.parent_scope else None,
        parent_category=item.parent_category.value if item.parent_category else None,
    )


def quality_dto(item: DataQualitySummary) -> DataQualityDTO:
    return DataQualityDTO(
        total_results=item.total_results,
        results_with_ai_classification=item.results_with_ai_classification,
        results_needing_review=item.results_needing_review,
        average_ai_confidence=decimal(item.average_ai_confidence),
        min_ai_confidence=decimal(item.min_ai_confidence),
        results_with_test_factors=item.results_with_test_factors,
        factor_sources=list(item.factor_sources),
    )


def impact_dto(result: ScenarioResult) -> ImpactDTO:
    impact = result.carbon_impact
    return ImpactDTO(
        baseline_emissions=decimal(impact.baseline_emissions) or "0",
        scenario_emissions=decimal(impact.scenario_emissions) or "0",
        absolute_reduction=decimal(impact.absolute_reduction) or "0",
        percentage_reduction=decimal(impact.percentage_reduction) or "0",
        emissions_unit=impact.emissions_unit,
    )


def financial_dto(result: ScenarioResult) -> FinancialImpactDTO:
    impact = result.financial_impact
    return FinancialImpactDTO(
        baseline_cost=decimal(impact.baseline_cost),
        scenario_cost=decimal(impact.scenario_cost),
        absolute_savings=decimal(impact.absolute_savings),
        percentage_savings=decimal(impact.percentage_savings),
        is_available=impact.is_available,
        missing_reason=impact.missing_reason,
    )


def scenario_dto(result: ScenarioResult) -> ScenarioDTO:
    definition = result.definition
    return ScenarioDTO(
        name=definition.name,
        description=definition.description,
        intervention_type=definition.intervention.intervention_type,
        target_activity_ids=sorted(definition.target_activity_ids),
        assumptions=list(definition.assumptions),
        carbon_impact=impact_dto(result),
        financial_impact=financial_dto(result),
        baseline_result_ids=[item.result_id for item in result.baseline_results],
        scenario_evidence=[evidence_dto(item) for item in result.scenario_results],
    )


def recommendation_dto(item: Recommendation) -> RecommendationDTO:
    scenario = scenario_dto(item.scenario_result) if item.scenario_result else None
    return RecommendationDTO(
        title=item.title,
        rationale=item.rationale,
        target_hotspot=item.evidence.hotspot_label,
        target_activity_ids=sorted(item.evidence.target_activity_ids),
        status=item.status.value,
        explanation=item.explanation,
        validation_errors=list(item.validation_errors),
        scenario=scenario,
    )


def report_parts(report: CarbonIntelligenceReport) -> dict[str, Any]:
    category_contributions: dict[str, list[ContributionDTO]] = {}
    for breakdown in report.category_breakdowns:
        category_contributions[breakdown.scope.value] = [
            contribution_dto(item) for item in breakdown.contributions
        ]

    return {
        "scope_contributions": [contribution_dto(item) for item in report.scope_breakdown.contributions],
        "category_contributions": category_contributions,
        "activity_contributions": [contribution_dto(item) for item in report.activity_contributions],
        "hotspots": [hotspot_dto(item) for item in report.hotspots],
        "insights": [
            InsightDTO(
                insight_type=item.insight_type.value,
                severity=item.severity.value,
                title=item.title,
                evidence=item.evidence,
                detail=item.detail,
            )
            for item in report.insights
        ],
        "data_quality": quality_dto(report.data_quality),
    }
