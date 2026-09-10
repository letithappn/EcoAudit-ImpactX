-- =============================================================================
-- EcoAudit AI / Enterprise Carbon Accounting Platform for Egypt
-- Migration 004: Double-Entry Carbon General Ledger & Cryptographic Chaining
-- Standards: Financial Accounting Standards applied to Carbon Accounting (GHG Protocol & PCAF)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Chart of Carbon Accounts (COCA)
CREATE TABLE carbon_accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., '2100-S1-GAS-LIABILITY', '1000-ABSORPTION-CLEARING'
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN (
        'EMISSION_LIABILITY',   -- Equivalent to a financial liability
        'ABSORPTION_CLEARING', -- Balancing clearing account
        'CARBON_ASSET_OFFSET', -- Retired CERCs or Carbon Credits
        'CAPITAL_EXPENDITURE'  -- Precursor embedded emissions
    )),
    scope VARCHAR(20) CHECK (scope IN ('Scope 1', 'Scope 2', 'Scope 3', 'Offset', 'None')),
    category VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Seed Chart of Carbon Accounts
INSERT INTO carbon_accounts (account_code, account_name, account_type, scope, category) VALUES
('1000-CLEARING-ABSORPTION', 'General Energy & Production Absorption Clearing', 'ABSORPTION_CLEARING', 'None', 'Clearing'),
('1500-OFFSET-CERC-RESERVE', 'Regulated Egyptian Carbon Emission Reduction Reserve (EGX)', 'CARBON_ASSET_OFFSET', 'Offset', 'Voluntary_Market'),
('2110-S1-STATIONARY-GAS', 'Scope 1 Stationary Combustion: Natural Gas Liability', 'EMISSION_LIABILITY', 'Scope 1', 'Stationary_Combustion'),
('2120-S1-STATIONARY-SOLAR', 'Scope 1 Stationary Combustion: Solar/Diesel Liability', 'EMISSION_LIABILITY', 'Scope 1', 'Stationary_Combustion'),
('2130-S1-STATIONARY-MAZUT', 'Scope 1 Stationary Combustion: Mazut Heavy Fuel Oil Liability', 'EMISSION_LIABILITY', 'Scope 1', 'Stationary_Combustion'),
('2210-S1-MOBILE-OCTANE', 'Scope 1 Mobile Combustion: Fleet Gasoline Liability', 'EMISSION_LIABILITY', 'Scope 1', 'Mobile_Combustion'),
('2300-S2-GRID-ELECTRICITY', 'Scope 2 Purchased Electricity: National Grid Liability', 'EMISSION_LIABILITY', 'Scope 2', 'Purchased_Electricity'),
('2410-S3-PURCHASED-GOODS', 'Scope 3 Category 1: Purchased Goods & Raw Materials', 'EMISSION_LIABILITY', 'Scope 3', 'Purchased_Goods'),
('2440-S3-UPSTREAM-LOGISTICS', 'Scope 3 Category 4: Upstream Freight & Logistics Liability', 'EMISSION_LIABILITY', 'Scope 3', 'Freight_Transport')
ON CONFLICT (account_code) DO NOTHING;

-- 2. Carbon Journal Header (Transaction Bundle)
CREATE TABLE carbon_journal_entries (
    journal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(facility_id) ON DELETE RESTRICT,
    accounting_period CHAR(7) NOT NULL, -- Format: 'YYYY-MM'
    posting_date DATE NOT NULL DEFAULT CURRENT_DATE,
    description TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'POSTED', 'REVERSED')),
    reversal_of_journal_id UUID REFERENCES carbon_journal_entries(journal_id),
    total_debit_tco2e NUMERIC(14, 6) NOT NULL DEFAULT 0.000000,
    total_credit_tco2e NUMERIC(14, 6) NOT NULL DEFAULT 0.000000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_balanced_journal CHECK (status != 'POSTED' OR total_debit_tco2e = total_credit_tco2e)
);

CREATE INDEX idx_journal_tenant_period ON carbon_journal_entries(tenant_id, accounting_period);

-- 3. Double-Entry Carbon Ledger Postings (Immutable Transactions)
CREATE TABLE carbon_ledger_postings (
    posting_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_id UUID NOT NULL REFERENCES carbon_journal_entries(journal_id) ON DELETE RESTRICT,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE RESTRICT,
    facility_id UUID NOT NULL REFERENCES facilities(facility_id) ON DELETE RESTRICT,
    activity_id UUID REFERENCES activity_data(activity_id) ON DELETE RESTRICT,
    factor_id UUID NOT NULL REFERENCES emission_factors(factor_id) ON DELETE RESTRICT,
    account_id UUID NOT NULL REFERENCES carbon_accounts(account_id) ON DELETE RESTRICT,
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    co2e_metric_tons NUMERIC(14, 6) NOT NULL CHECK (co2e_metric_tons >= 0),
    co2e_kg NUMERIC(18, 3) GENERATED ALWAYS AS (co2e_metric_tons * 1000.0) STORED,
    line_sequence INT NOT NULL,
    previous_entry_hash CHAR(64) NOT NULL,
    entry_hash CHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_postings_journal ON carbon_ledger_postings(journal_id);
CREATE INDEX idx_postings_tenant ON carbon_ledger_postings(tenant_id);
CREATE INDEX idx_postings_hash ON carbon_ledger_postings(entry_hash);

-- 4. Cryptographic Hashing Function
CREATE OR REPLACE FUNCTION compute_ledger_entry_hash(
    p_prev_hash TEXT,
    p_posting_id UUID,
    p_tenant_id UUID,
    p_facility_id UUID,
    p_activity_id UUID,
    p_factor_id UUID,
    p_entry_type TEXT,
    p_account_id UUID,
    p_co2e_tons NUMERIC,
    p_timestamp TIMESTAMPTZ
) RETURNS CHAR(64) AS $$
DECLARE
    v_payload TEXT;
BEGIN
    v_payload := COALESCE(p_prev_hash, REPEAT('0', 64)) || '|' ||
                 p_posting_id::TEXT || '|' ||
                 p_tenant_id::TEXT || '|' ||
                 p_facility_id::TEXT || '|' ||
                 COALESCE(p_activity_id::TEXT, 'NO_ACTIVITY') || '|' ||
                 p_factor_id::TEXT || '|' ||
                 p_entry_type || '|' ||
                 p_account_id::TEXT || '|' ||
                 TO_CHAR(p_co2e_tons, 'FM999999990.000000') || '|' ||
                 p_timestamp::TEXT;
    RETURN ENCODE(DIGEST(v_payload, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 5. Immutability Enforcement Trigger
CREATE OR REPLACE FUNCTION prevent_ledger_mutation() RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE' OR TG_OP = 'DELETE') THEN
        RAISE EXCEPTION 'CRITICAL AUDIT VIOLATION: Carbon ledger postings are strictly append-only and cannot be updated or deleted. Post a compensating reversal journal entry instead.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_immutable_ledger
BEFORE UPDATE OR DELETE ON carbon_ledger_postings
FOR EACH ROW EXECUTE FUNCTION prevent_ledger_mutation();

-- Enable Row-Level Security
ALTER TABLE carbon_journal_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE carbon_ledger_postings ENABLE ROW LEVEL SECURITY;

CREATE POLICY ledger_isolation_policy ON carbon_ledger_postings
    FOR ALL USING (tenant_id = current_app_tenant_id());
CREATE POLICY journal_isolation_policy ON carbon_journal_entries
    FOR ALL USING (tenant_id = current_app_tenant_id());
