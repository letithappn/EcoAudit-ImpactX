"""
Tests for the deterministic carbon calculation engine.

Covers:
- Basic activity × emission factor calculation
- Diesel reference calculation (10,000L × 2.51210 = 25,121.0 kgCO2e)
- Unit conversion during calculation (gallons → litres)
- Calculation trace completeness
- Scope and category metadata on results
- Numerical precision (Decimal arithmetic)
- Deterministic reproducibility (same input → same output)
"""

from decimal import Decimal

import pytest

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.models import ActivityData, CalculationResult, EmissionFactor
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.carbon.validation import ValidationError


class TestBasicCalculation:
    """Core calculation: emissions = quantity × factor."""

    def test_diesel_10000_litres(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        """Reference: 10,000L diesel × 2.51210 kgCO2e/L = 25,121.00000 kgCO2e.

        DEFRA 2024 Condensed Set, Fuels, Diesel (average biofuel blend).
        """
        result = calculator.calculate(diesel_activity, diesel_factor_2024)

        expected = Decimal("10000") * Decimal("2.51210")
        assert result.emissions_value == expected
        assert result.emissions_value == Decimal("25121.00000")
        assert result.emissions_unit == "kgCO2e"

    def test_electricity_50000_kwh(
        self,
        calculator: CarbonCalculator,
        electricity_activity: ActivityData,
        electricity_factor_uk: EmissionFactor,
    ) -> None:
        """50,000 kWh × 0.20705 = 10,352.50000 kgCO2e."""
        result = calculator.calculate(electricity_activity, electricity_factor_uk)

        expected = Decimal("50000") * Decimal("0.20705")
        assert result.emissions_value == expected
        assert result.emissions_unit == "kgCO2e"

    def test_petrol_2000_litres(
        self,
        calculator: CarbonCalculator,
        petrol_activity: ActivityData,
        petrol_factor_2024: EmissionFactor,
    ) -> None:
        """2,000L petrol × 2.16802 = 4,336.04000 kgCO2e."""
        result = calculator.calculate(petrol_activity, petrol_factor_2024)

        expected = Decimal("2000") * Decimal("2.16802")
        assert result.emissions_value == expected


class TestUnitConversionInCalculation:
    """Calculator should convert units when activity unit ≠ factor per_unit."""

    def test_gallons_converted_to_litres(
        self,
        calculator: CarbonCalculator,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        """Activity in US gallons, factor in litres. Should convert."""
        activity = ActivityData(
            activity_id="ACT-GAL",
            description="Diesel in gallons",
            quantity=Decimal("100"),
            unit=Unit.GALLON_US,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        result = calculator.calculate(activity, diesel_factor_2024)

        # 100 gallons × 3.785411784 = 378.5411784 litres
        # 378.5411784 × 2.51210 = expected emissions
        litres = Decimal("100") * Decimal("3.785411784")
        expected = litres * Decimal("2.51210")
        assert result.emissions_value == expected

        # Trace should reflect the conversion.
        assert result.trace.input_unit == Unit.GALLON_US
        assert result.trace.normalized_unit == Unit.LITRE
        assert result.trace.conversion_factor_applied == Decimal("3.785411784")

    def test_mwh_converted_to_kwh(
        self,
        calculator: CarbonCalculator,
        electricity_factor_uk: EmissionFactor,
    ) -> None:
        """Activity in MWh, factor in kWh. Should convert."""
        activity = ActivityData(
            activity_id="ACT-MWH",
            description="Electricity in MWh",
            quantity=Decimal("50"),
            unit=Unit.MWH,
            scope=Scope.SCOPE_2,
            category=Category.PURCHASED_ELECTRICITY,
        )
        result = calculator.calculate(activity, electricity_factor_uk)

        # 50 MWh × 1000 = 50,000 kWh
        # 50,000 × 0.20705 = expected
        expected = Decimal("50000") * Decimal("0.20705")
        assert result.emissions_value == expected
        assert result.trace.normalized_quantity == Decimal("50000")


class TestCalculationTrace:
    """Verify the audit trace contains all required information."""

    def test_trace_completeness(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        result = calculator.calculate(diesel_activity, diesel_factor_2024)
        trace = result.trace

        # Input data.
        assert trace.input_quantity == Decimal("10000")
        assert trace.input_unit == Unit.LITRE

        # Normalization (no conversion needed — same unit).
        assert trace.normalized_quantity == Decimal("10000")
        assert trace.normalized_unit == Unit.LITRE
        assert trace.conversion_factor_applied == Decimal("1")

        # Factor provenance.
        assert trace.emission_factor_value == Decimal("2.51210")
        assert trace.emission_factor_unit == "kgCO2e/litre"
        assert trace.emission_factor_id == "TEST-DEFRA-2024-DIESEL-LITRE"
        assert trace.emission_factor_source == "UK DESNZ/DEFRA"
        assert trace.emission_factor_year == 2024

        # Formula.
        assert "10000" in trace.formula_description
        assert "2.51210" in trace.formula_description
        assert "kgCO2e" in trace.formula_description

        # Classification.
        assert trace.scope == Scope.SCOPE_1
        assert trace.category == Category.STATIONARY_COMBUSTION

    def test_result_contains_original_activity(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        result = calculator.calculate(diesel_activity, diesel_factor_2024)

        assert result.activity is diesel_activity
        assert result.factor is diesel_factor_2024
        assert result.result_id  # UUID should be non-empty.
        assert result.calculated_at is not None


class TestScopeMetadata:
    """Results must carry correct scope and category."""

    def test_scope1_stationary(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        result = calculator.calculate(diesel_activity, diesel_factor_2024)
        assert result.trace.scope == Scope.SCOPE_1
        assert result.trace.category == Category.STATIONARY_COMBUSTION

    def test_scope2_electricity(
        self,
        calculator: CarbonCalculator,
        electricity_activity: ActivityData,
        electricity_factor_uk: EmissionFactor,
    ) -> None:
        result = calculator.calculate(electricity_activity, electricity_factor_uk)
        assert result.trace.scope == Scope.SCOPE_2
        assert result.trace.category == Category.PURCHASED_ELECTRICITY


class TestDeterminism:
    """Same input + same factor = identical result (value, trace)."""

    def test_reproducible_result(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        r1 = calculator.calculate(diesel_activity, diesel_factor_2024)
        r2 = calculator.calculate(diesel_activity, diesel_factor_2024)

        assert r1.emissions_value == r2.emissions_value
        assert r1.trace.formula_description == r2.trace.formula_description
        assert r1.trace.emission_factor_id == r2.trace.emission_factor_id
        # result_id should differ (unique UUID each time).
        assert r1.result_id != r2.result_id


class TestNumericalPrecision:
    """Verify Decimal precision — no floating-point drift."""

    def test_decimal_not_float(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        result = calculator.calculate(diesel_activity, diesel_factor_2024)
        assert isinstance(result.emissions_value, Decimal)

    def test_small_quantity_precision(
        self,
        calculator: CarbonCalculator,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        """Very small quantities should not lose precision."""
        activity = ActivityData(
            activity_id="ACT-SMALL",
            description="Small diesel",
            quantity=Decimal("0.001"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        result = calculator.calculate(activity, diesel_factor_2024)
        expected = Decimal("0.001") * Decimal("2.51210")
        assert result.emissions_value == expected

    def test_large_quantity_precision(
        self,
        calculator: CarbonCalculator,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        """Very large quantities should not overflow or lose precision."""
        activity = ActivityData(
            activity_id="ACT-LARGE",
            description="Large diesel",
            quantity=Decimal("99999999"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        result = calculator.calculate(activity, diesel_factor_2024)
        expected = Decimal("99999999") * Decimal("2.51210")
        assert result.emissions_value == expected


class TestValidationInCalculator:
    """Calculator should reject invalid inputs via validation layer."""

    def test_zero_quantity_rejected(
        self,
        calculator: CarbonCalculator,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        activity = ActivityData(
            activity_id="ACT-ZERO",
            description="Zero",
            quantity=Decimal("0"),
            unit=Unit.LITRE,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        with pytest.raises(ValidationError):
            calculator.calculate(activity, diesel_factor_2024)

    def test_incompatible_units_rejected(
        self,
        calculator: CarbonCalculator,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        """Activity in kWh, factor expects litres."""
        activity = ActivityData(
            activity_id="ACT-INCOMPAT",
            description="Wrong unit",
            quantity=Decimal("100"),
            unit=Unit.KWH,
            scope=Scope.SCOPE_1,
            category=Category.STATIONARY_COMBUSTION,
        )
        with pytest.raises(ValidationError):
            calculator.calculate(activity, diesel_factor_2024)


class TestNewMetadataFields:
    """Verify the new EmissionFactor metadata fields (gas_basis, etc.)."""

    def test_gas_basis_on_result(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        result = calculator.calculate(diesel_activity, diesel_factor_2024)
        assert result.factor.gas_basis == "CO2E"

    def test_fuel_type_detail_on_result(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        result = calculator.calculate(diesel_activity, diesel_factor_2024)
        assert "average biofuel blend" in result.factor.fuel_type_detail

    def test_dataset_name_on_result(
        self,
        calculator: CarbonCalculator,
        diesel_activity: ActivityData,
        diesel_factor_2024: EmissionFactor,
    ) -> None:
        result = calculator.calculate(diesel_activity, diesel_factor_2024)
        assert result.factor.dataset_name == "Fuels"
