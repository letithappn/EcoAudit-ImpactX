-- =============================================================================
-- EcoAudit AI / Enterprise Carbon Accounting Platform for Egypt
-- Migration 002: Versioned Emission Factors, Grid Baselines & Fuel Specifications
-- Standards: EEAA National Inventory, NREA, EGPC & IPCC AR5/AR6 GWP Frameworks
-- =============================================================================

-- 1. Factor Authoritative Sources
CREATE TABLE factor_sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_code VARCHAR(100) UNIQUE NOT NULL, -- 'EEAA', 'NREA', 'EGPC', 'DEFRA_2024', 'IEA_2024', 'IPCC_AR5'
    name VARCHAR(255) NOT NULL,
    issuing_body VARCHAR(255) NOT NULL,
    publication_year INT NOT NULL,
    methodology_url TEXT,
    is_official_regulatory_source BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Version-Controlled Emission Factor Library
CREATE TABLE emission_factors (
    factor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    factor_code VARCHAR(100) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    name VARCHAR(255) NOT NULL,
    scope VARCHAR(20) NOT NULL CHECK (scope IN ('Scope 1', 'Scope 2', 'Scope 3')),
    category VARCHAR(100) NOT NULL, -- 'Electricity', 'Stationary_Combustion', 'Mobile_Combustion', 'Purchased_Goods', 'Freight_Transport'
    fuel_or_activity_type VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL, -- 'kWh', 'MWh', 'L', 'm3', 'Ton', 'tonne-km', 'km'
    co2e_factor NUMERIC(14, 6) NOT NULL, -- Metric tons CO2e per unit or kg CO2e per unit
    factor_unit_denominator VARCHAR(50) NOT NULL DEFAULT 'per_unit',
    co2_factor NUMERIC(14, 6),
    ch4_factor NUMERIC(14, 6),
    n2o_factor NUMERIC(14, 6),
    gwp_framework VARCHAR(20) NOT NULL DEFAULT 'AR5' CHECK (gwp_framework IN ('AR4', 'AR5', 'AR6')),
    region VARCHAR(50) NOT NULL DEFAULT 'EG', -- 'EG', 'UK', 'US', 'EU', 'GLOBAL'
    source_id UUID REFERENCES factor_sources(source_id) ON DELETE SET NULL,
    source_citation TEXT NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_test_data BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_factor_version UNIQUE (factor_code, version)
);

CREATE INDEX idx_ef_lookup ON emission_factors(factor_code, valid_from, valid_to);
CREATE INDEX idx_ef_activity ON emission_factors(fuel_or_activity_type, region, valid_from);

