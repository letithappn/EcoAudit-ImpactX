# Module 3: System Architecture & Tech Stack Tailored for Egypt
**Engineering Blueprint: Bilingual Ingestion, Deterministic Compute, ANSI/ISA-101 HMI & Enterprise ERP Integration**

---

## 1. Solving the "Dirty Data / Paper-Heavy" Reality in Egyptian Industry

Egyptian industrial facilities (e.g., factories in 10th of Ramadan, 6th of October, Sadat City, Helwan, and Alexandria) do not operate on clean digital utility API feeds. Over 75% of operational activity data exists as physical, low-grade paper artifacts:
- Carbon-copy utility invoices from regional distributors:
  - **South Cairo Electricity Distribution Company (SCEDC - شركة جنوب القاهرة لتوزيع الكهرباء)**
  - **North Cairo Electricity Distribution Company (NCEDC - شركة شمال القاهرة لتوزيع الكهرباء)**
  - **Canal Electricity Distribution Company (CEDC - شركة القناة لتوزيع الكهرباء)**
  - **Alexandria Electricity Distribution Company (AEDC - شركة الإسكندرية لتوزيع الكهرباء)**
- Handwritten thermal fuel slips (Solar/Diesel delivery chits, Mazut tank-dipping logs).
- Printed Arabic-language procurement invoices with mixed Eastern Arabic numerals (`٠, ١, ٢, ٣, ٤, ٥, ٦, ٧, ٨, ٩`) and Western digits.

```
                                  Physical Paper Invoice / Scan
                                                │
                                                ▼
                             ┌─────────────────────────────────────┐
                             │ Stage 1: OpenCV Preprocessing       │
                             │ • Radon-transform Deskewing         │
                             │ • Otsu Adaptive Binarization        │
                             │ • Morphological Denoising           │
                             └──────────────────┬──────────────────┘
                                                │
                                                ▼
                             ┌─────────────────────────────────────┐
                             │ Stage 2: YOLO Layout Segmentation   │
                             │ • Region of Interest (ROI) Bounding │
                             │ • Header, Meter, Dates, kWh, EGP    │
                             └──────────────────┬──────────────────┘
                                                │
                                                ▼
                             ┌─────────────────────────────────────┐
                             │ Stage 3: Bilingual TrOCR Engine     │
                             │ • Fine-Tuned Arabic Vision-Language │
                             │ • Eastern-to-Western Digit Convert  │
                             └──────────────────┬──────────────────┘
                                                │
                                                ▼
                             ┌─────────────────────────────────────┐
                             │ Stage 4: Mathematical Cross-Check   │
                             │ • Reading Delta = Active kWh        │
                             │ • Tariff Voltage Bracket Parity     │
                             └──────────────────┬──────────────────┘
                                                │
                                                ├──────────────┐
                                Confidence ≥ 0.92              Confidence < 0.92
                                                │              │ (or Anomaly)
                                                ▼              ▼
                                     ┌──────────────────┐  ┌──────────────────┐
                                     │ Verified Data DB │  │ HITL Review Queue│
                                     │ (activity_data)  │  │ (Audit Dashboard)│
                                     └──────────────────┘  └──────────────────┘
```

### 1.1 Document Preprocessing Pipeline (Computer Vision)
Uploaded scans (TIFF/PDF/JPG) pass through a containerized OpenCV pipeline to eliminate skew, sensor noise, and contrast degradation:
1. **Radon-Transform Deskewing:** Determines the dominant orientation angle of text rows across $[-45^\circ, +45^\circ]$ and rotates the image matrix to zero-degree alignment.
2. **Otsu Adaptive Binarization:** Overcomes uneven illumination (e.g., shadows cast by plant supervisors photographing bills with mobile cameras) by evaluating local $31 \times 31$ pixel window thresholds:
   $$T(x,y) = \mu(x,y) \times \left(1 + k \times \left(\frac{\sigma(x,y)}{R} - 1\right)\right)$$
3. **Morphological Filtering:** Applies open/close kernel operations ($3 \times 3$ structuring element) to remove scanner grain and salt-and-pepper noise while preserving the stroke integrity of Arabic diacritics.

