-- =============================================================================
-- EcoAudit AI / Enterprise Carbon Accounting Platform for Egypt
-- Migration 006: FRA Decrees 107/108 & Decision 36 Filings, Green Finance & Auditor's Room
-- Standards: FRA Decrees 107/108 (2021), Decision 36 (2026), ISO 14064-3 Third-Party Verification
-- =============================================================================

-- 1. FRA Annual Regulatory Filings (Decrees 107/108 & Decision 36/2026)
CREATE TABLE fra_compliance_filings (
    filing_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    reporting_year INT NOT NULL,
    filing_status VARCHAR(50) NOT NULL DEFAULT 'DRAFT' 
        CHECK (filing_status IN ('DRAFT', 'AUDITED', 'SUBMITTED_TO_FRA', 'REJECTED')),
    
    -- Mandatory Quantified KPIs
    e1_scope1_tco2e NUMERIC(14, 3) NOT NULL DEFAULT 0.000,
    e1_scope2_tco2e NUMERIC(14, 3) NOT NULL DEFAULT 0.000,
    e1_total_operational_tco2e NUMERIC(14, 3) NOT NULL DEFAULT 0.000,
    e1_carbon_intensity_per_million_egp NUMERIC(12, 4) NOT NULL DEFAULT 0.0000,
    e2_direct_energy_gj NUMERIC(16, 2) NOT NULL DEFAULT 0.00,
    e2_indirect_energy_mwh NUMERIC(16, 2) NOT NULL DEFAULT 0.00,
    
    -- Decision 36/2026 NBFI Mandatory 20% CERC Offset Obligation
    is_decision_36_applicable BOOLEAN NOT NULL DEFAULT FALSE,
    offset_obligation_cerc_tonnes NUMERIC(12, 0) GENERATED ALWAYS AS (
        CASE WHEN is_decision_36_applicable THEN CEIL(e1_total_operational_tco2e * 0.20) ELSE 0 END
    ) STORED,
    cerc_retired_count INT NOT NULL DEFAULT 0,
    cerc_retirement_serial_numbers JSONB, -- List of EGX carbon certificate serials
    offset_deadline_date DATE, -- 90 calendar days from filing date
    licensing_condition_status VARCHAR(50) NOT NULL DEFAULT 'PENDING_RETIREMENT' 
        CHECK (licensing_condition_status IN ('PENDING_RETIREMENT', 'COMPLIANT_RETIRED', 'LICENSE_RISK_BREACHED', 'EXEMPT')),
    
    -- TCFD / IFRS S2 Governance Disclosures
    governance_board_oversight TEXT,
    climate_risks_identified JSONB,
    transition_plan_summary TEXT,
    
    -- Verification Body Sign-Off
    verified_by_vvb_id VARCHAR(150),
    vvb_accreditation_number VARCHAR(100), -- EGAC or FRA registry accreditation
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_tenant_filing_year UNIQUE (tenant_id, reporting_year)
);

CREATE INDEX idx_fra_tenant_year ON fra_compliance_filings(tenant_id, reporting_year);

-- 2. Green Finance & Banking Disclosure Packages (CIB, EBRD, IFC)
CREATE TABLE green_finance_applications (
    application_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    bank_name VARCHAR(150) NOT NULL, -- e.g., 'Commercial International Bank (CIB)', 'EBRD', 'IFC'
    loan_facility_reference VARCHAR(100) NOT NULL,
    requested_amount_egp NUMERIC(18, 2) NOT NULL,
    interest_rate_rebate_bps INT, -- e.g., 50 bps discount for hitting carbon KPIs
    baseline_year INT NOT NULL,
    baseline_emissions_tco2e NUMERIC(14, 3) NOT NULL,
    target_reduction_percentage NUMERIC(5, 2) NOT NULL,
    verified_audit_lineage_hash CHAR(64) NOT NULL,
    package_status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED' 
        CHECK (package_status IN ('DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'APPROVED_DISBURSED', 'REJECTED')),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. The "Auditor's Room" Virtual Cleanroom Sessions
CREATE TABLE verifier_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    verifier_org_name VARCHAR(255) NOT NULL, -- e.g., 'SGS Egypt', 'TÜV Nord Egypt', 'Petrosafe', 'Integral'
    lead_auditor_name VARCHAR(255) NOT NULL,
    lead_auditor_email VARCHAR(255) NOT NULL,
    access_token_hash CHAR(64) NOT NULL UNIQUE,
    authorized_reporting_year INT NOT NULL,
    scoped_facility_ids JSONB, -- Array of facility UUIDs authorized for inspection
    expires_at TIMESTAMPTZ NOT NULL,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_token ON verifier_sessions(access_token_hash);

-- 4. Auditor Findings & Non-Conformity Management (ISO 14064-3)
CREATE TABLE auditor_findings (
    finding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES verifier_sessions(session_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    finding_type VARCHAR(50) NOT NULL CHECK (finding_type IN (
        'NON_CONFORMITY_MAJOR',
        'NON_CONFORMITY_MINOR',
        'OPPORTUNITY_FOR_IMPROVEMENT',
        'CLARIFICATION_REQUEST'
    )),
    target_table VARCHAR(100) NOT NULL, -- e.g., 'activity_data', 'emission_factors'
    target_record_id UUID,
    description TEXT NOT NULL,
    corrective_action_requested TEXT,
    resolution_status VARCHAR(50) NOT NULL DEFAULT 'OPEN' CHECK (resolution_status IN ('OPEN', 'ADDRESSED', 'CLOSED')),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. Comprehensive Immutable Audit Trail (Chained System Log)
CREATE TABLE audit_trails (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'VOID', 'CERTIFY', 'EXPORT')),
    actor_id UUID NOT NULL REFERENCES users(user_id),
    ip_address INET,
    user_agent TEXT,
    old_state JSONB,
    new_state JSONB,
    state_diff JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_table_record ON audit_trails(table_name, record_id);
CREATE INDEX idx_audit_tenant_time ON audit_trails(tenant_id, timestamp DESC);

-- Enable Row-Level Security
ALTER TABLE fra_compliance_filings ENABLE ROW LEVEL SECURITY;
ALTER TABLE green_finance_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE verifier_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE auditor_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_trails ENABLE ROW LEVEL SECURITY;

CREATE POLICY fra_isolation_policy ON fra_compliance_filings
    FOR ALL USING (tenant_id = current_app_tenant_id());
CREATE POLICY green_fin_isolation_policy ON green_finance_applications
    FOR ALL USING (tenant_id = current_app_tenant_id());
CREATE POLICY audit_trail_isolation_policy ON audit_trails
    FOR ALL USING (tenant_id = current_app_tenant_id());
