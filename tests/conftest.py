"""
Shared test fixtures for EcoAudit carbon calculation tests.

All emission factors used in tests are explicitly labelled as
TEST/EXAMPLE DATA and carry is_test_data=True.

Factor values are derived from the DEFRA 2024 Condensed Set:
- Diesel (avg biofuel blend): 2.51210 kgCO2e/litre
- Petrol (avg biofuel blend): 2.16802 kgCO2e/litre
- UK electricity (generation): 0.20705 kgCO2e/kWh
"""

from decimal import Decimal

import pytest

from ecoaudit.carbon.factors import EmissionFactorRegistry, load_test_factors
from ecoaudit.carbon.models import ActivityData, EmissionFactor
from ecoaudit.carbon.scopes import Category, Scope
from ecoaudit.carbon.units import Unit
from ecoaudit.carbon.calculator import CarbonCalculator


@pytest.fixture
def registry() -> EmissionFactorRegistry:
    """A registry pre-loaded with test emission factors."""
    return load_test_factors()


@pytest.fixture
def calculator(registry: EmissionFactorRegistry) -> CarbonCalculator:
    """A CarbonCalculator initialized with test factors."""
    return CarbonCalculator(registry)


# ---- Reusable test emission factors ----

@pytest.fixture
def diesel_factor_2024() -> EmissionFactor:
    """DEFRA 2024 diesel factor (TEST DATA).

    Value: 2.51210 kgCO2e/litre (average biofuel blend).
    Source: UK DESNZ/DEFRA 2024 Condensed Set, Fuels worksheet.
    """
    return EmissionFactor(
        factor_id="TEST-DEFRA-2024-DIESEL-LITRE",
        activity_type="diesel",
        value=Decimal("2.51210"),
        unit="kgCO2e/litre",
        per_unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        country="UK",
        year=2024,
        source="UK DESNZ/DEFRA",
        source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        methodology="GHG Protocol / IPCC AR5 GWPs",
        version="DEFRA 2024 Condensed Set",
        gas_basis="CO2E",
        fuel_type_detail="Diesel (average biofuel blend)",
        dataset_name="Fuels",
        is_test_data=True,
    )


@pytest.fixture
def electricity_factor_uk() -> EmissionFactor:
    """DEFRA 2024 UK grid electricity factor (TEST DATA).

    Value: 0.20705 kgCO2e/kWh (location-based, generation only).
    Source: UK DESNZ/DEFRA 2024 Condensed Set, UK Electricity worksheet.
    """
    return EmissionFactor(
        factor_id="TEST-DEFRA-2024-ELEC-UK-KWH",
        activity_type="grid_electricity",
        value=Decimal("0.20705"),
        unit="kgCO2e/kWh",
        per_unit=Unit.KWH,
        scope=Scope.SCOPE_2,
        category=Category.PURCHASED_ELECTRICITY,
        country="UK",
        year=2024,
        source="UK DESNZ/DEFRA",
        source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        methodology="Location-based / GHG Protocol Scope 2 Guidance",
        version="DEFRA 2024 Condensed Set",
        gas_basis="CO2E",
        fuel_type_detail="UK Electricity (generation)",
        dataset_name="UK Electricity",
        is_test_data=True,
    )


@pytest.fixture
def petrol_factor_2024() -> EmissionFactor:
    """DEFRA 2024 petrol factor (TEST DATA).

    Value: 2.16802 kgCO2e/litre (average biofuel blend).
    Source: UK DESNZ/DEFRA 2024 Condensed Set, Fuels worksheet.
    """
    return EmissionFactor(
        factor_id="TEST-DEFRA-2024-PETROL-LITRE",
        activity_type="petrol",
        value=Decimal("2.16802"),
        unit="kgCO2e/litre",
        per_unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.MOBILE_COMBUSTION,
        country="UK",
        year=2024,
        source="UK DESNZ/DEFRA",
        source_url="https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024",
        methodology="GHG Protocol / IPCC AR5 GWPs",
        version="DEFRA 2024 Condensed Set",
        gas_basis="CO2E",
        fuel_type_detail="Petrol (average biofuel blend)",
        dataset_name="Fuels",
        is_test_data=True,
    )


# ---- Reusable test activities ----

@pytest.fixture
def diesel_activity() -> ActivityData:
    """10,000 litres of diesel in a factory generator."""
    return ActivityData(
        activity_id="ACT-001",
        description="Monthly diesel consumption - factory generator",
        quantity=Decimal("10000"),
        unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.STATIONARY_COMBUSTION,
        source_file="test_data.csv",
        source_row=1,
        metadata={"activity_type": "diesel", "department": "Operations"},
    )


@pytest.fixture
def electricity_activity() -> ActivityData:
    """50,000 kWh of purchased grid electricity."""
    return ActivityData(
        activity_id="ACT-002",
        description="Monthly electricity - main factory",
        quantity=Decimal("50000"),
        unit=Unit.KWH,
        scope=Scope.SCOPE_2,
        category=Category.PURCHASED_ELECTRICITY,
        source_file="test_data.csv",
        source_row=2,
        metadata={"activity_type": "grid_electricity"},
    )


@pytest.fixture
def petrol_activity() -> ActivityData:
    """2,000 litres of petrol for company vehicles."""
    return ActivityData(
        activity_id="ACT-003",
        description="Monthly petrol - company fleet",
        quantity=Decimal("2000"),
        unit=Unit.LITRE,
        scope=Scope.SCOPE_1,
        category=Category.MOBILE_COMBUSTION,
        source_file="test_data.csv",
        source_row=3,
        metadata={"activity_type": "petrol"},
    )
