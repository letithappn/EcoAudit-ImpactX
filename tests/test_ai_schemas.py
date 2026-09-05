"""Tests for AI output schemas."""

from decimal import Decimal

import pytest

from ecoaudit.ai.schemas import ActivityCandidate, parse_ai_response


class TestActivityCandidate:
    """Tests for ActivityCandidate construction."""

    def test_valid_construction(self) -> None:
        c = ActivityCandidate(
            activity_type="diesel",
            quantity="500",
            unit="litre",
            scope="Scope 1",
            category="Stationary Combustion",
            description="Generator diesel",
            confidence=0.95,
            reasoning="Diesel generator.",
            needs_review=False,
            source_row=2,
            raw_input="Diesel Generator, 500, Liters",
        )
        assert c.activity_type == "diesel"
        assert c.quantity == "500"
        assert c.confidence == 0.95
        assert c.needs_review is False

    def test_frozen_immutability(self) -> None:
        c = ActivityCandidate(
            activity_type="diesel",
            quantity="100",
            unit="litre",
            scope="Scope 1",
            category="Stationary Combustion",
            description="Test",
            confidence=0.9,
            reasoning="Test",
            needs_review=False,
        )
        with pytest.raises(AttributeError):
            c.activity_type = "petrol"  # type: ignore[misc]


class TestParseAIResponse:
    """Tests for parsing raw JSON dicts into ActivityCandidates."""

    def test_valid_response(self) -> None:
        raw = {
            "activity_type": "grid_electricity",
            "quantity": "12000",
            "unit": "kWh",
            "scope": "Scope 2",
            "category": "Purchased Electricity",
            "description": "Office electricity",
            "confidence": 0.95,
            "reasoning": "Monthly bill.",
            "needs_review": False,
        }
        candidate = parse_ai_response(raw)
        assert candidate.activity_type == "grid_electricity"
        assert candidate.quantity == "12000"
        assert candidate.needs_review is False

    def test_missing_required_key(self) -> None:
        raw = {
            "activity_type": "diesel",
            "quantity": "500",
            # missing: unit, scope, category, description, confidence, reasoning, needs_review
        }
        with pytest.raises(ValueError, match="missing required keys"):
            parse_ai_response(raw)

    def test_invalid_confidence_type(self) -> None:
        raw = {
            "activity_type": "diesel",
            "quantity": "500",
            "unit": "litre",
            "scope": "Scope 1",
            "category": "Stationary Combustion",
            "description": "Test",
            "confidence": "not_a_number",
            "reasoning": "Test",
            "needs_review": False,
        }
        with pytest.raises(ValueError, match="Invalid confidence"):
            parse_ai_response(raw)

    def test_confidence_out_of_range(self) -> None:
        raw = {
            "activity_type": "diesel",
            "quantity": "500",
            "unit": "litre",
            "scope": "Scope 1",
            "category": "Stationary Combustion",
            "description": "Test",
            "confidence": 1.5,
            "reasoning": "Test",
            "needs_review": False,
        }
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            parse_ai_response(raw)

    def test_needs_review_not_boolean(self) -> None:
        raw = {
            "activity_type": "diesel",
            "quantity": "500",
            "unit": "litre",
            "scope": "Scope 1",
            "category": "Stationary Combustion",
            "description": "Test",
            "confidence": 0.9,
            "reasoning": "Test",
            "needs_review": "yes",
        }
        with pytest.raises(ValueError, match="must be a boolean"):
            parse_ai_response(raw)

    def test_empty_quantity(self) -> None:
        raw = {
            "activity_type": "diesel",
            "quantity": "",
            "unit": "litre",
            "scope": "Scope 1",
            "category": "Stationary Combustion",
            "description": "Test",
            "confidence": 0.9,
            "reasoning": "Test",
            "needs_review": False,
        }
        with pytest.raises(ValueError, match="non-empty"):
            parse_ai_response(raw)

    def test_numeric_quantity_accepted(self) -> None:
        """The AI might return quantity as a number, not string."""
        raw = {
            "activity_type": "diesel",
            "quantity": 500,
            "unit": "litre",
            "scope": "Scope 1",
            "category": "Stationary Combustion",
            "description": "Test",
            "confidence": 0.9,
            "reasoning": "Test",
            "needs_review": False,
        }
        candidate = parse_ai_response(raw)
        assert candidate.quantity == "500"

    def test_extra_keys_ignored(self) -> None:
        raw = {
            "activity_type": "diesel",
            "quantity": "500",
            "unit": "litre",
            "scope": "Scope 1",
            "category": "Stationary Combustion",
            "description": "Test",
            "confidence": 0.9,
            "reasoning": "Test",
            "needs_review": False,
            "extra_field": "ignored",
        }
        candidate = parse_ai_response(raw)
        assert candidate.activity_type == "diesel"
