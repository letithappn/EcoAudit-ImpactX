"""Deterministic CSV normalization for the AI boundary.

The classifier should receive a useful, explicit representation of a row,
but the original row must remain untouched for audit evidence.  This module
handles common CSV hygiene and expands known wide energy schemas into one
candidate per measurable activity without inventing quantities.
"""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


class CsvInputError(ValueError):
    """Raised when a CSV cannot be safely interpreted."""


@dataclass(frozen=True)
class PreparedRow:
    """A source row plus the deterministic view sent to the classifier."""

    source_row: int
    raw_row: dict[str, str]
    classification_row: dict[str, str]


def normalize_header(value: str) -> str:
    """Normalize a header for matching while preserving the original row."""
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lstrip("\ufeff").lower()).strip("_")


def parse_decimal(value: str | None) -> Decimal | None:
    """Parse common CSV number formats without guessing a missing value."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    cleaned = text.replace(",", "").replace(" ", "")
    if negative:
        cleaned = cleaned[1:-1]
    try:
        parsed = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None
    return -parsed if negative else parsed


def read_csv_rows(filepath: str | Path, max_rows: int | None = None) -> list[dict[str, str]]:
    """Read a CSV with BOM/encoding/whitespace handling and a row guard.

    Duplicate rows are retained: a duplicate may be a legitimate repeated
    measurement, and silently deduplicating would change the footprint.
    """
    limit = max_rows or int(os.getenv("ECOAUDIT_MAX_ROWS", "100000"))
    path = Path(filepath)
    last_error: UnicodeDecodeError | None = None

    for encoding in ("utf-8-sig", "cp1252"):
        try:
            rows: list[dict[str, str]] = []
            with path.open("r", encoding=encoding, newline="") as source:
                reader = csv.DictReader(source, skipinitialspace=True)
                if not reader.fieldnames:
                    raise CsvInputError("CSV must contain a header row")
                headers = [str(header or "").strip() for header in reader.fieldnames]
                if not any(headers):
                    raise CsvInputError("CSV header row is empty")

                for row in reader:
                    cleaned = {
                        headers[index]: str(value or "").strip()
                        for index, value in enumerate(row.values())
                        if index < len(headers) and headers[index]
                    }
                    if not any(cleaned.values()):
                        continue
                    rows.append(cleaned)
                    if len(rows) > limit:
                        raise CsvInputError(
                            f"CSV contains more than the configured {limit:,} row limit"
                        )
            return rows
        except UnicodeDecodeError as error:
            last_error = error
            continue

    raise CsvInputError("CSV encoding is not supported; use UTF-8 or Windows-1252") from last_error


_WIDE_ACTIVITY_FIELDS: tuple[tuple[str, str, str, str, str, str], ...] = (
    (
        "electricity_use_kbtu",
        "grid_electricity",
        "Scope 2",
        "Purchased Electricity",
        "Grid electricity consumption",
        "kBtu",
    ),
    (
        "natural_gas_use_kbtu",
        "natural_gas",
        "Scope 1",
        "Stationary Combustion",
        "Natural gas consumption",
        "kBtu",
    ),
    (
        "district_steam_use_kbtu",
        "unknown",
        "Scope 2",
        "Purchased Heat/Steam/Cooling",
        "District steam consumption is outside the current factor registry",
        "kBtu",
    ),
    (
        "district_chilled_water_use_kbtu",
        "unknown",
        "Scope 2",
        "Purchased Heat/Steam/Cooling",
        "District chilled water consumption is outside the current factor registry",
        "kBtu",
    ),
    (
        "all_other_fuel_use_kbtu",
        "unknown",
        "Scope 1",
        "Stationary Combustion",
        "Other fuel is outside the current supported activity taxonomy",
        "kBtu",
    ),
)


def _normalized_columns(row: dict[str, str]) -> dict[str, str]:
    return {normalize_header(key): value for key, value in row.items()}


def _canonical_row(
    row: dict[str, str],
    *,
    activity_type: str,
    quantity: str,
    unit: str,
    scope: str,
    category: str,
    description: str,
    reasoning: str,
) -> dict[str, str]:
    """Add explicit semantic fields without replacing source values."""
    prepared = dict(row)
    prepared.update(
        {
            "EcoAudit Activity Type": activity_type,
            "EcoAudit Quantity": quantity,
            "EcoAudit Unit": unit,
            "EcoAudit Scope": scope,
            "EcoAudit Category": category,
            "EcoAudit Description": description,
            "EcoAudit Reasoning": reasoning,
        }
    )
    return prepared


def prepare_row(row: dict[str, str], source_row: int) -> list[PreparedRow]:
    """Return one or more safe classifier inputs for a source row.

    Chicago's benchmarking export is a wide row with several independent
    energy columns.  Each positive, parseable quantity becomes a separate
    candidate.  Zero and blank values are omitted; malformed non-empty values
    become reviewable unknown candidates rather than being guessed.
    """
    normalized = _normalized_columns(row)
    wide_headers = {header for header, *_ in _WIDE_ACTIVITY_FIELDS}
    if wide_headers.intersection(normalized):
        prepared: list[PreparedRow] = []
        prop_name = row.get("Property Name") or row.get("Address") or ""
        prop_type = row.get("Primary Property Type") or ""
        building_context = f" - {prop_name}" if prop_name else ""
        if prop_type:
            building_context += f" ({prop_type})"

        for header, activity_type, scope, category, base_description, unit in _WIDE_ACTIVITY_FIELDS:
            if header not in normalized or not normalized[header]:
                continue
            raw_quantity = normalized[header]
            parsed = parse_decimal(raw_quantity)
            if parsed is not None and parsed == 0:
                continue
            quantity = str(parsed) if parsed is not None else raw_quantity
            is_supported = activity_type != "unknown"
            description = f"{base_description}{building_context}" if building_context else base_description
            reasoning = (
                f"Deterministically mapped from '{header}' for {prop_type or 'facility'} at {prop_name or 'site'}."
                if is_supported
                else base_description
            )
            prepared.append(
                PreparedRow(
                    source_row=source_row,
                    raw_row=row,
                    classification_row=_canonical_row(
                        row,
                        activity_type=activity_type,
                        quantity=quantity,
                        unit=unit,
                        scope=scope,
                        category=category,
                        description=description,
                        reasoning=reasoning,
                    ),
                )
            )
        if prepared:
            return prepared

        # The file has a recognized wide schema but no supported positive
        # activity quantity. Do not use the reported GHG total as an input.
        return [
            PreparedRow(
                source_row=source_row,
                raw_row=row,
                classification_row=_canonical_row(
                    row,
                    activity_type="unknown",
                    quantity="0",
                    unit="kBtu",
                    scope="Scope 1",
                    category="Stationary Combustion",
                    description="No supported positive activity quantity was supplied",
                    reasoning=(
                        "The row may contain reported GHG totals or non-supported energy fields, "
                        "but EcoAudit never treats a reported emissions total as an input quantity."
                    ),
                ),
            )
        ]

    quantity_aliases = (
        "usage_amount", "usage", "quantity", "qty", "amount", "value", "gallons",
        "volume", "consumption", "energy_qty", "energy_quantity", "fuel_used",
    )
    activity_aliases = (
        "utility", "utility_type", "fuel_type", "activity", "activity_type", "type",
        "energy_source", "description", "service_type",
    )
    unit_aliases = ("uom", "unit", "units", "measurement_unit")

    quantity_key = next((key for key in quantity_aliases if normalized.get(key)), None)
    activity_key = next((key for key in activity_aliases if normalized.get(key)), None)
    unit_key = next((key for key in unit_aliases if normalized.get(key)), None)
    facility = next(
        (normalized[key] for key in ("facility", "facility_name", "property_name", "site") if normalized.get(key)),
        "",
    )

    # Copy common aliases into the classifier view. Values remain sourced from
    # the input; this is only a deterministic column-name normalization.
    classification = dict(row)
    if quantity_key:
        raw_quantity = normalized[quantity_key]
        parsed_quantity = parse_decimal(raw_quantity)
        classification["Usage Amount"] = str(parsed_quantity) if parsed_quantity is not None else raw_quantity
    if activity_key:
        classification["Utility"] = normalized[activity_key]
    if unit_key:
        classification["UOM"] = normalized[unit_key]
    if facility:
        classification["Facility"] = facility

    return [PreparedRow(source_row=source_row, raw_row=row, classification_row=classification)]


def prepare_rows(rows: list[dict[str, str]]) -> list[PreparedRow]:
    """Prepare rows for callers that need the normalized view in one pass."""
    prepared: list[PreparedRow] = []
    for source_row, row in enumerate(rows, start=2):
        prepared.extend(prepare_row(row, source_row))
    return prepared
