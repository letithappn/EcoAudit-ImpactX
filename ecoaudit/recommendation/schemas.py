"""
Validation and parsing of AI candidate outputs.
"""

from __future__ import annotations

from typing import Any

from ecoaudit.recommendation.models import RecommendationCandidate


def parse_candidate_response(raw_json: dict[str, Any]) -> list[RecommendationCandidate]:
    """Parse the raw JSON response from the LLM into candidate objects.
    
    Args:
        raw_json: The parsed JSON dictionary from the LLM.
        
    Returns:
        List of RecommendationCandidate objects.
        
    Raises:
        ValueError: If the JSON structure is invalid.
    """
    if "recommendations" not in raw_json:
        raise ValueError("AI response missing 'recommendations' key at root level.")
        
    recs_list = raw_json["recommendations"]
    if not isinstance(recs_list, list):
        raise ValueError("'recommendations' must be a list.")
        
    candidates = []
    for i, raw_rec in enumerate(recs_list):
        try:
            target_ids = frozenset(str(x) for x in raw_rec["target_activity_ids"])
            parameters = {str(k): str(v) for k, v in raw_rec.get("parameters", {}).items()}
            
            candidate = RecommendationCandidate(
                title=str(raw_rec["title"]),
                target_hotspot=str(raw_rec["target_hotspot"]),
                intervention_type=str(raw_rec["intervention_type"]),
                target_activity_ids=target_ids,
                parameters=parameters,
                rationale=str(raw_rec["rationale"]),
                needs_review=bool(raw_rec.get("needs_review", False)),
            )
            candidates.append(candidate)
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid candidate structure at index {i}: {e}") from e
            
    return candidates
