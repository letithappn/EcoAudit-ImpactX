"""
Post-AI validation firewall.

This module is the CRITICAL BOUNDARY between AI output and the
deterministic carbon engine. It converts ActivityCandidates into
validated ActivityData objects, rejecting anything that violates
domain rules.

The AI is never trusted. Every field is re-validated against the
actual domain model before it can enter the calculation pipeline.
"""

from __future__ import annotations

import uuid
from decimal import Decimal, InvalidOperation

from ecoaudit.ai.schemas import ActivityCandidate, CandidateValidationResult
from ecoaudit.carbon.models import ActivityData
from ecoaudit.carbon.scopes import Category, Scope, is_valid_scope_category
from ecoaudit.carbon.units import Unit


# Valid string-to-enum mappings. These are the ONLY values the AI may produce.
# Anything else is rejected.

_UNIT_MAP: dict[str, Unit] = {
    # Canonical names
    "litre": Unit.LITRE,
    "gallon_us": Unit.GALLON_US,
    "m3": Unit.CUBIC_METRE,
    "kg": Unit.KG,
    "tonne": Unit.TONNE,
    "kWh": Unit.KWH,
    "MWh": Unit.MWH,
    "kBtu": Unit.KBTU,
    "km": Unit.KILOMETRE,
    "mile": Unit.MILE,
    # Common aliases (case-insensitive lookup below)
    "litres": Unit.LITRE,
    "liter": Unit.LITRE,
    "liters": Unit.LITRE,
    "l": Unit.LITRE,
    "gallon": Unit.GALLON_US,
    "gallons": Unit.GALLON_US,
    "gal": Unit.GALLON_US,
    "cubic_metre": Unit.CUBIC_METRE,
    "cubic metre": Unit.CUBIC_METRE,
    "cubic meter": Unit.CUBIC_METRE,
    "kwh": Unit.KWH,
    "kilowatt-hour": Unit.KWH,
    "kilowatt hour": Unit.KWH,
    "mwh": Unit.MWH,
    "megawatt-hour": Unit.MWH,
    "megawatt hour": Unit.MWH,
    "kbtu": Unit.KBTU,
    "kilogram": Unit.KG,
    "kilograms": Unit.KG,
    "tonne": Unit.TONNE,
    "tonnes": Unit.TONNE,
    "metric ton": Unit.TONNE,
    "metric tons": Unit.TONNE,
    "kilometer": Unit.KILOMETRE,
    "kilometres": Unit.KILOMETRE,
    "kilometers": Unit.KILOMETRE,
    "miles": Unit.MILE,
}

_SCOPE_MAP: dict[str, Scope] = {
    "scope 1": Scope.SCOPE_1,
    "scope_1": Scope.SCOPE_1,
    "scope1": Scope.SCOPE_1,
    "1": Scope.SCOPE_1,
    "scope 2": Scope.SCOPE_2,
    "scope_2": Scope.SCOPE_2,
    "scope2": Scope.SCOPE_2,
    "2": Scope.SCOPE_2,
    "scope 3": Scope.SCOPE_3,
    "scope_3": Scope.SCOPE_3,
    "scope3": Scope.SCOPE_3,
    "3": Scope.SCOPE_3,
}

_CATEGORY_MAP: dict[str, Category] = {
    "stationary combustion": Category.STATIONARY_COMBUSTION,
    "stationary_combustion": Category.STATIONARY_COMBUSTION,
    "mobile combustion": Category.MOBILE_COMBUSTION,
    "mobile_combustion": Category.MOBILE_COMBUSTION,
    "fugitive emissions": Category.FUGITIVE_EMISSIONS,
    "fugitive_emissions": Category.FUGITIVE_EMISSIONS,
    "process emissions": Category.PROCESS_EMISSIONS,
    "process_emissions": Category.PROCESS_EMISSIONS,
    "purchased electricity": Category.PURCHASED_ELECTRICITY,
    "purchased_electricity": Category.PURCHASED_ELECTRICITY,
    "purchased heat/steam/cooling": Category.PURCHASED_HEAT_STEAM,
    "purchased_heat_steam": Category.PURCHASED_HEAT_STEAM,
    "purchased goods & services": Category.PURCHASED_GOODS_SERVICES,
    "purchased_goods_services": Category.PURCHASED_GOODS_SERVICES,
    "upstream transportation & distribution": Category.UPSTREAM_TRANSPORTATION,
    "upstream_transportation": Category.UPSTREAM_TRANSPORTATION,
    "waste generated in operations": Category.WASTE_GENERATED,
    "waste_generated": Category.WASTE_GENERATED,
    "business travel": Category.BUSINESS_TRAVEL,
    "business_travel": Category.BUSINESS_TRAVEL,
    "employee commuting": Category.EMPLOYEE_COMMUTING,
    "employee_commuting": Category.EMPLOYEE_COMMUTING,
}

