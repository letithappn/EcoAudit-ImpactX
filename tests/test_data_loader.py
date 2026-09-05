"""
Tests for the JSON factor data loader.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from ecoaudit.carbon.data_loader import load_factors_from_json
from ecoaudit.carbon.factors import EmissionFactorRegistry
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit


@pytest.fixture
def sample_json_file(tmp_path: Path) -> Path:
    data = {
        "dataset_metadata": {
            "name": "Test Authority",
            "source_url": "http://example.com",
            "year": 2025,
            "version": "v1.0",
            "country": "Global",
            "methodology": "Test Method"
        },
        "factors": [
            {
                "factor_id": "TEST-JSON-001",
                "activity_type": "magic_fuel",
                "value": "1.234",
                "unit": "kgCO2e/litre",
                "per_unit": "litre",
                "scope": "Scope 1",
                "category": "Stationary Combustion",
                "gas_basis": "CO2E",
                "fuel_type_detail": "Liquid Magic",
                "dataset_name": "Magic Table"
            }
        ]
    }
    filepath = tmp_path / "test_factors.json"
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(data, f)
    return filepath


class TestDataLoader:
    def test_load_valid_json(self, sample_json_file: Path) -> None:
        registry = load_factors_from_json(sample_json_file, is_test_data=False)
        assert len(registry) == 1

        factor = registry.get_by_id("TEST-JSON-001")
        assert factor.activity_type == "magic_fuel"
        assert factor.value == Decimal("1.234")
        assert factor.per_unit == Unit.LITRE
        assert factor.scope == Scope.SCOPE_1
        assert factor.category == Category.STATIONARY_COMBUSTION
        
        # Provenance metadata inherited from dataset_metadata
        assert factor.source == "Test Authority"
        assert factor.source_url == "http://example.com"
        assert factor.year == 2025
        assert factor.version == "v1.0"
        assert factor.country == "Global"
        assert factor.methodology == "Test Method"
        
        # Factor specific metadata
        assert factor.gas_basis == "CO2E"
        assert factor.fuel_type_detail == "Liquid Magic"
        assert factor.dataset_name == "Magic Table"
        assert factor.is_test_data is False

    def test_load_into_existing_registry(self, sample_json_file: Path) -> None:
        registry = EmissionFactorRegistry()
        load_factors_from_json(sample_json_file, registry=registry)
        assert len(registry) == 1

    def test_load_invalid_schema_missing_keys(self, tmp_path: Path) -> None:
        bad_json = tmp_path / "bad.json"
        with bad_json.open("w", encoding="utf-8") as f:
            json.dump({"factors": []}, f)  # Missing dataset_metadata
            
        with pytest.raises(ValueError, match="Invalid JSON schema"):
            load_factors_from_json(bad_json)

    def test_load_invalid_enum_values(self, tmp_path: Path) -> None:
        data = {
            "dataset_metadata": {"name": "X", "year": 2025},
            "factors": [
                {
                    "factor_id": "F1",
                    "activity_type": "x",
                    "value": "1",
                    "unit": "x",
                    "per_unit": "BAD_UNIT",
                    "scope": "Scope 1",
                    "category": "Stationary Combustion"
                }
            ]
        }
        bad_json = tmp_path / "bad2.json"
        with bad_json.open("w", encoding="utf-8") as f:
            json.dump(data, f)
            
        with pytest.raises(ValueError, match="Unknown unit: BAD_UNIT"):
            load_factors_from_json(bad_json)