### 1.2 Layout Segmentation & Bilingual Extraction (YOLOv8 + TrOCR)
- **Document Layout Segmentation:** A lightweight YOLOv8-Doc model identifies key regions of interest (ROIs):
  - `distributor_logo_roi`: Identifies regional utility company (e.g., South Cairo vs. Canal).
  - `meter_metadata_roi`: Captures meter serial number, account number, voltage tier (Medium 11/22 kV vs. High 66 kV).
  - `consumption_table_roi`: Isolates previous reading, current reading, multiplying factor, and active consumption.
  - `financial_summary_roi`: Captures energy tariff charge, fuel clause surcharge, customer service fees, and total EGP payable.
- **Bilingual TrOCR Architecture:** Printed tabular cells are passed to a dual-head Transformer model. Printed numerals and English identifiers are processed via an OCR backbone, while Arabic headings and handwritten signatures are parsed by a fine-tuned Arabic Vision Transformer (`microsoft/trocr-base-stage1` fine-tuned on corporate Egyptian Arabic invoices).
- **Eastern Arabic Numeral Normalization:** A deterministic Unicode substitution layer maps all Eastern Arabic numerals (`U+0660`–`U+0669`) to standard ASCII digits (`0`–`9`):
  ```python
  EASTERN_TO_WESTERN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
  normalized_kwh = raw_kwh_text.translate(EASTERN_TO_WESTERN)
  ```

### 1.3 Automated Verification & Human-in-the-Loop (HITL) Queue
Before inserting any parsed record into the operational activity store, the pipeline executes automated sanity constraints:
1. **Consumption Consistency:**
   $$\text{Delta} = (\text{Meter Reading}_{\text{current}} - \text{Meter Reading}_{\text{previous}}) \times \text{Multiplier}$$
   The extracted active consumption must match $\text{Delta}$ within $\pm 0.1\%$.
2. **Tariff Rate Bracket Validation:** Total billed amount is divided by active kWh and matched against the official EgyptERA (Egyptian Electric Utility and Consumer Protection Regulatory Agency) industrial tariff schedule.
3. **Meter Serial Verification:** The extracted meter number is verified against the tenant’s registered facility meter inventory.

**The HITL Quarantine Rule:**
If the aggregate extraction confidence score is **$< 0.92$**, if the meter reading delta fails, or if the meter serial does not exist in the tenant's registry, the document is immediately quarantined in `hitl_review_queue`. An industrial auditor must review the side-by-side split screen (original image with bounding boxes vs. parsed editable fields) and click an explicit dual-step confirmation before the record can be committed.

---

## 2. Recommended Enterprise Technology Stack

EcoAudit AI implements a distributed, decoupled microservices architecture designed for high availability, sub-millisecond calculation recalculations, and complete audit immutability.

