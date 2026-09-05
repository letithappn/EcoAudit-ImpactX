"""
Specific dataset adapters for Phase 3 validation.
"""

import csv
from collections.abc import Iterator
from decimal import Decimal
from typing import Any

from ecoaudit.carbon.models import ActivityData
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


class ChicagoEnergyAdapter:
    """Adapter for the Chicago Energy Benchmarking dataset.

    Extracts:
    - Electricity Use (kBtu) -> Scope 2, Purchased Electricity
    - Natural Gas Use (kBtu) -> Scope 1, Stationary Combustion
    """

    def normalize(self, filepath: str) -> Iterator[ActivityData]:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2): # 1-based, header is 1
                property_id = row.get("ID", f"ROW-{row_idx}")
                property_name = row.get("Property Name", "Unknown Facility")
                
                # Parse Electricity
                elec_kbtu = self._parse_decimal(row.get("Electricity Use (kBtu)"))
                if elec_kbtu and elec_kbtu > 0:
                    yield ActivityData(
                        activity_id=f"{property_id}-ELEC",
                        description=f"{property_name} - Electricity",
                        quantity=elec_kbtu,
                        unit=Unit.KBTU,
                        scope=Scope.SCOPE_2,
                        category=Category.PURCHASED_ELECTRICITY,
                        source_file=filepath,
                        source_row=row_idx,
                        metadata={"activity_type": "grid_electricity"}
                    )

                # Parse Natural Gas
                gas_kbtu = self._parse_decimal(row.get("Natural Gas Use (kBtu)"))
                if gas_kbtu and gas_kbtu > 0:
                    yield ActivityData(
                        activity_id=f"{property_id}-GAS",
                        description=f"{property_name} - Natural Gas",
                        quantity=gas_kbtu,
                        unit=Unit.KBTU,
                        scope=Scope.SCOPE_1,
                        category=Category.STATIONARY_COMBUSTION,
                        source_file=filepath,
                        source_row=row_idx,
                        metadata={"activity_type": "natural_gas"}
                    )

    def _parse_decimal(self, value: str | None) -> Decimal | None:
        if not value:
            return None
        try:
            return Decimal(value.strip())
        except Exception:
            return None


class AustinFleetAdapter:
    """Adapter for the City of Austin Fleet Fuel dataset.

    Extracts:
    - Fuel Type (mapped to 'petrol' or 'diesel') -> Scope 1, Mobile Combustion
    - Gallons -> Volume
    """

    def normalize(self, filepath: str) -> Iterator[ActivityData]:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2):
                fuel_str = row.get("Fuel Type", "").strip().lower()
                gallons_str = row.get("Gallons", "").strip()
                department = row.get("Department", "Unknown Dept")
                date = row.get("Transaction Date", "Unknown Date")

                # Map fuel type to our taxonomy
                activity_type = self._map_fuel_type(fuel_str)
                if not activity_type:
                    continue  # Skip unsupported fuels (e.g. E-85, Propane)

                gallons = self._parse_decimal(gallons_str)
                if gallons and gallons > 0:
                    yield ActivityData(
                        activity_id=f"FLEET-{row_idx}",
                        description=f"{department} Fleet Fuel - {date}",
                        quantity=gallons,
                        unit=Unit.GALLON_US,
                        scope=Scope.SCOPE_1,
                        category=Category.MOBILE_COMBUSTION,
                        source_file=filepath,
                        source_row=row_idx,
                        metadata={"activity_type": activity_type, "department": department}
                    )

    def _map_fuel_type(self, fuel_str: str) -> str | None:
        if "unleaded" in fuel_str or "gasoline" in fuel_str:
            return "petrol"
        if "diesel" in fuel_str:
            return "diesel"
        return None

    def _parse_decimal(self, value: str | None) -> Decimal | None:
        if not value:
            return None
        try:
            return Decimal(value.strip())
        except Exception:
            return None


class SyntheticCompanyAdapter:
    """Adapter for messy corporate data (simulation)."""

    def normalize(self, filepath: str) -> Iterator[ActivityData]:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2):
                facility = row.get("Facility", "Unknown")
                utility = row.get("Utility", "").lower()
                usage_str = row.get("Usage Amount", "")
                uom_str = row.get("UOM", "").lower()

                usage = self._parse_decimal(usage_str)
                if not usage or usage <= 0:
                    continue

                # Ad-hoc mapping logic (what an AI would normally do better)
                if "electricity" in utility or "power" in utility:
                    yield ActivityData(
                        activity_id=f"SYN-{row_idx}",
                        description=f"{facility} - {utility}",
                        quantity=usage,
                        unit=Unit.KWH if "kwh" in uom_str else Unit.MWH,
                        scope=Scope.SCOPE_2,
                        category=Category.PURCHASED_ELECTRICITY,
                        source_file=filepath,
                        source_row=row_idx,
                        metadata={"activity_type": "grid_electricity"}
                    )
                elif "diesel" in utility:
                    yield ActivityData(
                        activity_id=f"SYN-{row_idx}",
                        description=f"{facility} - {utility}",
                        quantity=usage,
                        unit=Unit.LITRE if "liter" in uom_str else Unit.GALLON_US,
                        scope=Scope.SCOPE_1,
                        category=Category.MOBILE_COMBUSTION if "truck" in facility.lower() else Category.STATIONARY_COMBUSTION,
                        source_file=filepath,
                        source_row=row_idx,
                        metadata={"activity_type": "diesel"}
                    )
                elif "petrol" in utility or "gasoline" in utility:
                    yield ActivityData(
                        activity_id=f"SYN-{row_idx}",
                        description=f"{facility} - {utility}",
                        quantity=usage,
                        unit=Unit.LITRE if "liter" in uom_str else Unit.GALLON_US,
                        scope=Scope.SCOPE_1,
                        category=Category.MOBILE_COMBUSTION,
                        source_file=filepath,
                        source_row=row_idx,
                        metadata={"activity_type": "petrol"}
                    )
                # Ignore water or unknown utilities deterministically

    def _parse_decimal(self, value: str | None) -> Decimal | None:
        if not value:
            return None
        try:
            return Decimal(value.strip())
        except Exception:
            return None