-- 3. Egyptian Grid Electricity Baselines
CREATE TABLE grid_emission_factors (
    grid_factor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    factor_id UUID NOT NULL REFERENCES emission_factors(factor_id) ON DELETE CASCADE,
    grid_name VARCHAR(150) NOT NULL DEFAULT 'Unified_Egyptian_National_Grid',
    calculation_method VARCHAR(50) NOT NULL CHECK (calculation_method IN ('LOCATION_BASED', 'MARKET_BASED', 'RESIDUAL_MIX')),
    transmission_loss_rate NUMERIC(5, 4) NOT NULL DEFAULT 0.0720, -- 7.2% national average
    generation_mix_summary JSONB, -- {'natural_gas_pct': 88.0, 'solar_wind_pct': 7.5, 'hydro_pct': 4.5}
    valid_year INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Egyptian Local Fuel Specifications & Net Calorific Values (NCV)
CREATE TABLE fuel_calorific_values (
    fuel_spec_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fuel_name VARCHAR(100) UNIQUE NOT NULL,
    name_ar VARCHAR(100) NOT NULL,
    technical_grade VARCHAR(100),
    net_calorific_value NUMERIC(10, 4) NOT NULL, -- e.g., 38.20 for Gas, 43.00 for Solar
    ncv_unit VARCHAR(50) NOT NULL, -- 'MJ/m3', 'MJ/kg'
    density_kg_per_unit NUMERIC(10, 4) NOT NULL, -- Density (e.g., 0.845 kg/L for solar)
    carbon_content_factor_kg_tj NUMERIC(12, 2) NOT NULL, -- kg CO2 / TJ
    standard_emission_factor NUMERIC(12, 6) NOT NULL, -- Resulting factor
    source_reference VARCHAR(255) NOT NULL
);

-- =============================================================================
-- SEED DATA: Official Egyptian Baselines (EEAA, NREA, EGPC)
-- =============================================================================

INSERT INTO factor_sources (source_code, name, issuing_body, publication_year, is_official_regulatory_source) VALUES
('EEAA_2025', 'Egyptian National GHG Baseline Inventory', 'Egyptian Environmental Affairs Agency', 2025, TRUE),
('EGPC_2025', 'Petroleum Fuel Standards & Calorific Baselines', 'Egyptian General Petroleum Corporation', 2025, TRUE),
('DEFRA_2024', 'UK Government GHG Conversion Factors', 'DESNZ / DEFRA', 2024, TRUE)
ON CONFLICT (source_code) DO NOTHING;

-- Seed Egyptian Fuel Specifications
INSERT INTO fuel_calorific_values (fuel_name, name_ar, technical_grade, net_calorific_value, ncv_unit, density_kg_per_unit, carbon_content_factor_kg_tj, standard_emission_factor, source_reference) VALUES
('Natural_Gas', 'الغاز الطبيعي', 'Methane-rich pipeline blend', 38.20, 'MJ/m3', 0.730, 56100.00, 2.143000, 'EEAA National Inventory / EGAS'),
('Solar_Gasoil', 'سولار', 'Industrial & automotive diesel', 43.00, 'MJ/kg', 0.845, 74100.00, 2.692500, 'EGPC Technical Specification'),
('Mazut', 'مازوت', 'Heavy Fuel Oil (high sulfur)', 40.40, 'MJ/kg', 0.965, 77400.00, 3.127000, 'EEAA Industrial Guideline'),
('Octane_92', 'بنزين ٩٢', 'Domestic light vehicle gasoline', 44.30, 'MJ/kg', 0.742, 69300.00, 2.278000, 'EGPC Logistics Standard'),
('Octane_95', 'بنزين ٩٥', 'Premium motor gasoline', 44.50, 'MJ/kg', 0.750, 69300.00, 2.310500, 'EGPC Logistics Standard')
ON CONFLICT (fuel_name) DO UPDATE SET standard_emission_factor = EXCLUDED.standard_emission_factor;

-- Seed Egyptian Emission Factors
INSERT INTO emission_factors (factor_code, version, name, scope, category, fuel_or_activity_type, unit, co2e_factor, gwp_framework, region, source_citation, valid_from, valid_to, is_test_data) VALUES
('EF-EGY-GRID-LOC', 1, 'Egyptian National Electricity Grid (Location-Based)', 'Scope 2', 'Purchased_Electricity', 'grid_electricity', 'kWh', 0.000458, 'AR5', 'EG', 'EEAA/NREA Baseline 2024-2026 (0.4580 tCO2e/MWh net 7.2% loss)', '2024-01-01', '2026-12-31', FALSE),
('EF-EGY-GRID-LOC-MWH', 1, 'Egyptian National Electricity Grid (MWh Basis)', 'Scope 2', 'Purchased_Electricity', 'grid_electricity', 'MWh', 0.458000, 'AR5', 'EG', 'EEAA/NREA Baseline 2024-2026 (0.4580 tCO2e/MWh)', '2024-01-01', '2026-12-31', FALSE),
('EF-EGY-GAS-M3', 1, 'Natural Gas Stationary Combustion (m3)', 'Scope 1', 'Stationary_Combustion', 'natural_gas', 'm3', 2.143000, 'AR5', 'EG', 'EEAA / EGAS Pipeline Blend Standard (2.1430 kgCO2e/m3)', '2024-01-01', '2026-12-31', FALSE),
('EF-EGY-SOLAR-L', 1, 'Solar / Diesel Industrial Combustion (Litres)', 'Scope 1', 'Stationary_Combustion', 'diesel', 'L', 2.692500, 'AR5', 'EG', 'EGPC Standard Diesel (2.6925 kgCO2e/L)', '2024-01-01', '2026-12-31', FALSE),
('EF-EGY-MAZUT-TON', 1, 'Mazut Heavy Fuel Oil (Metric Ton)', 'Scope 1', 'Stationary_Combustion', 'mazut', 'Ton', 3.127000, 'AR5', 'EG', 'EEAA Industrial Baseline for Cement & Steel (3.1270 tCO2e/Ton)', '2024-01-01', '2026-12-31', FALSE),
('EF-EGY-OCT92-L', 1, 'Octane 92 Mobile Combustion (Litres)', 'Scope 1', 'Mobile_Combustion', 'petrol', 'L', 2.278000, 'AR5', 'EG', 'EGPC Fleet Standard (2.2780 kgCO2e/L)', '2024-01-01', '2026-12-31', FALSE),
('EF-EGY-FREIGHT-HDV', 1, 'Heavy-Duty Articulated Truck (>32t)', 'Scope 3', 'Freight_Transport', 'heavy_truck', 'tonne-km', 0.088500, 'AR5', 'EG', 'Egyptian National Logistics Baseline', '2024-01-01', '2026-12-31', FALSE),
('EF-EGY-FREIGHT-RIGID', 1, 'Rigid Commercial Truck (7.5-16t)', 'Scope 3', 'Freight_Transport', 'rigid_truck', 'tonne-km', 0.194200, 'AR5', 'EG', 'Egyptian National Logistics Baseline', '2024-01-01', '2026-12-31', FALSE),
('EF-EGY-FREIGHT-VAN', 1, 'Light Commercial Transport Van (<3.5t)', 'Scope 3', 'Freight_Transport', 'van', 'km', 0.312000, 'AR5', 'EG', 'Egyptian Urban Distribution Fleet Baseline', '2024-01-01', '2026-12-31', FALSE)
ON CONFLICT (factor_code, version) DO UPDATE SET co2e_factor = EXCLUDED.co2e_factor;
