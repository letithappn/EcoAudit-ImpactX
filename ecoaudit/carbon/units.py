"""
Unit definitions and deterministic conversion engine.

All conversion factors are stored as Decimal values to ensure
deterministic, reproducible arithmetic with no floating-point drift.

Units are grouped into dimension families (volume, mass, energy, distance).
Conversion is only permitted within the same dimension family.
"""

from decimal import Decimal
from enum import Enum


class UnitConversionError(Exception):
    """Raised when a unit conversion is impossible (incompatible dimensions)."""


class Unit(Enum):
    """Physical units relevant to carbon accounting.

    Each unit belongs to a dimension family:
    - VOLUME: litre, gallon_us, cubic_metre
    - MASS: kg, tonne
    - ENERGY: kWh, MWh
    - DISTANCE: km, mile
    """

    # Volume
    LITRE = "litre"
    GALLON_US = "gallon_us"
    CUBIC_METRE = "m3"

    # Mass
    KG = "kg"
    TONNE = "tonne"

    # Energy
    KWH = "kWh"
    MWH = "MWh"
    KBTU = "kBtu"

    # Distance
    KILOMETRE = "km"
    MILE = "mile"

    def __str__(self) -> str:
        return self.value


# ----- Dimension families -----
# Each dimension maps unit → conversion factor to the base unit of that
# dimension. The base unit has a factor of Decimal("1").

_VOLUME_BASE = Unit.LITRE
_VOLUME_FACTORS: dict[Unit, Decimal] = {
    Unit.LITRE: Decimal("1"),
    # 1 US gallon = 3.785411784 litres (exact US definition)
    Unit.GALLON_US: Decimal("3.785411784"),
    # 1 cubic metre = 1000 litres
    Unit.CUBIC_METRE: Decimal("1000"),
}

_MASS_BASE = Unit.KG
_MASS_FACTORS: dict[Unit, Decimal] = {
    Unit.KG: Decimal("1"),
    Unit.TONNE: Decimal("1000"),
}

_ENERGY_BASE = Unit.KWH
_ENERGY_FACTORS: dict[Unit, Decimal] = {
    Unit.KWH: Decimal("1"),
    Unit.MWH: Decimal("1000"),
    # 1 kBtu = 0.293071 kWh (standard international conversion)
    Unit.KBTU: Decimal("0.293071"),
}

_DISTANCE_BASE = Unit.KILOMETRE
_DISTANCE_FACTORS: dict[Unit, Decimal] = {
    Unit.KILOMETRE: Decimal("1"),
    # 1 mile = 1.609344 km (exact international definition)
    Unit.MILE: Decimal("1.609344"),
}

# Collect all dimension families for lookup.
_DIMENSION_FAMILIES: list[dict[Unit, Decimal]] = [
    _VOLUME_FACTORS,
    _MASS_FACTORS,
    _ENERGY_FACTORS,
    _DISTANCE_FACTORS,
]


def _get_family(unit: Unit) -> dict[Unit, Decimal]:
    """Return the dimension family that contains the given unit.

    Raises:
        UnitConversionError: If the unit is not in any known family.
    """
    for family in _DIMENSION_FAMILIES:
        if unit in family:
            return family
    raise UnitConversionError(f"Unit {unit!r} is not in any known dimension family.")


def convert(
    quantity: Decimal,
    from_unit: Unit,
    to_unit: Unit,
) -> tuple[Decimal, Decimal]:
    """Convert a quantity between units of the same dimension.

    The conversion is performed via the base unit of the dimension:
        result = quantity × (from_factor / to_factor)

    Args:
        quantity: The numeric value to convert.
        from_unit: The source unit.
        to_unit: The target unit.

    Returns:
        A tuple of (converted_quantity, conversion_factor_applied).
        The conversion_factor is from_factor / to_factor so that:
            converted_quantity == quantity × conversion_factor

    Raises:
        UnitConversionError: If from_unit and to_unit are in different
            dimension families (e.g., litres → kWh).
    """
    if from_unit == to_unit:
        return quantity, Decimal("1")

    from_family = _get_family(from_unit)
    to_family = _get_family(to_unit)

    if from_family is not to_family:
        raise UnitConversionError(
            f"Cannot convert between {from_unit.value} and {to_unit.value}: "
            f"incompatible dimensions."
        )

    from_to_base = from_family[from_unit]
    to_to_base = to_family[to_unit]

    conversion_factor = from_to_base / to_to_base
    converted = quantity * conversion_factor

    return converted, conversion_factor


def are_compatible(unit_a: Unit, unit_b: Unit) -> bool:
    """Check whether two units belong to the same dimension family.

    Args:
        unit_a: First unit.
        unit_b: Second unit.

    Returns:
        True if they can be converted to each other, False otherwise.
    """
    if unit_a == unit_b:
        return True
    try:
        family_a = _get_family(unit_a)
        family_b = _get_family(unit_b)
        return family_a is family_b
    except UnitConversionError:
        return False