```
┌────────────────────────────────────────────────────────────────────────┐
│               Enterprise Technology Stack Architecture                 │
├────────────────────────────────────────────────────────────────────────┤
│ Presentation Layer (Next.js 15, React 19, Tailwind, Tremor, D3.js)    │
│ ANSI/ISA-101.01 High-Performance HMI (Neutral Gray #2B2B2B, SBO)      │
├──────────────────────────────────┬─────────────────────────────────────┤
│ REST & Webhook Gateway (FastAPI) │ Async Ingestion Queue (Celery/Redis)│
├──────────────────────────────────┴─────────────────────────────────────┤
│ Deterministic Calculation Core (Python 3.12 + PyO3 Rust Vector Engine) │
├────────────────────────────────────────────────────────────────────────┤
│ Enterprise Connectors: SAP S/4HANA (OData), Odoo (RPC), Oracle, Meters │
├────────────────────────────────────────────────────────────────────────┤
│ Data Layer: PostgreSQL 16 (RLS Multi-Tenancy) + TimescaleDB + MinIO S3 │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Backend: Hybrid Python FastAPI + PyO3 Rust Vector Core
- **API Orchestration Layer:** Built with **Python 3.12** and **FastAPI**. Exposes asynchronous, OpenAPI 3.1-compliant endpoints for tenant onboarding, invoice upload, scenario modeling, and regulatory reporting.
- **Vectorized Calculation Engine (Rust via PyO3):**
  While standard activity additions are fast in Python `Decimal`, enterprise clients with 50+ facilities and 100,000+ historical ledger entries face substantial latency when a national grid factor is retroactively updated (requiring a full recalculation of multi-year corporate baselines).
  The core calculation loops, DAG traversal, and SHA-256 state hashing are compiled into a native Rust crate (`ecoaudit_engine_core`) and bound to Python via **PyO3**. This guarantees:
  - 100% deterministic, 128-bit fixed-point arithmetic (zero IEEE-754 floating-point inaccuracies).
  - Recalculation throughput exceeding **500,000 ledger transactions per second** across SIMD vector lanes.
  - Strict memory safety without garbage collection pauses during audit report generation.

### 2.2 Frontend: ANSI/ISA-101.01 High-Performance Industrial HMI
The user interface adheres strictly to **ANSI/ISA-101.01 (Human Machine Interfaces for Process Automation Systems)** and **ISA-18.2 / EEMUA 191** alarm management standards, rejecting consumer SaaS aesthetic cliches:

1. **Report-by-Exception Philosophy:**
   - Background canvas: Uniform, flat neutral gray (`#2B2B2B` in dark mode / `#D0D0D0` in high-contrast industrial light mode).
   - Normal operating conditions (steady-state energy consumption, verified invoices, balanced ledgers) are rendered in muted, low-saturation grays (`#808080`–`#A0A0A0`).
   - Saturated colors are **strictly reserved for abnormal deviations and alerts**:
     - **Crimson Red (`#D32F2F`):** Critical Alarms (CBAM threshold breach, unverified ledger entry, negative balance).
     - **Amber Orange (`#F57C00`):** High Warnings (HITL confidence $< 0.92$, tariff bracket mismatch, meter out of calibration).
     - **Bright Cyan (`#00ACC1`):** Active selections and operator focus indicators.
2. **Four-Level Industrial Display Hierarchy:**
   - **Level 1 — Enterprise & Site Overview:** Global compliance posture, aggregate Scope 1/2/3 totals, regulatory filing countdown timers (FRA June 30 deadline, EU CBAM quarter close), and critical alarm count. Designed for $< 5$-second operator comprehension.
   - **Level 2 — Facility & Unit Workspace:** Specific industrial zone facility view (e.g., 10th of Ramadan Steel Mill Line 3), active sub-meters, daily energy load curves, and live batch carbon accumulation.
   - **Level 3 — Equipment Faceplates & Ingestion Review:** Detailed invoice inspection, side-by-side OCR verification window, meter calibration histories, and bill-of-materials components.
   - **Level 4 — Diagnostics, Cryptographic Audit Room & Lineage Tracing:** Deep DAG traversal, SHA-256 state chain verification, raw database transaction inspection, and one-click VVB export packages.
3. **Select-Before-Operate (SBO) Two-Step Verification:**
   High-consequence actions—such as committing an unverified batch of activity data, posting compensating ledger reversals, or submitting CERC retirement orders to the EGX—cannot be executed with a single click. The UI requires:
   1. Selection of the target entity.
   2. Opening an explicit modal faceplate displaying the full before-and-after cryptographic diff.
   3. A mandatory confirmation step with audit trail logging.

