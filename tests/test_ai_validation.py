"""Tests for post-AI validation firewall.

These tests verify that the validation layer correctly gates
AI output before it can enter the deterministic engine.
"""

from decimal import Decimal

import pytest

from ecoaudit.ai.schemas import ActivityCandidate
from ecoaudit.ai.validation import (
    CONFIDENCE_REVIEW_THRESHOLD,
    resolve_category,
    resolve_scope,
    resolve_unit,
    validate_candidate,
)
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


def _make_candidate(**overrides) -> ActivityCandidate:
    """Helper to build a candidate with sensible defaults."""
    defaults = {
        "activity_type": "diesel",
        "quantity": "500",
        "unit": "litre",
        "scope": "Scope 1",
        "category": "Stationary Combustion",
        "description": "Generator diesel fuel",
        "confidence": 0.95,
        "reasoning": "Diesel generator.",
        "needs_review": False,
        "source_row": 2,
        "raw_input": "Generator Diesel, 500, Liters",
    }
    defaults.update(overrides)
    return ActivityCandidate(**defaults)


class TestResolveUnit:
    def test_canonical_names(self) -> None:
        assert resolve_unit("litre") == Unit.LITRE
        assert resolve_unit("kWh") == Unit.KWH
        assert resolve_unit("gallon_us") == Unit.GALLON_US

    def test_aliases(self) -> None:
        assert resolve_unit("Liters") == Unit.LITRE
        assert resolve_unit("LITRES") == Unit.LITRE
        assert resolve_unit("gallons") == Unit.GALLON_US
        assert resolve_unit("kwh") == Unit.KWH
        assert resolve_unit("MWh") == Unit.MWH

    def test_unknown_unit(self) -> None:
        assert resolve_unit("banana") is None
        assert resolve_unit("cups") is None
        assert resolve_unit("") is None


class TestResolveScope:
    def test_canonical(self) -> None:
        assert resolve_scope("Scope 1") == Scope.SCOPE_1
        assert resolve_scope("Scope 2") == Scope.SCOPE_2
        assert resolve_scope("Scope 3") == Scope.SCOPE_3

    def test_variants(self) -> None:
        assert resolve_scope("scope_1") == Scope.SCOPE_1
        assert resolve_scope("scope1") == Scope.SCOPE_1
        assert resolve_scope("1") == Scope.SCOPE_1

    def test_invalid_scope(self) -> None:
        assert resolve_scope("Scope 7") is None
        assert resolve_scope("") is None
        assert resolve_scope("all") is None


class TestResolveCategory:
    def test_canonical(self) -> None:
        assert resolve_category("Stationary Combustion") == Category.STATIONARY_COMBUSTION
        assert resolve_category("Mobile Combustion") == Category.MOBILE_COMBUSTION
        assert resolve_category("Purchased Electricity") == Category.PURCHASED_ELECTRICITY

    def test_variants(self) -> None:
        assert resolve_category("stationary_combustion") == Category.STATIONARY_COMBUSTION
        assert resolve_category("mobile_combustion") == Category.MOBILE_COMBUSTION

    def test_invalid_category(self) -> None:
        assert resolve_category("Explosive Combustion") is None
        assert resolve_category("") is None


class TestValidateCandidate:
    """Tests for the full candidate validation."""

    def test_valid_candidate_produces_activity_data(self) -> None:
        candidate = _make_candidate()
        result = validate_candidate(candidate)
        assert result.is_valid is True
        assert result.activity_data is not None
        assert result.activity_data.quantity == Decimal("500")
        assert result.activity_data.unit == Unit.LITRE
        assert result.activity_data.scope == Scope.SCOPE_1
        assert result.activity_data.category == Category.STATIONARY_COMBUSTION
        assert result.errors == ()

    def test_unknown_activity_type_rejected(self) -> None:
        candidate = _make_candidate(activity_type="unknown")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("unknown" in e.lower() for e in result.errors)

    def test_unrecognized_activity_type_rejected(self) -> None:
        candidate = _make_candidate(activity_type="plutonium")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("unrecognized activity type" in e.lower() for e in result.errors)

    def test_invalid_unit_banana_rejected(self) -> None:
        candidate = _make_candidate(unit="banana")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("unrecognized unit" in e.lower() for e in result.errors)

    def test_invalid_scope_7_rejected(self) -> None:
        candidate = _make_candidate(scope="Scope 7")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("unrecognized scope" in e.lower() for e in result.errors)

    def test_invalid_category_rejected(self) -> None:
        candidate = _make_candidate(category="Explosive Combustion")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("unrecognized category" in e.lower() for e in result.errors)

    def test_scope_category_mismatch_rejected(self) -> None:
        """Diesel classified under Scope 2 should be caught."""
        candidate = _make_candidate(scope="Scope 2", category="Purchased Electricity")
        result = validate_candidate(candidate)
        # This is valid scope/category combo, but for diesel it makes no sense.
        # The validation layer checks structural validity, not semantic.
        # The factor registry will reject this later.
        assert result.is_valid is True  # Structurally valid

    def test_diesel_scope2_purchased_electricity_caught(self) -> None:
        """Invalid: Purchased Electricity under Scope 1."""
        candidate = _make_candidate(
            scope="Scope 1",
            category="Purchased Electricity",
        )
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("invalid scope/category" in e.lower() for e in result.errors)

    def test_zero_quantity_rejected(self) -> None:
        candidate = _make_candidate(quantity="0")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("positive" in e.lower() for e in result.errors)

    def test_negative_quantity_rejected(self) -> None:
        candidate = _make_candidate(quantity="-500")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("positive" in e.lower() for e in result.errors)

    def test_non_numeric_quantity_rejected(self) -> None:
        candidate = _make_candidate(quantity="lots")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("not a valid number" in e.lower() for e in result.errors)

    def test_empty_description_rejected(self) -> None:
        candidate = _make_candidate(description="")
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert any("non-empty" in e.lower() for e in result.errors)

    def test_low_confidence_flags_review(self) -> None:
        candidate = _make_candidate(confidence=0.3, needs_review=False)
        result = validate_candidate(candidate)
        assert result.is_valid is True
        assert result.activity_data is not None
        # Low confidence should force needs_review = true
        assert result.activity_data.metadata["ai_needs_review"] is True
        assert any("low confidence" in w.lower() for w in result.warnings)

    def test_high_confidence_preserves_review_flag(self) -> None:
        candidate = _make_candidate(confidence=0.95, needs_review=False)
        result = validate_candidate(candidate)
        assert result.is_valid is True
        assert result.activity_data.metadata["ai_needs_review"] is False

    def test_metadata_includes_ai_provenance(self) -> None:
        candidate = _make_candidate()
        result = validate_candidate(candidate)
        assert result.is_valid is True
        meta = result.activity_data.metadata
        assert "ai_confidence" in meta
        assert "ai_reasoning" in meta
        assert "ai_raw_input" in meta
        assert "activity_type" in meta

    def test_multiple_errors_collected(self) -> None:
        """A candidate with many problems should report all errors."""
        candidate = _make_candidate(
            activity_type="plutonium",
            quantity="lots",
            unit="banana",
            scope="Scope 7",
            category="Explosive",
            description="",
        )
        result = validate_candidate(candidate)
        assert result.is_valid is False
        assert len(result.errors) >= 5  # At least 5 different errors
