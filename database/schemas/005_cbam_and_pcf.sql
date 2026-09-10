-- =============================================================================
-- EcoAudit AI / Enterprise Carbon Accounting Platform for Egypt
-- Migration 005: EU CBAM Readiness, Product Carbon Footprint (PCF) & Bill of Materials (BOM)
-- Standards: EU Regulation 2023/956, Commission Implementing Regulation (EU) 2025/2547, ISO 14067
-- =============================================================================

-- 1. Manufactured Finished & Precursor Products
CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    product_name VARCHAR(255) NOT NULL,
    erp_material_code VARCHAR(100) NOT NULL,
    cn_code VARCHAR(8) NOT NULL, -- 8-digit EU Combined Nomenclature (e.g., '73011000' for Steel Sheets, '76061100' for Aluminum)
    sector VARCHAR(50) NOT NULL CHECK (sector IN (
        'IRON_AND_STEEL',
        'ALUMINUM',
        'CEMENT',
        'FERTILIZERS',
        'HYDROGEN',
        'ELECTRICITY',
        'GENERAL_MANUFACTURING'
    )),
    cbam_annex VARCHAR(20) NOT NULL DEFAULT 'ANNEX_II' CHECK (cbam_annex IN ('ANNEX_II', 'ANNEX_IV', 'NON_CBAM')),
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'TONNE',
    is_precursor BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_tenant_material UNIQUE (tenant_id, erp_material_code)
);

CREATE INDEX idx_products_cn ON products(cn_code);
CREATE INDEX idx_products_sector ON products(sector);

-- 2. Bill of Materials (BOM) & Precursor Hierarchy
CREATE TABLE bill_of_materials (
    bom_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    component_product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity_required NUMERIC(14, 6) NOT NULL CHECK (quantity_required > 0),
    component_unit VARCHAR(20) NOT NULL DEFAULT 'TONNE',
    scrap_rate_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0.00 CHECK (scrap_rate_percentage >= 0 AND scrap_rate_percentage < 100),
    is_relevant_precursor BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bom_parent ON bill_of_materials(parent_product_id);

-- 3. Production Steps & Routing (Machine Hour Allocation)
CREATE TABLE production_routes (
    route_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    facility_id UUID NOT NULL REFERENCES facilities(facility_id) ON DELETE RESTRICT,
    step_sequence INT NOT NULL,
    step_name VARCHAR(150) NOT NULL, -- e.g., 'Direct Reduction', 'Electric Arc Furnace', 'Hot Rolling'
    electricity_intensity_kwh_per_unit NUMERIC(14, 4) NOT NULL DEFAULT 0.0000,
    thermal_fuel_type VARCHAR(100), -- 'Natural_Gas', 'Mazut', 'Solar_Gasoil'
    thermal_fuel_intensity_per_unit NUMERIC(14, 4) NOT NULL DEFAULT 0.0000,
    anode_pfc_emission_factor NUMERIC(10, 6) DEFAULT 0.0000, -- For Aluminum Smelters (CF4 & C2F6)
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Batch Runs & Product Carbon Footprint (PCF) Lineage
CREATE TABLE product_carbon_footprints (
    pcf_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    facility_id UUID NOT NULL REFERENCES facilities(facility_id) ON DELETE RESTRICT,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    production_batch_number VARCHAR(100) NOT NULL,
    reporting_quarter CHAR(7) NOT NULL, -- e.g., '2026-Q1'
    batch_quantity_tonnes NUMERIC(14, 4) NOT NULL CHECK (batch_quantity_tonnes > 0),
    
    -- Specific Embedded Emissions Breakdown (SEE_g in tCO2e / Tonne)
    direct_embedded_emissions_tco2e NUMERIC(14, 6) NOT NULL DEFAULT 0.000000,
    indirect_embedded_emissions_tco2e NUMERIC(14, 6) NOT NULL DEFAULT 0.000000,
    precursor_embedded_emissions_tco2e NUMERIC(14, 6) NOT NULL DEFAULT 0.000000,
    total_specific_embedded_tco2e_per_ton NUMERIC(14, 6) NOT NULL,
    
    -- Primary Data Compliance Thresholds (EU mandates >= 80% primary data)
    default_values_share_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0.00 
        CHECK (default_values_share_percentage <= 20.00), -- Rejects non-compliant runs
    calculation_methodology VARCHAR(100) NOT NULL DEFAULT 'EU_CBAM_Definitive_Methodology_Annex_III',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pcf_product_period ON product_carbon_footprints(product_id, reporting_quarter);

-- 5. Quarterly Official EU CBAM Declarations
CREATE TABLE cbam_quarterly_declarations (
    declaration_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    facility_id UUID NOT NULL REFERENCES facilities(facility_id) ON DELETE RESTRICT,
    reporting_quarter CHAR(7) NOT NULL, -- '2026-Q1', '2026-Q2', etc.
    total_goods_exported_tonnes NUMERIC(16, 4) NOT NULL,
    total_embedded_emissions_tco2e NUMERIC(16, 4) NOT NULL,
    annex_ii_emissions_tco2e NUMERIC(16, 4) NOT NULL DEFAULT 0.0000,
    annex_iv_emissions_tco2e NUMERIC(16, 4) NOT NULL DEFAULT 0.0000,
    submission_status VARCHAR(50) NOT NULL DEFAULT 'DRAFT' 
        CHECK (submission_status IN ('DRAFT', 'AUDITOR_CERTIFIED', 'SUBMITTED_TO_COMMISSION', 'AMENDED')),
    declaration_xml_payload XML,
    signed_by_person_name VARCHAR(255),
    signed_by_role VARCHAR(150),
    certified_by_vvb_name VARCHAR(255), -- e.g., 'TUV Nord Egypt', 'SGS Egypt'
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_facility_quarter UNIQUE (facility_id, reporting_quarter)
);

-- Enable Row-Level Security
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_carbon_footprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE cbam_quarterly_declarations ENABLE ROW LEVEL SECURITY;

CREATE POLICY products_isolation_policy ON products
    FOR ALL USING (tenant_id = current_app_tenant_id());
CREATE POLICY pcf_isolation_policy ON product_carbon_footprints
    FOR ALL USING (tenant_id = current_app_tenant_id());
CREATE POLICY cbam_isolation_policy ON cbam_quarterly_declarations
    FOR ALL USING (tenant_id = current_app_tenant_id());
