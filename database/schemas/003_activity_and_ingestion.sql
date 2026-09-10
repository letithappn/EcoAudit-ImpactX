-- =============================================================================
-- EcoAudit AI / Enterprise Carbon Accounting Platform for Egypt
-- Migration 003: Ingestion Pipeline, Arabic/English OCR & Activity Ingestion
-- Standards: GHG Protocol Corporate Standard (Chapter 6: Quantifying GHG Emissions)
-- =============================================================================

-- 1. Ingested Physical & Digital Documents
CREATE TABLE raw_documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    facility_id UUID REFERENCES facilities(facility_id) ON DELETE SET NULL,
    file_name VARCHAR(255) NOT NULL,
    storage_s3_key TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    sha256_hash CHAR(64) NOT NULL,
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN (
        'ELECTRICITY_BILL_PAPER', -- Scanned invoice from South/North Cairo Co., etc.
        'NATURAL_GAS_INVOICE',
        'FUEL_DELIVERY_SLIP',     -- Hand-signed Solar/Diesel slip
        'WEIGHBRIDGE_RECEIPT',
        'ERP_EXPORT_CSV',
        'PROCUREMENT_INVOICE'
    )),
    uploaded_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_docs_tenant ON raw_documents(tenant_id);
CREATE INDEX idx_docs_hash ON raw_documents(sha256_hash);

-- 2. OCR Layout Segmentation & Bilingual Extraction Results
CREATE TABLE ocr_extractions (
    extraction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES raw_documents(document_id) ON DELETE CASCADE,
    ocr_engine VARCHAR(50) NOT NULL DEFAULT 'TrOCR_Bilingual_v2',
    raw_extracted_text TEXT NOT NULL,
    arabic_numerals_normalized BOOLEAN NOT NULL DEFAULT TRUE,
    layout_segments JSONB, -- Coordinates of Meter No, Dates, Active Energy kWh, Total EGP
    parsed_fields JSONB NOT NULL, -- Key-value pairs extracted by LLM/parser
    overall_confidence_score NUMERIC(5, 4) NOT NULL, -- 0.0000 to 1.0000
    requires_hitl BOOLEAN GENERATED ALWAYS AS (overall_confidence_score < 0.92) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ocr_doc ON ocr_extractions(document_id);

-- 3. Human-in-the-Loop (HITL) Validation Queue
CREATE TABLE hitl_review_queue (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    extraction_id UUID NOT NULL REFERENCES ocr_extractions(extraction_id) ON DELETE CASCADE,
    assigned_reviewer_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    review_status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (review_status IN ('PENDING', 'IN_REVIEW', 'APPROVED', 'REJECTED')),
    rejection_reason TEXT,
    field_corrections JSONB, -- Original vs. Human corrected values
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hitl_tenant_status ON hitl_review_queue(tenant_id, review_status);

-- 4. Ingestion Batches
CREATE TABLE activity_batches (
    batch_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    batch_name VARCHAR(255) NOT NULL,
    source_channel VARCHAR(50) NOT NULL CHECK (source_channel IN ('WEB_UPLOAD', 'REST_API', 'ERP_SAP_CONNECTOR', 'ERP_ODOO_CONNECTOR', 'TELEMETRY_MQTT')),
    total_records INT NOT NULL DEFAULT 0,
    valid_records INT NOT NULL DEFAULT 0,
    rejected_records INT NOT NULL DEFAULT 0,
    processing_status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (processing_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. Standardized Normalized Activity Data
CREATE TABLE activity_data (
    activity_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    facility_id UUID NOT NULL REFERENCES facilities(facility_id) ON DELETE RESTRICT,
    batch_id UUID REFERENCES activity_batches(batch_id) ON DELETE SET NULL,
    document_id UUID REFERENCES raw_documents(document_id) ON DELETE SET NULL,
    activity_code VARCHAR(100), -- Unique ERP or meter reference
    activity_type VARCHAR(100) NOT NULL, -- 'grid_electricity', 'natural_gas', 'diesel', 'mazut', 'petrol', 'employee_flight', 'freight_transport'
    quantity NUMERIC(18, 4) NOT NULL CHECK (quantity >= 0),
    unit VARCHAR(50) NOT NULL, -- 'kWh', 'MWh', 'L', 'm3', 'Ton', 'passenger-km', 'tonne-km'
    scope VARCHAR(20) NOT NULL CHECK (scope IN ('Scope 1', 'Scope 2', 'Scope 3')),
    category VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_cost_egp NUMERIC(18, 2), -- Explicit monetary value in EGP (never extrapolated)
    meter_serial_number VARCHAR(100),
    ocr_confidence_score NUMERIC(5, 4),
    validation_status VARCHAR(50) NOT NULL DEFAULT 'DRAFT' CHECK (validation_status IN ('DRAFT', 'VALIDATED', 'FLAGGED_REVIEW', 'REJECTED')),
    metadata JSONB, -- Additional ERP cost center, supplier, transport mode metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_date_sequence CHECK (end_date >= start_date)
);

CREATE INDEX idx_activity_tenant_period ON activity_data(tenant_id, start_date, end_date);
CREATE INDEX idx_activity_type ON activity_data(activity_type, scope);
CREATE INDEX idx_activity_facility ON activity_data(facility_id);

-- Apply Row-Level Security
ALTER TABLE raw_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE hitl_review_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY activity_isolation_policy ON activity_data
    FOR ALL USING (tenant_id = current_app_tenant_id());
CREATE POLICY raw_docs_isolation_policy ON raw_documents
    FOR ALL USING (tenant_id = current_app_tenant_id());
