"""
Recommendation Engine orchestration.

Coordinates AI candidate generation, deterministic verification,
and natural language explanation.
"""

from __future__ import annotations

import logging
from decimal import Decimal

from ecoaudit.ai.providers import AIClient
from ecoaudit.carbon.models import BatchResult
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.intelligence.models import CarbonIntelligenceReport
from ecoaudit.optimization.engine import ScenarioEngine
from ecoaudit.optimization.interventions import (
    AbsoluteReduction,
    FuelSubstitution,
    PercentageReduction,
)
from ecoaudit.optimization.models import ScenarioDefinition, ScenarioResult
from ecoaudit.recommendation.models import (
    Recommendation,
    RecommendationCandidate,
    RecommendationEvidence,
    RecommendationStatus,
)
from ecoaudit.recommendation.prompts import (
    build_candidate_prompt,
    build_explanation_prompt,
)
from ecoaudit.recommendation.schemas import parse_candidate_response


logger = logging.getLogger(__name__)


def _build_intervention(candidate: RecommendationCandidate) -> Any:
    """Safely construct an Intervention object from AI parameters."""
    t = candidate.intervention_type
    p = candidate.parameters
    
    if t == "PercentageReduction":
        if "reduction_percentage" not in p:
            raise ValueError("PercentageReduction requires 'reduction_percentage' parameter.")
        return PercentageReduction(Decimal(p["reduction_percentage"]))
        
    if t == "AbsoluteReduction":
        if "reduction_amount" not in p:
            raise ValueError("AbsoluteReduction requires 'reduction_amount' parameter.")
        return AbsoluteReduction(Decimal(p["reduction_amount"]))
        
    if t == "FuelSubstitution":
        req = ["new_activity_type", "new_unit", "new_scope", "new_category", "conversion_multiplier"]
        for r in req:
            if r not in p:
                raise ValueError(f"FuelSubstitution requires '{r}' parameter.")
                
        return FuelSubstitution(
            new_activity_type=p["new_activity_type"],
            new_unit=Unit(p["new_unit"]),
            new_scope=Scope(p["new_scope"]),
            new_category=Category(p["new_category"]),
            conversion_multiplier=Decimal(p["conversion_multiplier"]),
            new_unit_price=None, # Never guess prices from AI
        )
        
    raise ValueError(f"Unsupported intervention type: {t}")


class RecommendationEngine:
    """Orchestrates the AI recommendation workflow."""

    def __init__(self, ai_client: AIClient, scenario_engine: ScenarioEngine) -> None:
        self.ai_client = ai_client
        self.scenario_engine = scenario_engine

    def generate_recommendations(
        self,
        report: CarbonIntelligenceReport,
        batch: BatchResult,
    ) -> list[Recommendation]:
        """End-to-end recommendation pipeline.
        
        1. Propose candidates via AI.
        2. Evaluate candidates deterministically.
        3. Explain evaluated results via AI.
        
        Args:
            report: The Phase 5 intelligence report to analyze.
            batch: The Phase 1-4 calculation batch (for baseline data).
            
        Returns:
            List of evaluated Recommendation objects.
        """
        # Step 1: Candidate Generation
        prompt = build_candidate_prompt(report)
        try:
            raw_response = self.ai_client.generate_structured(prompt)
            # Ensure it's a dict for our parser
            if isinstance(raw_response, list):
                raw_response = {"recommendations": raw_response}
            candidates = parse_candidate_response(raw_response)
        except Exception as e:
            logger.error("Failed to generate/parse AI candidates: %s", e)
            return []

        recommendations = []

        # Step 2 & 3: Verification & Explanation
        for candidate in candidates:
            # Build Evidence block
            evidence = RecommendationEvidence(
                hotspot_label=candidate.target_hotspot,
                target_activity_ids=candidate.target_activity_ids,
                baseline_result_ids=frozenset(), # Updated if evaluation succeeds
            )
            
            try:
                # Map to Intervention
                intervention = _build_intervention(candidate)
                
                # Build ScenarioDefinition
                definition = ScenarioDefinition(
                    name=candidate.title,
                    description=candidate.rationale,
                    target_activity_ids=candidate.target_activity_ids,
                    intervention=intervention,
                    assumptions=intervention.get_assumptions(),
                )
                
                # Deterministic Evaluation
                scenario_result = self.scenario_engine.evaluate(definition, batch)
                
                # Update evidence with actual baseline results modified
                baseline_ids = frozenset(r.result_id for r in scenario_result.baseline_results)
                evidence = RecommendationEvidence(
                    hotspot_label=candidate.target_hotspot,
                    target_activity_ids=candidate.target_activity_ids,
                    baseline_result_ids=baseline_ids,
                )
                
                # AI Explanation
                explanation_prompt = build_explanation_prompt(scenario_result)
                explanation = self.ai_client.generate_text(explanation_prompt)
                
                status = RecommendationStatus.SUPPORTED
                if candidate.needs_review:
                    status = RecommendationStatus.REQUIRES_REVIEW
                    
                recommendations.append(Recommendation(
                    title=candidate.title,
                    rationale=candidate.rationale,
                    evidence=evidence,
                    scenario_result=scenario_result,
                    explanation=explanation,
                    status=status,
                ))
                
            except Exception as e:
                # Validation or Evaluation Failed
                logger.warning("Rejecting candidate '%s': %s", candidate.title, e)
                recommendations.append(Recommendation(
                    title=candidate.title,
                    rationale=candidate.rationale,
                    evidence=evidence,
                    scenario_result=None,
                    explanation="",
                    status=RecommendationStatus.REJECTED,
                    validation_errors=(str(e),),
                ))

        return recommendations
