/**
 * TypeScript definitions mirroring backend Pydantic DTOs (api/schemas.py).
 * CRITICAL DIRECTIVE: Authoritative carbon and financial values are serialized
 * as STRINGS from Python Decimal to prevent IEEE 754 precision loss.
 */

export interface RunCreateResponse {
  run_id: string;
  status: string;
  stage: string;
}

export interface RunStatusResponse {
  run_id: string;
  status: string;
  stage: string;
  progress: number;
  provider: string;
  year: number;
  country: string;
  filename: string;
  statistics: Record<string, number>;
  error?: string | null;
}

export interface FactorDTO {
  factor_id: string;
  source: string;
  dataset: string;
  year: number;
  version: string;
  methodology: string;
  applicability_notes: string;
  country: string;
  factor_value: string; // Decimal string
  factor_unit: string;
  is_proxy: boolean;
}

export interface CalculationTraceDTO {
  input_quantity: string;
  input_unit: string;
  normalized_quantity: string;
  normalized_unit: string;
  conversion_factor_applied: string;
  emission_factor_value: string;
  emission_factor_unit: string;
  emission_factor_id: string;
  emission_factor_source: string;
  emission_factor_year: number;
  formula_description: string;
  scope: string;
  category: string;
}

export interface EvidenceDTO {
  result_id: string;
  activity_id: string;
  activity_description: string;
  original_row: Record<string, string>;
  emissions_value: string; // Decimal string
  emissions_unit: string;
  factor: FactorDTO;
  trace: CalculationTraceDTO;
  source_row: number | null;
}

export interface ActivityDTO {
  source_row: number | null;
  original_row: Record<string, string>;
  activity_id: string | null;
  activity_type: string | null;
  description: string | null;
  quantity: string | null;
  unit: string | null;
  scope: string | null;
  category: string | null;
  confidence: string | null;
  needs_review: boolean;
  validation_status: "validated" | "review" | "rejected";
  validation_errors: string[];
  validation_warnings: string[];
  reasoning?: string | null;
}

export interface ContributionDTO {
  label: string;
  emissions: string; // Decimal string
  percentage: string; // Decimal string
  rank: number;
  result_count: number;
  result_ids: string[];
}

export interface HotspotDTO {
  label: string;
  dimension: string;
  emissions: string; // Decimal string
  percentage_of_total: string; // Decimal string
  percentage_of_scope: string | null; // Decimal string
  severity: string;
  rank: number;
  actionability: string;
  contributing_activities: number;
  result_ids: string[];
  parent_scope: string | null;
  parent_category: string | null;
}

export interface InsightDTO {
  insight_type: string;
  severity: string;
  title: string;
  evidence: string;
  detail: string;
}

export interface DataQualityDTO {
  total_results: number;
  results_with_ai_classification: number;
  results_needing_review: number;
  average_ai_confidence: string | null;
  min_ai_confidence: string | null;
  results_with_test_factors: number;
  factor_sources: string[];
}

export interface ImpactDTO {
  baseline_emissions: string; // Decimal string
  scenario_emissions: string; // Decimal string
  absolute_reduction: string; // Decimal string
  percentage_reduction: string; // Decimal string
  emissions_unit: string;
}

export interface FinancialImpactDTO {
  baseline_cost: string | null; // Decimal string
  scenario_cost: string | null; // Decimal string
  absolute_savings: string | null; // Decimal string
  percentage_savings: string | null; // Decimal string
  is_available: boolean;
  missing_reason: string;
}

export interface ScenarioDTO {
  name: string;
  description: string;
  intervention_type: string;
  target_activity_ids: string[];
  assumptions: string[];
  carbon_impact: ImpactDTO;
  financial_impact: FinancialImpactDTO;
  baseline_result_ids: string[];
  scenario_evidence: EvidenceDTO[];
}

export interface RecommendationDTO {
  title: string;
  rationale: string;
  target_hotspot: string;
  target_activity_ids: string[];
  status: string;
  explanation: string;
  validation_errors: string[];
  scenario: ScenarioDTO | null;
}

export interface RunSummaryResponse {
  run_id: string;
  filename: string;
  provider: string;
  year: number;
  country: string;
  total_emissions: string; // Decimal string
  emissions_unit: string;
  scope_totals: Record<string, string>; // e.g. { "Scope 1": "123.45" }
  statistics: Record<string, number>;
  hotspots: HotspotDTO[];
  scope_contributions: ContributionDTO[];
  category_contributions: Record<string, ContributionDTO[]>;
  activity_contributions: ContributionDTO[];
  insights: InsightDTO[];
  data_quality: DataQualityDTO;
}

export interface ActivitiesResponse {
  run_id: string;
  total: number;
  offset: number;
  limit: number;
  activities: ActivityDTO[];
}

export interface EvidenceResponse {
  run_id: string;
  evidence: EvidenceDTO[];
  calculation_rejections: Record<string, string>[];
}

export interface RecommendationsResponse {
  run_id: string;
  recommendations: RecommendationDTO[];
}

export interface ScenarioRequest {
  name?: string;
  description?: string;
  target_activity_ids: string[];
  intervention_type: "PercentageReduction" | "AbsoluteReduction" | "FuelSubstitution";
  reduction_percentage?: string | null;
  reduction_amount?: string | null;
  new_activity_type?: string | null;
  new_unit?: string | null;
  new_scope?: string | null;
  new_category?: string | null;
  conversion_multiplier?: string | null;
  new_unit_price?: string | null;
}

export interface ScenarioResponse {
  run_id: string;
  scenario: ScenarioDTO;
}

export interface AIStatusResponse {
  configured: boolean;
  provider: string;
  model: string;
  status: string;
  message?: string | null;
}

export interface AIConfigRequest {
  api_key: string;
  model?: string | null;
}

export interface AIConfigResponse {
  success: boolean;
  message: string;
  model: string;
}

export interface AITestRequest {
  api_key: string;
  model?: string | null;
}

export interface AITestResponse {
  success: boolean;
  message: string;
  model: string;
  response?: string | null;
}

