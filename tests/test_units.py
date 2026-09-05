"""
Tests for the unit conversion engine.

Covers:
- Same-unit identity conversion
- Volume conversions (litres ↔ gallons, litres ↔ m³)
- Mass conversions (kg ↔ tonne)
- Energy conversions (kWh ↔ MWh)
- Distance conversions (km ↔ mile)
- Incompatible unit rejection (litres → kWh)
- Precision (Decimal, no float drift)
"""

from decimal import Decimal

import pytest

from ecoaudit.carbon.units import Unit, UnitConversionError, are_compatible, convert


class TestIdentityConversion:
    """Converting a unit to itself should return the same quantity."""

    def test_litre_to_litre(self) -> None:
        result, factor = convert(Decimal("100"), Unit.LITRE, Unit.LITRE)
        assert result == Decimal("100")
        assert factor == Decimal("1")

    def test_kwh_to_kwh(self) -> None:
        result, factor = convert(Decimal("5000"), Unit.KWH, Unit.KWH)
        assert result == Decimal("5000")
        assert factor == Decimal("1")


class TestVolumeConversions:
    """Volume dimension conversions."""

    def test_gallons_to_litres(self) -> None:
        # 1 US gallon = 3.785411784 litres
        result, factor = convert(Decimal("1"), Unit.GALLON_US, Unit.LITRE)
        assert result == Decimal("3.785411784")
        assert factor == Decimal("3.785411784")

    def test_litres_to_gallons(self) -> None:
        # 3.785411784 litres = 1 US gallon
        result, _ = convert(Decimal("3.785411784"), Unit.LITRE, Unit.GALLON_US)
        assert result == Decimal("1")

    def test_cubic_metres_to_litres(self) -> None:
        result, factor = convert(Decimal("1"), Unit.CUBIC_METRE, Unit.LITRE)
        assert result == Decimal("1000")
        assert factor == Decimal("1000")

    def test_litres_to_cubic_metres(self) -> None:
        result, _ = convert(Decimal("5000"), Unit.LITRE, Unit.CUBIC_METRE)
        assert result == Decimal("5")


class TestMassConversions:
    """Mass dimension conversions."""

    def test_tonne_to_kg(self) -> None:
        result, factor = convert(Decimal("1"), Unit.TONNE, Unit.KG)
        assert result == Decimal("1000")
        assert factor == Decimal("1000")

    def test_kg_to_tonne(self) -> None:
        result, _ = convert(Decimal("2500"), Unit.KG, Unit.TONNE)
        assert result == Decimal("2.5")


class TestEnergyConversions:
    """Energy dimension conversions."""

    def test_mwh_to_kwh(self) -> None:
        result, factor = convert(Decimal("1"), Unit.MWH, Unit.KWH)
        assert result == Decimal("1000")
        assert factor == Decimal("1000")

    def test_kwh_to_mwh(self) -> None:
        result, _ = convert(Decimal("50000"), Unit.KWH, Unit.MWH)
        assert result == Decimal("50")


class TestDistanceConversions:
    """Distance dimension conversions."""

    def test_miles_to_km(self) -> None:
        result, factor = convert(Decimal("1"), Unit.MILE, Unit.KILOMETRE)
        assert result == Decimal("1.609344")
        assert factor == Decimal("1.609344")

    def test_km_to_miles(self) -> None:
        result, _ = convert(Decimal("1.609344"), Unit.KILOMETRE, Unit.MILE)
        assert result == Decimal("1")


class TestIncompatibleConversions:
    """Conversions between different dimensions must raise errors."""

    def test_litre_to_kwh_raises(self) -> None:
        with pytest.raises(UnitConversionError, match="incompatible dimensions"):
            convert(Decimal("100"), Unit.LITRE, Unit.KWH)

    def test_kg_to_litre_raises(self) -> None:
        with pytest.raises(UnitConversionError, match="incompatible dimensions"):
            convert(Decimal("100"), Unit.KG, Unit.LITRE)

    def test_km_to_kwh_raises(self) -> None:
        with pytest.raises(UnitConversionError, match="incompatible dimensions"):
            convert(Decimal("100"), Unit.KILOMETRE, Unit.KWH)

    def test_tonne_to_mile_raises(self) -> None:
        with pytest.raises(UnitConversionError, match="incompatible dimensions"):
            convert(Decimal("1"), Unit.TONNE, Unit.MILE)


class TestCompatibilityCheck:
    """Test the are_compatible helper."""

    def test_same_unit(self) -> None:
        assert are_compatible(Unit.LITRE, Unit.LITRE) is True

    def test_same_dimension(self) -> None:
        assert are_compatible(Unit.LITRE, Unit.GALLON_US) is True
        assert are_compatible(Unit.KWH, Unit.MWH) is True

    def test_different_dimension(self) -> None:
        assert are_compatible(Unit.LITRE, Unit.KWH) is False
        assert are_compatible(Unit.KG, Unit.KILOMETRE) is False


class TestDecimalPrecision:
    """Verify that conversions use Decimal and avoid float drift."""

    def test_no_float_drift_gallons(self) -> None:
        """Float arithmetic: 1/3.785411784 often produces drift.
        Decimal should be exact when round-tripping."""
        litres, _ = convert(Decimal("1"), Unit.GALLON_US, Unit.LITRE)
        gallons_back, _ = convert(litres, Unit.LITRE, Unit.GALLON_US)
        assert gallons_back == Decimal("1")

    def test_large_quantity_precision(self) -> None:
        """Large quantity conversion should maintain precision."""
        result, _ = convert(Decimal("1000000"), Unit.LITRE, Unit.CUBIC_METRE)
        assert result == Decimal("1000")
