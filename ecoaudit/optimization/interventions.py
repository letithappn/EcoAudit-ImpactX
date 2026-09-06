"""
Intervention implementations for the Scenario Engine.

An intervention deterministically modifies an ActivityData record
to represent a scenario change.
"""

from __future__ import annotations

import copy
from decimal import Decimal

from ecoaudit.carbon.models import ActivityData
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


_ZERO = Decimal("0")
_HUNDRED = Decimal("100")


class PercentageReduction:
    """Reduces the quantity of an activity by a given percentage.

    Example: "Reduce diesel usage by 20%."
    """

    def __init__(self, reduction_percentage: Decimal) -> None:
        """Initialize the intervention.

        Args:
            reduction_percentage: The percentage to reduce by (0 to 100).
                E.g., Decimal("20") means a 20% reduction.
        """
        if reduction_percentage < _ZERO or reduction_percentage > _HUNDRED:
            raise ValueError(f"Reduction percentage must be between 0 and 100, got {reduction_percentage}")
        self.reduction_percentage = reduction_percentage

    @property
    def intervention_type(self) -> str:
        return "PercentageReduction"

    def apply(self, activity: ActivityData) -> ActivityData:
        multiplier = (_HUNDRED - self.reduction_percentage) / _HUNDRED
        new_quantity = activity.quantity * multiplier
        
        # Determine scenario cost if unit price exists
        new_meta = copy.deepcopy(activity.metadata) if activity.metadata else {}
        if "total_cost" in new_meta:
            # Scale total cost down proportionally
            old_cost = Decimal(str(new_meta["total_cost"]))
            new_meta["total_cost"] = old_cost * multiplier

        return ActivityData(
            activity_id=f"{activity.activity_id}-SCENARIO",
            description=f"{activity.description} (Scenario: -{self.reduction_percentage}%)",
            quantity=new_quantity,
            unit=activity.unit,
            scope=activity.scope,
            category=activity.category,
            source_file=activity.source_file,
            source_row=activity.source_row,
            metadata=new_meta,
        )

    def get_assumptions(self) -> tuple[str, ...]:
        return (
            f"Activity volume is reduced by exactly {self.reduction_percentage}%.",
            "Costs scale perfectly linearly with volume reduction.",
        )


class AbsoluteReduction:
    """Reduces the quantity of an activity by an absolute amount.

    Example: "Reduce diesel usage by 1,000 litres."
    """

    def __init__(self, reduction_amount: Decimal) -> None:
        """Initialize the intervention.

        Args:
            reduction_amount: The absolute amount to reduce. Must be >= 0.
        """
        if reduction_amount < _ZERO:
            raise ValueError(f"Reduction amount cannot be negative, got {reduction_amount}")
        self.reduction_amount = reduction_amount

    @property
    def intervention_type(self) -> str:
        return "AbsoluteReduction"

    def apply(self, activity: ActivityData) -> ActivityData:
        new_quantity = activity.quantity - self.reduction_amount
        if new_quantity < _ZERO:
            new_quantity = _ZERO  # Cannot reduce below zero

        multiplier = _ZERO
        if activity.quantity > _ZERO:
            multiplier = new_quantity / activity.quantity

        new_meta = copy.deepcopy(activity.metadata) if activity.metadata else {}
        if "total_cost" in new_meta:
            old_cost = Decimal(str(new_meta["total_cost"]))
            new_meta["total_cost"] = old_cost * multiplier

        return ActivityData(
            activity_id=f"{activity.activity_id}-SCENARIO",
            description=f"{activity.description} (Scenario: -{self.reduction_amount} {activity.unit.value})",
            quantity=new_quantity,
            unit=activity.unit,
            scope=activity.scope,
            category=activity.category,
            source_file=activity.source_file,
            source_row=activity.source_row,
            metadata=new_meta,
        )

    def get_assumptions(self) -> tuple[str, ...]:
        return (
            f"Activity volume is reduced by exactly {self.reduction_amount} units.",
            "If reduction exceeds current volume, volume becomes exactly 0.",
            "Costs scale perfectly linearly with volume reduction.",
        )


class FuelSubstitution:
    """Substitutes one fuel/activity type for another.

    Example: "Switch from diesel to grid_electricity."
    This requires explicit conversion factors if the unit changes.
    """

    def __init__(
        self,
        new_activity_type: str,
        new_unit: Unit,
        new_scope: Scope,
        new_category: Category,
        conversion_multiplier: Decimal = Decimal("1"),
        new_unit_price: Decimal | None = None,
    ) -> None:
        """Initialize the intervention.

        Args:
            new_activity_type: The new activity type (e.g., "grid_electricity").
            new_unit: The new unit (e.g., Unit.KWH).
            new_scope: The new scope (e.g., Scope.SCOPE_2).
            new_category: The new category (e.g., Category.PURCHASED_ELECTRICITY).
            conversion_multiplier: How many new units equal one old unit.
                E.g., if switching from Diesel (Litres) to Electricity (kWh),
                and 1 Litre Diesel contains ~10 kWh energy, multiplier is 10.
            new_unit_price: Optional unit price for the new fuel, to compute financial impact.
        """
        self.new_activity_type = new_activity_type
        self.new_unit = new_unit
        self.new_scope = new_scope
        self.new_category = new_category
        self.conversion_multiplier = conversion_multiplier
        self.new_unit_price = new_unit_price

    @property
    def intervention_type(self) -> str:
        return "FuelSubstitution"

    def apply(self, activity: ActivityData) -> ActivityData:
        new_quantity = activity.quantity * self.conversion_multiplier
        
        new_meta = copy.deepcopy(activity.metadata) if activity.metadata else {}
        new_meta["activity_type"] = self.new_activity_type
        
        if self.new_unit_price is not None:
            new_meta["total_cost"] = new_quantity * self.new_unit_price
        else:
            # If we don't have a new unit price, we must wipe out old total_cost
            # because the cost is no longer valid for the new fuel.
            new_meta.pop("total_cost", None)
            new_meta.pop("unit_price", None)

        old_type = activity.metadata.get("activity_type", "unknown") if activity.metadata else "unknown"

        return ActivityData(
            activity_id=f"{activity.activity_id}-SCENARIO",
            description=f"{activity.description} (Scenario: {old_type} -> {self.new_activity_type})",
            quantity=new_quantity,
            unit=self.new_unit,
            scope=self.new_scope,
            category=self.new_category,
            source_file=activity.source_file,
            source_row=activity.source_row,
            metadata=new_meta,
        )

    def get_assumptions(self) -> tuple[str, ...]:
        assumptions = [
            f"1 original unit is equivalent to {self.conversion_multiplier} new units ({self.new_unit.value})."
        ]
        if self.new_unit_price is not None:
            assumptions.append(f"New fuel unit price is assumed to be {self.new_unit_price}.")
        else:
            assumptions.append("No new fuel price provided; financial impact will be unavailable.")
        return tuple(assumptions)
