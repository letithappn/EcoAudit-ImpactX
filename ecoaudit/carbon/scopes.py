"""
GHG Protocol Scope and Category definitions.

Scopes and categories follow the GHG Protocol Corporate Standard:
- https://ghgprotocol.org/corporate-standard

Scope 1: Direct emissions from owned/controlled sources
Scope 2: Indirect emissions from purchased energy
Scope 3: Other indirect value-chain emissions

Categories are further sub-classifications within each scope.
"""

from enum import Enum


class Scope(Enum):
    """GHG Protocol emission scopes.

    Reference: GHG Protocol Corporate Accounting and Reporting Standard,
    Chapter 4: Setting Operational Boundaries.
    """

    SCOPE_1 = "Scope 1"
    SCOPE_2 = "Scope 2"
    SCOPE_3 = "Scope 3"

    def __str__(self) -> str:
        return self.value


class Category(Enum):
    """Emission source categories within each GHG Protocol scope.

    Scope 1 categories:
        - STATIONARY_COMBUSTION: Fuel burned in stationary equipment
          (boilers, furnaces, generators).
        - MOBILE_COMBUSTION: Fuel burned in company-owned/controlled
          vehicles (cars, trucks, forklifts).
        - FUGITIVE_EMISSIONS: Leaks of greenhouse gases
          (refrigerants, SF6, etc.).
        - PROCESS_EMISSIONS: Emissions from industrial processes
          (e.g., cement calcination, chemical reactions).

    Scope 2 categories:
        - PURCHASED_ELECTRICITY: Electricity purchased from the grid.
        - PURCHASED_HEAT_STEAM: Purchased heat, steam, or cooling.

    Scope 3 categories (subset for Phase 1):
        - PURCHASED_GOODS_SERVICES: Scope 3 Category 1.
        - UPSTREAM_TRANSPORTATION: Scope 3 Category 4.
        - WASTE_GENERATED: Scope 3 Category 5.
        - BUSINESS_TRAVEL: Scope 3 Category 6.
        - EMPLOYEE_COMMUTING: Scope 3 Category 7.

    Reference: GHG Protocol Corporate Value Chain (Scope 3) Standard.
    """

    # Scope 1
    STATIONARY_COMBUSTION = "Stationary Combustion"
    MOBILE_COMBUSTION = "Mobile Combustion"
    FUGITIVE_EMISSIONS = "Fugitive Emissions"
    PROCESS_EMISSIONS = "Process Emissions"

    # Scope 2
    PURCHASED_ELECTRICITY = "Purchased Electricity"
    PURCHASED_HEAT_STEAM = "Purchased Heat/Steam/Cooling"

    # Scope 3
    PURCHASED_GOODS_SERVICES = "Purchased Goods & Services"
    UPSTREAM_TRANSPORTATION = "Upstream Transportation & Distribution"
    WASTE_GENERATED = "Waste Generated in Operations"
    BUSINESS_TRAVEL = "Business Travel"
    EMPLOYEE_COMMUTING = "Employee Commuting"

    def __str__(self) -> str:
        return self.value


# Mapping: which categories are valid under each scope.
# This is the authoritative mapping for validation.
SCOPE_CATEGORIES: dict[Scope, frozenset[Category]] = {
    Scope.SCOPE_1: frozenset({
        Category.STATIONARY_COMBUSTION,
        Category.MOBILE_COMBUSTION,
        Category.FUGITIVE_EMISSIONS,
        Category.PROCESS_EMISSIONS,
    }),
    Scope.SCOPE_2: frozenset({
        Category.PURCHASED_ELECTRICITY,
        Category.PURCHASED_HEAT_STEAM,
    }),
    Scope.SCOPE_3: frozenset({
        Category.PURCHASED_GOODS_SERVICES,
        Category.UPSTREAM_TRANSPORTATION,
        Category.WASTE_GENERATED,
        Category.BUSINESS_TRAVEL,
        Category.EMPLOYEE_COMMUTING,
    }),
}


def get_scope_for_category(category: Category) -> Scope:
    """Return the scope that a category belongs to.

    Args:
        category: The emission category.

    Returns:
        The GHG Protocol scope.

    Raises:
        ValueError: If the category is not mapped to any scope.
    """
    for scope, categories in SCOPE_CATEGORIES.items():
        if category in categories:
            return scope
    raise ValueError(f"Category {category!r} is not mapped to any scope.")


def is_valid_scope_category(scope: Scope, category: Category) -> bool:
    """Check whether a category is valid under the given scope.

    Args:
        scope: The GHG Protocol scope.
        category: The emission category.

    Returns:
        True if the category belongs to the scope, False otherwise.
    """
    return category in SCOPE_CATEGORIES.get(scope, frozenset())