# Known valid activity types from our factor registry.
# The AI must classify into one of these or "unknown".
KNOWN_ACTIVITY_TYPES: frozenset[str] = frozenset({
    "diesel",
    "petrol",
    "natural_gas",
    "grid_electricity",
    "unknown",
})

# Confidence threshold below which we force needs_review = true
CONFIDENCE_REVIEW_THRESHOLD: float = 0.7


def resolve_unit(raw: str) -> Unit | None:
    """Resolve a raw unit string to a Unit enum member."""
    return _UNIT_MAP.get(raw.lower().strip())


def resolve_scope(raw: str) -> Scope | None:
    """Resolve a raw scope string to a Scope enum member."""
    return _SCOPE_MAP.get(raw.lower().strip())


def resolve_category(raw: str) -> Category | None:
    """Resolve a raw category string to a Category enum member."""
    return _CATEGORY_MAP.get(raw.lower().strip())


def validate_candidate(
    candidate: ActivityCandidate,
    known_activity_types: frozenset[str] = KNOWN_ACTIVITY_TYPES,
) -> CandidateValidationResult:
    """Validate an AI-produced ActivityCandidate against domain rules.

    This is the FIREWALL between AI output and the deterministic engine.
    Every field is checked. Nothing is trusted.

    Args:
        candidate: The AI-produced candidate.
        known_activity_types: Set of valid activity type strings.

    Returns:
        A CandidateValidationResult with validation outcome.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Activity type must be known
    activity_type = candidate.activity_type.lower().strip()
    if activity_type == "unknown":
        errors.append(
            "Activity type is 'unknown' — AI could not classify this row."
        )
    elif activity_type not in known_activity_types:
        errors.append(
            f"Unrecognized activity type: '{candidate.activity_type}'. "
            f"Valid types: {sorted(known_activity_types - {'unknown'})}"
        )

    # 2. Quantity must be a positive Decimal
    quantity: Decimal | None = None
    try:
        quantity = Decimal(candidate.quantity)
        if quantity <= Decimal("0"):
            errors.append(
                f"Quantity must be positive, got {quantity}."
            )
    except (InvalidOperation, ValueError):
        errors.append(
            f"Quantity is not a valid number: '{candidate.quantity}'."
        )

    # 3. Unit must resolve to a known Unit
    unit = resolve_unit(candidate.unit)
    if unit is None:
        errors.append(
            f"Unrecognized unit: '{candidate.unit}'. "
            f"Valid units include: litre, gallon_us, m3, kg, tonne, kWh, MWh, kBtu, km, mile"
        )

    # 4. Scope must resolve to a known Scope
    scope = resolve_scope(candidate.scope)
    if scope is None:
        errors.append(
            f"Unrecognized scope: '{candidate.scope}'. "
            f"Valid scopes: Scope 1, Scope 2, Scope 3"
        )

    # 5. Category must resolve to a known Category
    category = resolve_category(candidate.category)
    if category is None:
        errors.append(
            f"Unrecognized category: '{candidate.category}'. "
            f"Valid categories include: Stationary Combustion, Mobile Combustion, "
            f"Purchased Electricity, etc."
        )

    # 6. Scope/Category combination must be valid per GHG Protocol
    if scope is not None and category is not None:
        if not is_valid_scope_category(scope, category):
            errors.append(
                f"Invalid scope/category combination: "
                f"{scope.value} + {category.value}. "
                f"This violates GHG Protocol scope-category mapping."
            )

    # 7. Description must be non-empty
    if not candidate.description.strip():
        errors.append("Description must be non-empty.")

    # 8. Confidence warnings (not errors — but we override needs_review)
    needs_review = candidate.needs_review
    if candidate.confidence < CONFIDENCE_REVIEW_THRESHOLD:
        needs_review = True
        warnings.append(
            f"Low confidence ({candidate.confidence:.2f}) — flagged for human review."
        )

    # Build result
    if errors:
        return CandidateValidationResult(
            candidate=candidate,
            is_valid=False,
            activity_data=None,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    # All checks passed — build the validated ActivityData
    assert quantity is not None
    assert unit is not None
    assert scope is not None
    assert category is not None

    activity_data = ActivityData(
        activity_id=f"AI-{uuid.uuid4().hex[:8]}",
        description=candidate.description,
        quantity=quantity,
        unit=unit,
        scope=scope,
        category=category,
        source_row=candidate.source_row,
        metadata={
            "activity_type": activity_type,
            "ai_confidence": candidate.confidence,
            "ai_reasoning": candidate.reasoning,
            "ai_needs_review": needs_review,
            "ai_raw_input": candidate.raw_input,
        },
    )

    return CandidateValidationResult(
        candidate=candidate,
        is_valid=True,
        activity_data=activity_data,
        errors=(),
        warnings=tuple(warnings),
    )
