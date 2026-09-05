"""
EcoAudit Carbon Calculation Sub-package.

Provides the deterministic carbon calculation engine including:
- Domain models (ActivityData, EmissionFactor, CalculationResult)
- Scope & category classification (GHG Protocol)
- Unit conversion
- Emission factor registry
- Validation
- Calculation engine with full audit trace
"""

from ecoaudit.carbon.models import (
    ActivityData,
    CalculationResult,
    CalculationTrace,
    EmissionFactor,
)
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit

__all__ = [
    "ActivityData",
    "CalculationResult",
    "CalculationTrace",
    "EmissionFactor",
    "Category",
    "Scope",
    "Unit",
]
