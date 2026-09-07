"""
Mock AI provider for deterministic testing and evaluation.

This provider returns pre-programmed classifications based on keyword
matching. It does NOT use an LLM — it simulates what a well-behaved
LLM would return for known inputs.

Purpose:
1. Test the full pipeline without API calls
2. Provide a deterministic baseline for comparison
3. Allow development of evaluation scripts before real API integration
"""

from __future__ import annotations

from ecoaudit.ai.schemas import ActivityCandidate


class MockClassifier:
    """Deterministic mock classifier for testing.

    Uses keyword matching on the raw row values to produce classifications.
    This intentionally mimics what the real LLM should produce, allowing
    us to test the full pipeline architecture.
    """

    def classify_row(
        self,
        raw_row: dict[str, str],
        source_row: int | None = None,
    ) -> ActivityCandidate:
        """Classify a single raw data row using keyword matching."""
        # Combine all values into a single searchable string
        combined = " ".join(str(v) for v in raw_row.values()).lower()
        raw_input = " | ".join(f"{k}: {v}" for k, v in raw_row.items())

        # Extract quantity from common column names
        quantity = self._extract_quantity(raw_row)

        # Extract unit from common column names
        unit = self._extract_unit(raw_row, combined)

        # Classify based on keywords
        if any(kw in combined for kw in ["electricity", "electric", "power bill", "grid"]):
            return ActivityCandidate(
                activity_type="grid_electricity",
                quantity=quantity,
                unit=unit or "kWh",
                scope="Scope 2",
                category="Purchased Electricity",
                description=self._build_description(raw_row, "Grid electricity consumption"),
                confidence=0.95,
                reasoning="Keywords indicate purchased electricity from the grid.",
                needs_review=False,
                source_row=source_row,
                raw_input=raw_input,
            )

        if any(kw in combined for kw in ["natural gas", "gas heating", "gas boiler", "lng"]):
            return ActivityCandidate(
                activity_type="natural_gas",
                quantity=quantity,
                unit=unit or "kWh",
                scope="Scope 1",
                category="Stationary Combustion",
                description=self._build_description(raw_row, "Natural gas consumption"),
                confidence=0.92,
                reasoning="Keywords indicate natural gas combustion for heating/industrial use.",
                needs_review=False,
                source_row=source_row,
                raw_input=raw_input,
            )

        if any(kw in combined for kw in ["diesel gen", "diesel generator", "diesel boiler", "diesel furnace"]):
            return ActivityCandidate(
                activity_type="diesel",
                quantity=quantity,
                unit=unit or "litre",
                scope="Scope 1",
                category="Stationary Combustion",
                description=self._build_description(raw_row, "Diesel stationary combustion"),
                confidence=0.93,
                reasoning="Diesel generator/boiler indicates stationary combustion.",
                needs_review=False,
                source_row=source_row,
                raw_input=raw_input,
            )

        if any(kw in combined for kw in ["fleet", "truck", "vehicle", "car ", "van ", "delivery"]):
            # Check fuel type within the vehicle context
            if "petrol" in combined or "gasoline" in combined or "unleaded" in combined:
                fuel = "petrol"
            else:
                fuel = "diesel"  # Default for commercial fleets

            return ActivityCandidate(
                activity_type=fuel,
                quantity=quantity,
                unit=unit or "litre",
                scope="Scope 1",
                category="Mobile Combustion",
                description=self._build_description(raw_row, f"Vehicle {fuel} consumption"),
                confidence=0.85 if "petrol" in combined or "diesel" in combined else 0.65,
                reasoning=f"Vehicle/fleet context indicates mobile combustion with {fuel}.",
                needs_review="petrol" not in combined and "diesel" not in combined,
                source_row=source_row,
                raw_input=raw_input,
            )

        if "diesel" in combined:
            return ActivityCandidate(
                activity_type="diesel",
                quantity=quantity,
                unit=unit or "litre",
                scope="Scope 1",
                category="Stationary Combustion",
                description=self._build_description(raw_row, "Diesel fuel consumption"),
                confidence=0.80,
                reasoning="Diesel mentioned without clear mobile/stationary context. Defaulting to stationary.",
                needs_review=True,
                source_row=source_row,
                raw_input=raw_input,
            )

        if "petrol" in combined or "gasoline" in combined:
            return ActivityCandidate(
                activity_type="petrol",
                quantity=quantity,
                unit=unit or "litre",
                scope="Scope 1",
                category="Mobile Combustion",
                description=self._build_description(raw_row, "Petrol fuel consumption"),
                confidence=0.85,
                reasoning="Petrol/gasoline typically indicates vehicle fuel.",
                needs_review=False,
                source_row=source_row,
                raw_input=raw_input,
            )

        if "gas" in combined and "natural" not in combined:
            # Ambiguous "gas" — could be natural gas or something else
            return ActivityCandidate(
                activity_type="natural_gas",
                quantity=quantity,
                unit=unit or "m3",
                scope="Scope 1",
                category="Stationary Combustion",
                description=self._build_description(raw_row, "Gas consumption (assumed natural gas)"),
                confidence=0.60,
                reasoning="'Gas' mentioned without 'natural' qualifier. Assumed natural gas but uncertain.",
                needs_review=True,
                source_row=source_row,
                raw_input=raw_input,
            )

        # Unknown / unclassifiable
        if any(kw in combined for kw in ["water", "waste", "sewage", "recycling"]):
            return ActivityCandidate(
                activity_type="unknown",
                quantity=quantity,
                unit=unit or "m3",
                scope="Scope 1",
                category="Stationary Combustion",
                description=self._build_description(raw_row, "Non-GHG utility"),
                confidence=0.10,
                reasoning="Water/waste is not a direct GHG emission source in standard carbon accounting.",
                needs_review=True,
                source_row=source_row,
                raw_input=raw_input,
            )

        return ActivityCandidate(
            activity_type="unknown",
            quantity=quantity,
            unit=unit or "kWh",
            scope="Scope 1",
            category="Stationary Combustion",
            description=self._build_description(raw_row, "Unclassified activity"),
            confidence=0.05,
            reasoning="Could not determine the activity type from the available information.",
            needs_review=True,
            source_row=source_row,
            raw_input=raw_input,
        )

    def generate_structured(self, prompt: str) -> dict[str, Any] | list[dict[str, Any]]:
        # Used for testing recommendation candidates
        # Returns a dummy candidate proposal
        return {
            "recommendations": [
                {
                    "title": "Mock 10% Reduction",
                    "target_hotspot": "Stationary Combustion",
                    "intervention_type": "PercentageReduction",
                    "target_activity_ids": ["ACT-TEST"],
                    "parameters": {"reduction_percentage": "10"},
                    "rationale": "Testing rationale",
                    "needs_review": False
                }
            ]
        }

    def generate_text(self, prompt: str) -> str:
        # Used for testing recommendation explanation
        return "This is a mock AI explanation of the deterministic scenario result."

    def classify_batch(
        self,
        raw_rows: list[dict[str, str]],
        start_row: int = 2,
    ) -> list[ActivityCandidate]:
        """Classify multiple rows by calling classify_row in a loop."""
        return [
            self.classify_row(row, source_row=start_row + i)
            for i, row in enumerate(raw_rows)
        ]

    def _extract_quantity(self, raw_row: dict[str, str]) -> str:
        """Try to extract a numeric quantity from common column names."""
        quantity_columns = [
            "Usage Amount", "usage_amount", "UsageAmount", "Usage", "usage",
            "Quantity", "quantity", "Amount", "amount", "Value", "value", 
            "Gallons", "gallons", "Volume", "volume", "Consumption", "consumption",
        ]
        for col in quantity_columns:
            if col in raw_row and raw_row[col].strip():
                return raw_row[col].strip()
        return "0"

    def _extract_unit(self, raw_row: dict[str, str], combined: str) -> str | None:
        """Try to extract a unit string from common column names."""
        unit_columns = ["UOM", "uom", "Unit", "unit", "Units", "units"]
        for col in unit_columns:
            if col in raw_row and raw_row[col].strip():
                raw_unit = raw_row[col].strip().lower()
                # Normalize common variations
                unit_map = {
                    "kwh": "kWh", "mwh": "MWh", "kbtu": "kBtu",
                    "liters": "litre", "litres": "litre", "liter": "litre",
                    "l": "litre", "gallons": "gallon_us", "gal": "gallon_us",
                    "m3": "m3", "kg": "kg", "tonne": "tonne", "tonnes": "tonne",
                    "km": "km", "miles": "mile", "mile": "mile",
                }
                return unit_map.get(raw_unit, raw_unit)
        return None

    def _build_description(self, raw_row: dict[str, str], suffix: str) -> str:
        """Build a normalized description from the raw row."""
        facility = raw_row.get("Facility", raw_row.get("facility", ""))
        utility = raw_row.get("Utility", raw_row.get("utility", ""))
        if facility and utility:
            return f"{facility} - {suffix}"
        if facility:
            return f"{facility} - {suffix}"
        return suffix
