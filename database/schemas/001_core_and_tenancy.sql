-- =============================================================================
-- EcoAudit AI / Enterprise Carbon Accounting Platform for Egypt
-- Migration 001: Core Multi-Tenancy, Organizational Hierarchy & Row-Level Security
-- Standards: ISO 14064-1 Organizational Boundaries & Egyptian Commercial Registry
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 1. Tenant Master Table (Legal Entities)
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    legal_name_ar VARCHAR(255), -- Legal Arabic Name per Commercial Registry (السجل التجاري)
    legal_entity_type VARCHAR(50) NOT NULL CHECK (legal_entity_type IN ('SAE', 'LLC', 'Listed_EGX', 'NBFI', 'Partnership', 'SOE')),
    commercial_registry_number VARCHAR(100) UNIQUE NOT NULL,
    tax_identification_number VARCHAR(100) UNIQUE NOT NULL,
    country_code CHAR(2) NOT NULL DEFAULT 'EG',
    egx_ticker VARCHAR(20), -- e.g., 'CIEB', 'ESRS', 'EKHO' if listed on Egyptian Exchange
    is_egx_listed BOOLEAN NOT NULL DEFAULT FALSE,
    is_nbfi BOOLEAN NOT NULL DEFAULT FALSE, -- Non-Bank Financial Institution under FRA supervision
    issued_capital_egp NUMERIC(18, 2) NOT NULL DEFAULT 0.00,
    annual_turnover_egp NUMERIC(18, 2) DEFAULT 0.00,
    customer_segment VARCHAR(50) NOT NULL DEFAULT 'SME_Supplier' 
        CHECK (customer_segment IN ('SME_Supplier', 'Corporate_EGX_NBFI', 'CBAM_Industrial_Exporter', 'Financial_Institution')),
    is_cbam_covered BOOLEAN NOT NULL DEFAULT FALSE,
    is_green_finance_applicant BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED', 'PENDING_VERIFICATION')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenants_cr ON tenants(commercial_registry_number);
CREATE INDEX idx_tenants_tax ON tenants(tax_identification_number);
CREATE INDEX idx_tenants_segment ON tenants(customer_segment);

-- 2. Organizations / Subsidiaries Hierarchy
CREATE TABLE organizations (
    organization_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    parent_org_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    consolidation_method VARCHAR(50) NOT NULL DEFAULT 'OPERATIONAL_CONTROL' 
        CHECK (consolidation_method IN ('OPERATIONAL_CONTROL', 'FINANCIAL_CONTROL', 'EQUITY_SHARE')),
    equity_percentage NUMERIC(5, 2) NOT NULL DEFAULT 100.00 CHECK (equity_percentage >= 0 AND equity_percentage <= 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orgs_tenant ON organizations(tenant_id);

-- 3. Facilities and Operational Sites
CREATE TABLE facilities (
    facility_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    facility_name VARCHAR(255) NOT NULL,
    facility_code VARCHAR(100),
    governorate VARCHAR(100) NOT NULL, -- e.g., 'Cairo', 'Giza', 'Sharqia', 'Suez', 'Alexandria'
    industrial_zone VARCHAR(150), -- e.g., '10th of Ramadan', '6th of October', 'Sadat City', 'Ain Sokhna (SCZone)', 'Borg El Arab'
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    grid_connection_type VARCHAR(50) NOT NULL DEFAULT 'National_Grid' 
        CHECK (grid_connection_type IN ('National_Grid', 'Isolated_Minigrid', 'Private_Direct_PPA', 'Hybrid_Solar_Diesel')),
    primary_utility_distributor VARCHAR(150), -- e.g., 'South Cairo Electricity Distribution Co.', 'Canal Electricity Co.'
    is_cbam_installation BOOLEAN NOT NULL DEFAULT FALSE,
    cbam_installation_id VARCHAR(100), -- EU CBAM Registry Installation Identifier
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_facilities_tenant ON facilities(tenant_id);
CREATE INDEX idx_facilities_zone ON facilities(industrial_zone);

-- 4. User Accounts & Role-Based Access Control (RBAC)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email CITEXT UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50),
    national_id_number VARCHAR(50), -- Egyptian National ID (الرقم القومي)
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    role_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) UNIQUE NOT NULL -- 'TENANT_ADMIN', 'SUSTAINABILITY_OFFICER', 'PLANT_ENGINEER', 'EXTERNAL_AUDITOR', 'FINANCIAL_ANALYST'
);

INSERT INTO roles (role_name) VALUES 
('TENANT_ADMIN'),
('SUSTAINABILITY_OFFICER'),
('PLANT_ENGINEER'),
('EXTERNAL_AUDITOR'),
('FINANCIAL_ANALYST')
ON CONFLICT (role_name) DO NOTHING;

CREATE TABLE tenant_memberships (
    membership_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(role_id) ON DELETE RESTRICT,
    is_primary_contact BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_tenant_user UNIQUE (tenant_id, user_id)
);

CREATE INDEX idx_memberships_tenant ON tenant_memberships(tenant_id);
CREATE INDEX idx_memberships_user ON tenant_memberships(user_id);

-- 5. Row-Level Security (RLS) Isolation
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE facilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_memberships ENABLE ROW LEVEL SECURITY;

-- Context session function
CREATE OR REPLACE FUNCTION current_app_tenant_id() RETURNS UUID AS $$
    SELECT NULLIF(current_setting('app.current_tenant_id', true), '')::UUID;
$$ LANGUAGE sql STABLE;

CREATE POLICY tenant_isolation_policy ON facilities
    FOR ALL
    USING (tenant_id = current_app_tenant_id());

CREATE POLICY org_isolation_policy ON organizations
    FOR ALL
    USING (tenant_id = current_app_tenant_id());
