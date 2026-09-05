"""Tests for data ingestion adapters."""

from decimal import Decimal
from pathlib import Path

import pytest

from ecoaudit.carbon.models import ActivityData
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.ingestion.adapters import (
    AustinFleetAdapter,
    ChicagoEnergyAdapter,
    SyntheticCompanyAdapter,
)


@pytest.fixture
def chicago_csv(tmp_path: Path) -> Path:
    csv = tmp_path / "chicago.csv"
    csv.write_text(
        "Data Year,ID,Property Name,Electricity Use (kBtu),Natural Gas Use (kBtu)\n"
        "2022,1,Prop A,100,200\n"
        "2022,2,Prop B,,300\n"  # Missing electricity
        "2022,3,Prop C,BAD,0\n"  # Bad electricity, zero gas
    )
    return csv


@pytest.fixture
def austin_csv(tmp_path: Path) -> Path:
    csv = tmp_path / "austin.csv"
    csv.write_text(
        "Transaction Date,Department,Fuel Type,Gallons\n"
        "2023-01-01,POLICE,Unleaded,10.5\n"
        "2023-01-02,FIRE,Diesel,50.0\n"
        "2023-01-03,PARKS,E-85,20.0\n"  # Unsupported fuel
        "2023-01-04,WATER,Unleaded,BAD\n" # Bad amount
    )
    return csv


@pytest.fixture
def synthetic_csv(tmp_path: Path) -> Path:
    csv = tmp_path / "synthetic.csv"
    csv.write_text(
        "Facility,Utility,Usage Amount,UOM,Date\n"
        "HQ,Electricity,100,kWh,2023-01-01\n"
        "HQ,Water,50,m3,2023-01-01\n"  # Ignored
        "Truck,Diesel,10,Liters,2023-01-01\n"
    )
    return csv


class TestChicagoEnergyAdapter:
    def test_normalize_extracts_electricity_and_gas(self, chicago_csv: Path) -> None:
        adapter = ChicagoEnergyAdapter()
        activities = list(adapter.normalize(str(chicago_csv)))

        # Prop A (Elec + Gas), Prop B (Gas only). Total 3 valid activities.
        assert len(activities) == 3

        a_elec = activities[0]
        assert a_elec.activity_id == "1-ELEC"
        assert a_elec.unit == Unit.KBTU
        assert a_elec.quantity == Decimal("100")
        assert a_elec.scope == Scope.SCOPE_2

        a_gas = activities[1]
        assert a_gas.activity_id == "1-GAS"
        assert a_gas.unit == Unit.KBTU
        assert a_gas.quantity == Decimal("200")
        assert a_gas.scope == Scope.SCOPE_1


class TestAustinFleetAdapter:
    def test_normalize_extracts_and_maps_fuels(self, austin_csv: Path) -> None:
        adapter = AustinFleetAdapter()
        activities = list(adapter.normalize(str(austin_csv)))

        # Unleaded and Diesel are extracted. E-85 and BAD are skipped.
        assert len(activities) == 2

        police = activities[0]
        assert police.metadata["activity_type"] == "petrol"
        assert police.quantity == Decimal("10.5")
        assert police.unit == Unit.GALLON_US
        assert police.scope == Scope.SCOPE_1
        assert police.category == Category.MOBILE_COMBUSTION

        fire = activities[1]
        assert fire.metadata["activity_type"] == "diesel"
        assert fire.quantity == Decimal("50.0")


class TestSyntheticCompanyAdapter:
    def test_normalize_messy_data(self, synthetic_csv: Path) -> None:
        adapter = SyntheticCompanyAdapter()
        activities = list(adapter.normalize(str(synthetic_csv)))

        # Elec and Diesel are extracted. Water is ignored.
        assert len(activities) == 2

        elec = activities[0]
        assert elec.unit == Unit.KWH
        assert elec.metadata["activity_type"] == "grid_electricity"
        assert elec.quantity == Decimal("100")

        diesel = activities[1]
        assert diesel.unit == Unit.LITRE
        assert diesel.metadata["activity_type"] == "diesel"
        assert diesel.category == Category.MOBILE_COMBUSTION  # because 'Truck' in facility
