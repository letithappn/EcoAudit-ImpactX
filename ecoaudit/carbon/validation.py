"""
Input validation for the EcoAudit carbon calculation engine.

Validates ActivityData, EmissionFactor, and their compatibility
before any calculation is performed. All validation errors are
raised as ValidationError with descriptive messages.
"""

from decimal import Decimal

from ecoaudit.carbon.models import ActivityData, EmissionFactor
from ecoaudit.carbon.scopes import is_valid_scope_category
from ecoaudit.carbon.units import are_compatible


class ValidationError(Exception):
    """Raised when input data fails validation."""


def validate_activity(activity: ActivityData) -> None:
    """Validate an ActivityData record before calculation.

    Checks:
    - quantity is positive (> 0)
    - activity_id is non-empty
    - description is non-empty
    - scope and category are a valid combination per GHG Protocol

    Args:
        activity: The activity data to validate.

    Raises:
        ValidationError: If any validation check fails.
    """
    if not activity.activity_id or not activity.activity_id.strip():
        raise ValidationError(
            "Activity ID must be a non-empty string."
        )

    if not activity.description or not activity.description.strip():
        raise ValidationError(
            "Activity description must be a non-empty string."
        )

    if not isinstance(activity.quantity, Decimal):
        raise ValidationError(
            f"Activity quantity must be a Decimal, got {type(activity.quantity).__name__}."
        )

    if activity.quantity <= Decimal("0"):
        raise ValidationError(
            f"Activity quantity must be positive, got {activity.quantity}."
        )

    if not is_valid_scope_category(activity.scope, activity.category):
        raise ValidationError(
            f"Category {activity.category} is not valid under {activity.scope}. "
            f"Check GHG Protocol scope-category mapping."
        )


def validate_factor(factor: EmissionFactor) -> None:
    """Validate an EmissionFactor record.

    Checks:
    - factor_id is non-empty
    - value is positive (> 0)
    - required metadata fields are non-empty
    - year is reasonable (1990–2100)

    Args:
        factor: The emission factor to validate.

    Raises:
        ValidationError: If any validation check fails.
    """
    if not factor.factor_id or not factor.factor_id.strip():
        raise ValidationError(
            "Factor ID must be a non-empty string."
        )

    if not isinstance(factor.value, Decimal):
        raise ValidationError(
            f"Factor value must be a Decimal, got {type(factor.value).__name__}."
        )

    if factor.value <= Decimal("0"):
        raise ValidationError(
            f"Factor value must be positive, got {factor.value}."
        )

    if not factor.source or not factor.source.strip():
        raise ValidationError(
            "Factor source must be a non-empty string."
        )

    if not factor.source_url or not factor.source_url.strip():
        raise ValidationError(
            "Factor source_url must be a non-empty string."
        )

    if not (1990 <= factor.year <= 2100):
        raise ValidationError(
            f"Factor year must be between 1990 and 2100, got {factor.year}."
        )


def validate_compatibility(
    activity: ActivityData,
    factor: EmissionFactor,
) -> None:
    """Validate that an activity and factor are compatible for calculation.

    Checks:
    - The activity's unit is compatible with (convertible to) the
      factor's per_unit.
    - The scope matches.
    - The category matches.

    Args:
        activity: The activity data.
        factor: The emission factor.

    Raises:
        ValidationError: If they are not compatible.
    """
    if not are_compatible(activity.unit, factor.per_unit):
        raise ValidationError(
            f"Activity unit {activity.unit.value} is not compatible with "
            f"factor unit {factor.per_unit.value}. "
            f"Cannot convert between different dimensions."
        )

    if activity.scope != factor.scope:
        raise ValidationError(
            f"Scope mismatch: activity is {activity.scope}, "
            f"factor is {factor.scope}."
        )

    if activity.category != factor.category:
        raise ValidationError(
            f"Category mismatch: activity is {activity.category}, "
            f"factor is {factor.category}."
        )
