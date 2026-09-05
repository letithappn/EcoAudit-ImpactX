"""
Tests for input validation.

Covers:
- Activity validation: positive quantity, non-empty fields, scope-category
- Factor validation: positive value, required metadata, year range
- Compatibility: unit compatibility, scope match, category match
"""

from decimal import Decimal

import pytest

from ecoaudit.carbon.models import ActivityData, EmissionFactor
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.carbon.validation import ValidationError, validate_activity, validate_compatibility, validate_factor


class TestActivityValidation:
    """Validate ActivityData records."""

    def test_valid_activity_passes(self, diesel_activity: ActivityData) -> None:
        # Should not raise.
        validate_activity(diesel_activity)

    def test_zero_quantity_rejected(self) -> None:
        activity = ActivityData(
            activity_id="ACT-ZERO",
            description="Zero test",
            quantity=Decimal("0"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        with pytest.raises(ValidationError, match="positive"):
            validate_activity(activity)

    def test_negative_quantity_rejected(self) -> None:
        activity = ActivityData(
            activity_id="ACT-NEG",
            description="Negative test",
            quantity=Decimal("-100"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        with pytest.raises(ValidationError, match="positive"):
            validate_activity(activity)

    def test_empty_activity_id_rejected(self) -> None:
        activity = ActivityData(
            activity_id="",
            description="Test",
            quantity=Decimal("100"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        with pytest.raises(ValidationError, match="Activity ID"):
            validate_activity(activity)

    def test_empty_description_rejected(self) -> None:
        activity = ActivityData(
            activity_id="ACT-X",
            description="",
            quantity=Decimal("100"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        with pytest.raises(ValidationError, match="description"):
            validate_activity(activity)

    def test_wrong_scope_category_rejected(self) -> None:
        """Purchased electricity is Scope 2, not Scope 1."""
        activity = ActivityData(
            activity_id="ACT-BAD",
            description="Wrong scope-category",
            quantity=Decimal("100"),
            unit=Unit.KWH,
            scope=Scope.SCOPE_1,
            category=Category.PURCHASED_ELECTRICITY,
        )
        with pytest.raises(ValidationError, match="not valid under"):
            validate_activity(activity)

    def test_scope3_category_under_scope1_rejected(self) -> None:
        """Upstream transportation is Scope 3, not Scope 1."""
        activity = ActivityData(
            activity_id="ACT-BAD2",
            description="Wrong scope",
            quantity=Decimal("100"),
            unit=Unit.KG,
            scope=Scope.SCOPE_1,
            category=Category.UPSTREAM_TRANSPORTATION,
        )
        with pytest.raises(ValidationError, match="not valid under"):
            validate_activity(activity)


class TestFactorValidation:
    """Validate EmissionFactor records."""

    def test_valid_factor_passes(self, diesel_factor_2024: EmissionFactor) -> None:
        validate_factor(diesel_factor_2024)

    def test_zero_value_rejected(self) -> None:
        factor = EmissionFactor(
            factor_id="BAD-FACTOR",
            activity_type="test",
            value=Decimal("0"),
            unit="kgCO2e/litre",
            per_unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
            country="UK",
            year=2024,
            source="Test",
            source_url="https://example.com",
            methodology="Test",
            version="1.0",
        )
        with pytest.raises(ValidationError, match="positive"):
            validate_factor(factor)

    def test_negative_value_rejected(self) -> None:
        factor = EmissionFactor(
            factor_id="BAD-FACTOR-NEG",
            activity_type="test",
            value=Decimal("-1.5"),
            unit="kgCO2e/litre",
            per_unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
            country="UK",
            year=2024,
            source="Test",
            source_url="https://example.com",
            methodology="Test",
            version="1.0",
        )
        with pytest.raises(ValidationError, match="positive"):
            validate_factor(factor)

    def test_empty_source_rejected(self) -> None:
        factor = EmissionFactor(
            factor_id="BAD-SRC",
            activity_type="test",
            value=Decimal("1.0"),
            unit="kgCO2e/litre",
            per_unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
            country="UK",
            year=2024,
            source="",
            source_url="https://example.com",
            methodology="Test",
            version="1.0",
        )
        with pytest.raises(ValidationError, match="source"):
            validate_factor(factor)

    def test_invalid_year_rejected(self) -> None:
        factor = EmissionFactor(
            factor_id="BAD-YEAR",
            activity_type="test",
            value=Decimal("1.0"),
            unit="kgCO2e/litre",
            per_unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
            country="UK",
            year=1800,
            source="Test",
            source_url="https://example.com",
            methodology="Test",
            version="1.0",
        )
        with pytest.raises(ValidationError, match="year"):
            validate_factor(factor)


class TestCompatibilityValidation:
    """Validate activity-factor compatibility."""

    def test_compatible_units(
        self,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        # Should not raise.
        validate_compatibility(diesel_activity, diesel_factor_2024)

    def test_incompatible_units_rejected(
        self,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        """Activity in kWh with a factor expecting litres."""
        activity = ActivityData(
            activity_id="ACT-BAD-UNIT",
            description="Wrong unit",
            quantity=Decimal("100"),
            unit=Unit.KWH,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        with pytest.raises(ValidationError, match="not compatible"):
            validate_compatibility(activity, diesel_factor_2024)

    def test_scope_mismatch_rejected(self) -> None:
        """Activity is Scope 1 but factor is Scope 2."""
        activity = ActivityData(
            activity_id="ACT-S1",
            description="Scope 1 activity",
            quantity=Decimal("100"),
            unit=Unit.KWH,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        factor = EmissionFactor(
            factor_id="F-S2",
            activity_type="elec",
            value=Decimal("0.5"),
            unit="kgCO2e/kWh",
            per_unit=Unit.KWH,
            scope=Scope.SCOPE_2,
            category=Category.PURCHASED_ELECTRICITY,
            country="UK",
            year=2024,
            source="Test",
            source_url="https://example.com",
            methodology="Test",
            version="1.0",
        )
        with pytest.raises(ValidationError, match="Scope mismatch"):
            validate_compatibility(activity, factor)

    def test_category_mismatch_rejected(self) -> None:
        """Same scope but different category."""
        activity = ActivityData(
            activity_id="ACT-CAT1",
            description="Stationary",
            quantity=Decimal("100"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        factor = EmissionFactor(
            factor_id="F-CAT2",
            activity_type="petrol",
            value=Decimal("2.3"),
            unit="kgCO2e/litre",
            per_unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.MOBILE_COMBUSTION,
            country="UK",
            year=2024,
            source="Test",
            source_url="https://example.com",
            methodology="Test",
            version="1.0",
        )
        with pytest.raises(ValidationError, match="Category mismatch"):
            validate_compatibility(activity, factor)
