"""
Strict structured schemas for AI output.

These schemas define the CONTRACT between the AI classification layer
and the deterministic carbon engine. An ActivityCandidate is a CANDIDATE
classification — it is NOT trusted until it passes post-AI validation.

The AI produces ActivityCandidates.
The validation layer converts valid candidates into ActivityData.
Only ActivityData enters the deterministic engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass(frozen=True)
class ActivityCandidate:
    """AI-produced candidate classification for a single raw data row.

    This is the structured output the AI must produce. Every field is
    a string or primitive that must be validated before it becomes a
    trusted ActivityData object.

    Attributes:
        activity_type: Classified activity (e.g., "diesel", "grid_electricity").
            Must match a registered activity_type in the factor registry.
        quantity: Extracted numeric value as a string (parsed to Decimal later).
        unit: Unit string (must resolve to a Unit enum member).
        scope: Scope string (must resolve to a Scope enum member).
        category: Category string (must resolve to a Category enum member).
        description: Cleaned/normalized description of the activity.
        confidence: Model's self-assessed confidence (0.0 - 1.0).
            NOT blindly trusted — used for review flagging only.
        reasoning: Brief explanation of the classification decision.
        needs_review: True if the AI is uncertain or input is ambiguous.
        source_row: Row number in the original file (for traceability).
        raw_input: The original raw text/row that was classified.
    """

    activity_type: str
    quantity: str  # String, validated to Decimal in post-AI validation
    unit: str
    scope: str
    category: str
    description: str
    confidence: float
    reasoning: str
    needs_review: bool
    source_row: int | None = None
    raw_input: str = ""


@dataclass(frozen=True)
class CandidateValidationResult:
    """Result of validating an ActivityCandidate against domain rules.

    Attributes:
        candidate: The original AI-produced candidate.
        is_valid: Whether the candidate passed all validation checks.
        activity_data: The validated ActivityData (None if invalid).
        errors: Tuple of validation error messages (empty if valid).
        warnings: Tuple of non-fatal warnings (e.g., low confidence).
    """

    candidate: ActivityCandidate
    is_valid: bool
    activity_data: Any | None = None  # Actually ActivityData, avoiding circular import
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def parse_ai_response(raw_json: dict[str, Any]) -> ActivityCandidate:
    """Parse a raw JSON dict from the AI into an ActivityCandidate.

    This function performs STRUCTURAL validation only — it checks that
    required keys exist and types are approximately correct. It does NOT
    perform domain validation (that happens in ai.validation).

    Args:
        raw_json: The parsed JSON response from the AI provider.

    Returns:
        An ActivityCandidate.

    Raises:
        ValueError: If required keys are missing or types are wrong.
    """
    required_keys = {
        "activity_type", "quantity", "unit", "scope",
        "category", "description", "confidence", "reasoning",
        "needs_review",
    }

    missing = required_keys - set(raw_json.keys())
    if missing:
        raise ValueError(
            f"AI response missing required keys: {sorted(missing)}"
        )

    # Validate confidence is a number in [0, 1]
    try:
        confidence = float(raw_json["confidence"])
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid confidence value: {raw_json['confidence']}") from e

    if not (0.0 <= confidence <= 1.0):
        raise ValueError(
            f"Confidence must be between 0.0 and 1.0, got {confidence}"
        )

    # Validate needs_review is a boolean
    needs_review = raw_json["needs_review"]
    if not isinstance(needs_review, bool):
        raise ValueError(
            f"needs_review must be a boolean, got {type(needs_review).__name__}"
        )

    # Validate quantity is parseable as a number (structural check only)
    quantity_str = str(raw_json["quantity"]).strip()
    if not quantity_str:
        raise ValueError("Quantity must be a non-empty string or number.")

    return ActivityCandidate(
        activity_type=str(raw_json["activity_type"]).strip(),
        quantity=quantity_str,
        unit=str(raw_json["unit"]).strip(),
        scope=str(raw_json["scope"]).strip(),
        category=str(raw_json["category"]).strip(),
        description=str(raw_json["description"]).strip(),
        confidence=confidence,
        reasoning=str(raw_json.get("reasoning", "")).strip(),
        needs_review=needs_review,
        source_row=raw_json.get("source_row"),
        raw_input=str(raw_json.get("raw_input", "")).strip(),
    )
