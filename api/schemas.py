"""Public API DTOs for the EcoAudit web product."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DTO(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RunCreateResponse(DTO):
    run_id: str
    status: str
    stage: str


class RunStatusResponse(DTO):
    run_id: str
    status: str
    stage: str
    progress: int = Field(ge=0, le=100)
    provider: str
    year: int
    country: str
    filename: str
    statistics: dict[str, int | float]
    error: str | None = None


class FactorDTO(DTO):
    factor_id: str
    source: str
    dataset: str
    year: int
    version: str
    methodology: str
    applicability_notes: str
    country: str
    factor_value: str
    factor_unit: str
    is_proxy: bool


class ActivityDTO(DTO):
    source_row: int | None
    original_row: dict[str, str]
    activity_id: str | None
    activity_type: str | None
    description: str | None
    quantity: str | None
    unit: str | None
    scope: str | None
    category: str | None
    confidence: str | None
    needs_review: bool
    validation_status: Literal["validated", "review", "rejected"]
    validation_errors: list[str]
    validation_warnings: list[str]


class CalculationTraceDTO(DTO):
    input_quantity: str
    input_unit: str
    normalized_quantity: str
    normalized_unit: str
    conversion_factor_applied: str
    emission_factor_value: str
    emission_factor_unit: str
    emission_factor_id: str
    emission_factor_source: str
    emission_factor_year: int
    formula_description: str
    scope: str
    category: str


class EvidenceDTO(DTO):
    result_id: str
    activity_id: str
    activity_description: str
    original_row: dict[str, str]
    emissions_value: str
    emissions_unit: str
    factor: FactorDTO
    trace: CalculationTraceDTO
    source_row: int | None


class ContributionDTO(DTO):
    label: str
    emissions: str
    percentage: str
    rank: int
    result_count: int
    result_ids: list[str]


class HotspotDTO(DTO):
    label: str
    dimension: str
    emissions: str
    percentage_of_total: str
    percentage_of_scope: str | None
    severity: str
    rank: int
    actionability: str
    contributing_activities: int
    result_ids: list[str]
    parent_scope: str | None
    parent_category: str | None


class InsightDTO(DTO):
    insight_type: str
    severity: str
    title: str
    evidence: str
    detail: str


class DataQualityDTO(DTO):
    total_results: int
    results_with_ai_classification: int
    results_needing_review: int
    average_ai_confidence: str | None
    min_ai_confidence: str | None
    results_with_test_factors: int
    factor_sources: list[str]


class ImpactDTO(DTO):
    baseline_emissions: str
    scenario_emissions: str
    absolute_reduction: str
    percentage_reduction: str
    emissions_unit: str


class FinancialImpactDTO(DTO):
    baseline_cost: str | None
    scenario_cost: str | None
    absolute_savings: str | None
    percentage_savings: str | None
    is_available: bool
    missing_reason: str


class ScenarioDTO(DTO):
    name: str
    description: str
    intervention_type: str
    target_activity_ids: list[str]
    assumptions: list[str]
    carbon_impact: ImpactDTO
    financial_impact: FinancialImpactDTO
    baseline_result_ids: list[str]
    scenario_evidence: list[EvidenceDTO]


class RecommendationDTO(DTO):
    title: str
    rationale: str
    target_hotspot: str
    target_activity_ids: list[str]
    status: str
    explanation: str
    validation_errors: list[str]
    scenario: ScenarioDTO | None


class RunSummaryResponse(DTO):
    run_id: str
    filename: str
    provider: str
    year: int
    country: str
    total_emissions: str
    emissions_unit: str
    scope_totals: dict[str, str]
    statistics: dict[str, int | float]
    hotspots: list[HotspotDTO]
    scope_contributions: list[ContributionDTO]
    category_contributions: dict[str, list[ContributionDTO]]
    activity_contributions: list[ContributionDTO]
    insights: list[InsightDTO]
    data_quality: DataQualityDTO


class ActivitiesResponse(DTO):
    run_id: str
    total: int
    offset: int
    limit: int
    activities: list[ActivityDTO]


class EvidenceResponse(DTO):
    run_id: str
    evidence: list[EvidenceDTO]
    calculation_rejections: list[dict[str, str]]


class RecommendationsResponse(DTO):
    run_id: str
    recommendations: list[RecommendationDTO]


class ScenarioRequest(DTO):
    name: str = "Custom scenario"
    description: str = "User-defined deterministic scenario"
    target_activity_ids: list[str] = Field(min_length=1)
    intervention_type: Literal["PercentageReduction", "AbsoluteReduction", "FuelSubstitution"]
    reduction_percentage: str | None = None
    reduction_amount: str | None = None
    new_activity_type: str | None = None
    new_unit: str | None = None
    new_scope: str | None = None
    new_category: str | None = None
    conversion_multiplier: str | None = None
    new_unit_price: str | None = None


class ScenarioResponse(DTO):
    run_id: str
    scenario: ScenarioDTO
