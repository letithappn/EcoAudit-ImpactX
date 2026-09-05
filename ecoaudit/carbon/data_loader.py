"""
JSON Factor Data Loader.

Loads production emission factors from JSON files into the EmissionFactorRegistry.
This allows separating code from authoritative factor datasets.
"""

import json
import logging
from decimal import Decimal
from pathlib import Path

from ecoaudit.carbon.factors import EmissionFactorRegistry
from ecoaudit.carbon.models import EmissionFactor
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.carbon.validation import validate_factor

logger = logging.getLogger(__name__)


def _parse_scope(scope_str: str) -> Scope:
    """Parse a scope string into a Scope enum."""
    for s in Scope:
        if s.value.lower() == scope_str.lower():
            return s
    raise ValueError(f"Unknown scope: {scope_str}")


def _parse_category(category_str: str) -> Category:
    """Parse a category string into a Category enum."""
    for c in Category:
        if c.value.lower() == category_str.lower():
            return c
    raise ValueError(f"Unknown category: {category_str}")


def _parse_unit(unit_str: str) -> Unit:
    """Parse a unit string into a Unit enum."""
    for u in Unit:
        if u.value.lower() == unit_str.lower():
            return u
    raise ValueError(f"Unknown unit: {unit_str}")


def load_factors_from_json(
    filepath: str | Path,
    registry: EmissionFactorRegistry | None = None,
    is_test_data: bool = False,
) -> EmissionFactorRegistry:
    """Load emission factors from a JSON dataset file into a registry.

    Args:
        filepath: Path to the JSON file.
        registry: An existing registry to populate, or None to create a new one.
        is_test_data: Whether to flag the loaded factors as test data.
            If loading an authoritative production dataset, this must be False.

    Returns:
        The populated EmissionFactorRegistry.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the JSON file is invalid.
        ValueError: If the JSON schema is invalid or missing required fields.
        ValidationError: If any factor fails validation.
    """
    if registry is None:
        registry = EmissionFactorRegistry()

    path = Path(filepath)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "dataset_metadata" not in data or "factors" not in data:
        raise ValueError("Invalid JSON schema: missing 'dataset_metadata' or 'factors'.")

    meta = data["dataset_metadata"]
    source = meta.get("name", "Unknown Source")
    source_url = meta.get("source_url", "")
    default_year = meta.get("year", 0)
    default_version = meta.get("version", "Unknown Version")
    default_country = meta.get("country", "Unknown")
    methodology = meta.get("methodology", "Unknown Methodology")

    for f_data in data["factors"]:
        # Allow factor-level overrides for year, country, etc.
        year = f_data.get("year", default_year)
        version = f_data.get("version", default_version)
        country = f_data.get("country", default_country)
        source_override = f_data.get("source", source)

        factor = EmissionFactor(
            factor_id=f_data["factor_id"],
            activity_type=f_data["activity_type"],
            value=Decimal(str(f_data["value"])),
            unit=f_data["unit"],
            per_unit=_parse_unit(f_data["per_unit"]),
            scope=_parse_scope(f_data["scope"]),
            category=_parse_category(f_data["category"]),
            country=country,
            year=year,
            source=source_override,
            source_url=source_url,
            methodology=methodology,
            version=version,
            gas_basis=f_data.get("gas_basis", "CO2E"),
            fuel_type_detail=f_data.get("fuel_type_detail", ""),
            dataset_name=f_data.get("dataset_name", ""),
            applicability_notes=f_data.get("applicability_notes", ""),
            is_test_data=is_test_data,
        )

        validate_factor(factor)
        registry.register(factor)

    logger.info(
        "Loaded %d factors from %s into registry.",
        len(data["factors"]),
        path.name,
    )

    return registry