### 2.3 Database Layer: Multi-Tenant PostgreSQL 16 + TimescaleDB
The persistence tier uses **PostgreSQL 16** with **TimescaleDB** extensions, organized around 6 modular schema layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│             PostgreSQL 16 Production Schemas Overview                  │
├──────────────────────────────────┬─────────────────────────────────────┤
│ Schema File                      │ Core Tables & Operational Mandate   │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 001_core_and_tenancy.sql         │ tenants, organizations, facilities, │
│                                  │ users, facility_meters (RLS Enabled)│
├──────────────────────────────────┼─────────────────────────────────────┤
│ 002_emission_factors.sql         │ emission_factors, fuel_calorific_   │
│                                  │ values, transport_factors           │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 003_activity_and_ingestion.sql   │ raw_documents, ocr_extractions,     │
│                                  │ hitl_review_queue, activity_data    │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 004_double_entry_carbon_ledger.sql│ chart_of_carbon_accounts, journal_  │
│                                  │ entries, ledger_postings (Immutable)│
├──────────────────────────────────┼─────────────────────────────────────┤
│ 005_cbam_and_pcf.sql             │ cbam_products, bill_of_materials,   │
│                                  │ production_routes, pcf_calculations │
├──────────────────────────────────┼─────────────────────────────────────┤
│ 006_compliance_and_audit.sql     │ fra_compliance_filings, verifier_   │
│                                  │ sessions, audit_trails, cerc_orders │
└──────────────────────────────────┴─────────────────────────────────────┘
```

- **Row-Level Security (RLS):** Every query executed by the application enforces tenant isolation via PostgreSQL RLS policies (`SET LOCAL app.current_tenant_id = '...'`), preventing cross-tenant data leaks.
- **TimescaleDB Hypertables:** The `facility_meters` telemetry and real-time sub-metering feeds are partitioned into 7-day chunk hypertables, ensuring microsecond analytical query times across hundreds of millions of 15-minute load readings.
- **Append-Only Immutability:** Trigger functions (`prevent_ledger_mutation`) reject any `UPDATE` or `DELETE` statements on `carbon_ledger_postings`, enforcing GAAP-standard accounting integrity.

---

## 3. Enterprise Integration & ERP Connector Architecture

Industrial enterprises in Egypt run diverse business backbones. EcoAudit AI provides three native, battle-tested integration connectors:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   SAP S/4HANA   │      │ Odoo (v14-v18)  │      │  Oracle / D365  │
│  (Large Exporter│      │  (Mid-Market    │      │  (Enterprise    │
│   Steel/Fert)   │      │   Industrial)   │      │   Corporate)    │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │ OData v4               │ JSON-RPC               │ REST API
         ▼                        ▼                        ▼
┌───────────────────────────────────────────────────────────────────┐
│               EcoAudit Enterprise Ingestion Gateway               │
│ • Schema Mapping Engine & Transformation Pipelines                │
│ • Idempotent Deduplication (Payload Hash Verification)            │
│ • Automatic Activity Staging & Factor Resolution                  │
└───────────────────────────────────────────────────────────────────┘
```

### 3.1 SAP S/4HANA Enterprise Connector
- **Protocol:** OData v4 REST endpoints querying custom SAP Core Data Services (CDS) analytical views.
- **Target Extraction Entities:**
  - **Material Documents (`MATDOC`):** Extracts physical receipts and goods issues of primary fuels (Mazut, Diesel) and chemical precursors (Ammonia, Iron Ore Pellets).
  - **Universal Journal (`ACDOCA`):** Queries general ledger line items under specific utility expense accounts to cross-validate physical invoice quantities against financial payments.
  - **Production Orders (`AFPO` / `AFKO`):** Ingests confirmed machine run hours and scrap quantities for automated Product Carbon Footprint routing.

### 3.2 Odoo Industrial Connector (v14 through v18)
- **Protocol:** JSON-RPC / XML-RPC authenticated via API user keys, widely used in Egyptian private manufacturing.
- **Target Extraction Models:**
  - `mrp.production`: Polls completed manufacturing orders to extract finished goods batches and cycle times.
  - `mrp.bom` & `mrp.bom.line`: Ingests recursive multi-level bills of materials and scrap percentage tolerances.
  - `account.move` & `account.move.line`: Ingests vendor utility bills and fuel purchase vouchers with Egyptian VAT identifiers.

### 3.3 SCADA & Industrial IoT Sub-metering Ingress
For modern facilities with digital energy management systems (Schneider PowerLogic, Siemens PAC3200, ABB M4M), EcoAudit AI provides an **MQTT / Modbus-TCP Ingress Gateway**:
- Polls 15-minute active power ($\text{kW}$), reactive power ($\text{kVAR}$), and accumulated active energy ($\text{kWh}$).
- Automatically aggregates interval telemetry into daily and monthly activity records, bypassing paper utility bills entirely for advanced sites.
