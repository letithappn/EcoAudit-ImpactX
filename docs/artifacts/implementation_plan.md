# EcoAudit AI: End-to-End Engineering Journey & Execution Roadmap

Based on the strategic and macroeconomic research conducted by our **Chief Economics & Enterprise Climate Strategist** subagent, this implementation plan decomposes the remaining technical build into **7 logical, bite-sized milestones**. 

Every milestone is designed to be executed atomically and verified independently—following the **Superpowers Test-Driven Development (TDD) Iron Law** and **Evidence Before Completion** discipline—guaranteeing that no agent is overwhelmed while maintaining a cohesive, enterprise-grade architecture.

---

## User Review Required

> [!IMPORTANT]
> **Key Architecture Decisions Locked In:**
> 1. **Data Sovereignty & Persistence:** Transition from in-memory runtime (`api/store.py`) to PostgreSQL 16 with Row-Level Security (RLS) and TimescaleDB, matching Egyptian Data Protection Law 151/2020.
> 2. **AI Boundary ("AI is NOT the Calculator"):** Vision-Language AI (Gemini Multimodal / TrOCR) handles unstructured Arabic invoice parsing and narrative drafting; 100% deterministic Python/Rust `Decimal` code executes all emission calculations, ledgering, and SHA-256 state chaining.
> 3. **Egyptian Regulatory Engine:** Native implementation of FRA Decrees 107/108, FRA Decision 36/2026 (20% CERC offset mandate), and EU CBAM definitive rules (Regulation 2023/956) with $\le 20\%$ default value caps.
> 4. **Industrial UI/UX:** Frontend strictly adopts ANSI/ISA-101.01 High-Performance HMI (Report-by-Exception, neutral gray `#2B2B2B` canvas, Select-Before-Operate 2-step verification).

---

## Executive Summary of the Business Model Canvas (BMC) Grounding

| BMC Building Block | Operational Specification for EcoAudit AI |
|---|---|
| **Target Segments** | 1. Heavy Industrial CBAM Exporters (Steel, Aluminum, Cement, Fertilizers)<br/>2. EGX-Listed & NBFIs (FRA Decrees 107/108 & Decision 36/2026)<br/>3. Green Finance Borrowers (CIB, EBRD, IFC green credit covenants)<br/>4. Supply Chain SMEs (10th of Ramadan / 6th of October) |
| **Value Proposition** | **Financial Arbitrage:** $80k consultant vs. $24k SaaS (+$56k/yr net cash saving) + Protection against €3.5M+ EU CBAM default border penalties + Automated 20% CERC licensing compliance. |
| **Pricing & Revenue** | **EGP Hybrid SaaS:** SME (180k–350k EGP) \| Enterprise/NBFI (600k–1.2M EGP) \| CBAM Exporter (1.5M–3.2M EGP) + Year 1 Advisory Retainer + CBE Core Inflation indexing (capped at 15%). |
| **Moats & Defensibility** | Bilingual Arabic TrOCR, official EEAA/NREA factor baselines (`0.4580 tCO2e/MWh`), Law 151/2020 sovereign hosting, and "The Auditor's Room" ISO 14064-3 cleanroom. |

---

## Proposed Changes & Phased Execution Roadmap

```
┌────────────────────────────────────────────────────────────────────────┐
│                      The 7-Milestone Build Journey                     │
├────────────────────────────────────────────────────────────────────────┤
│ Milestone 1: PostgreSQL Persistence, RLS & Ledger Engine Integration   │
│ Milestone 2: Bilingual Document Ingestion, OpenCV & TrOCR Pipeline     │
│ Milestone 3: Live Market Feeds, TOU Tariffs & Regulatory Crawlers      │
│ Milestone 4: Product Carbon Footprint (PCF) & EU CBAM Engine           │
│ Milestone 5: FRA Decrees 107/108 & Decision 36 Compliance Exporter     │
│ Milestone 6: High-Performance Industrial Frontend (Next.js / ISA-101)  │
│ Milestone 7: End-to-End System Integration, Verification & Pitch Demo  │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Milestone 1: PostgreSQL Persistence, RLS & Ledger Integration
**Goal:** Transition from the in-memory `api/store.py` to a production PostgreSQL 16 persistence layer using SQLAlchemy / SQLModel, enforcing multi-tenant Row-Level Security (RLS) and immutable double-entry ledger postings with SHA-256 cryptographic state chaining.

#### [NEW] [`ecoaudit/db/session.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/db/session.py)
- Asynchronous PostgreSQL engine and session factory with connection pooling.
- Context manager setting `SET LOCAL app.current_tenant_id = :tenant_id` for RLS.

#### [NEW] [`ecoaudit/db/models.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/db/models.py)
- SQLAlchemy ORM mappings reflecting the 6 migration schemas in `database/schemas/` (`Tenant`, `Facility`, `EmissionFactor`, `ActivityData`, `CarbonJournalEntry`, `CarbonLedgerPosting`, `AuditTrail`).

#### [MODIFY] [`api/store.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/api/store.py)
- Refactor `RunStore` to persist activity runs, ledger postings, and audit traces directly into PostgreSQL with fallback to SQLite for local development/testing.

#### [NEW] [`tests/test_db_persistence.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/tests/test_db_persistence.py)
- TDD tests verifying multi-tenant RLS isolation, immutable append-only triggers, and SHA-256 hash recalculation across ledger sequences.

---

### Milestone 2: Bilingual Document Ingestion, OpenCV & TrOCR Pipeline
**Goal:** Implement the physical paper ingestion pipeline handling Arabic utility invoices from South/North Cairo Electricity Distribution Co., fuel chits, and PDF invoices.

#### [NEW] [`ecoaudit/ocr/preprocessor.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/ocr/preprocessor.py)
- OpenCV image cleanup: Radon-transform deskewing, Otsu adaptive thresholding for binarization, and morphological filtering.

#### [NEW] [`ecoaudit/ocr/extractor.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/ocr/extractor.py)
- Bilingual vision-language extraction using Google GenAI / Gemini Vision and TrOCR.
- Eastern Arabic numeral normalizer (`٠, ١, ٢, ٣, ٤, ٥, ٦, ٧, ٨, ٩` $\to$ `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`).

#### [NEW] [`ecoaudit/ocr/validator.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/ocr/validator.py)
- Reading delta mathematical consistency check ($(\text{Current} - \text{Previous}) \times \text{Multiplier} = \text{Consumption}$).
- Automated quarantine router to `hitl_review_queue` for confidence $< 0.92$ or meter mismatches.

#### [NEW] [`tests/test_ocr_pipeline.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/tests/test_ocr_pipeline.py)
- Unit tests verifying Eastern numeral normalization, deskew math, and HITL quarantine logic.

---

### Milestone 3: Live Market Feeds, TOU Tariffs & Regulatory Crawlers
**Goal:** Implement continuous economic feeds and dynamic industrial electricity pricing for Egyptian factories.

#### [NEW] [`ecoaudit/feeds/live_market.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/feeds/live_market.py)
- CBE daily official exchange rates (EGP/EUR, EGP/USD).
- European Energy Exchange (EEX) live spot EU ETS EUA price feed (€/tCO2e) for real-time CBAM financial exposure.

#### [NEW] [`ecoaudit/carbon/tariffs.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/carbon/tariffs.py)
- EgyptERA industrial Time-of-Use (TOU) tariff engine: Ultra-High, High, Medium, and Low voltage tiers with summer peak hour multipliers (19:00–23:00).

#### [NEW] [`ecoaudit/crawlers/regulatory_monitor.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/crawlers/regulatory_monitor.py)
- Scheduled DOM hash diffing for EgyptERA portal and Ministry of Petroleum announcements to alert admins of official decree changes.

#### [NEW] [`tests/test_tariffs_and_feeds.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/tests/test_tariffs_and_feeds.py)
- Tests verifying peak vs. off-peak tariff math, CBE FX conversion, and crawler diff detection.

---

### Milestone 4: Product Carbon Footprint (PCF) & EU CBAM Declarations Engine
**Goal:** Implement bottom-up industrial PCF calculations at the Bill of Materials (BOM) level for Egyptian steel, aluminum, cement, and fertilizer exporters facing definitive CBAM compliance.

#### [NEW] [`ecoaudit/cbam/models.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/cbam/models.py)
- Dataclasses for 8-digit CN products, BOM line items, production routing machine hours, and Specific Embedded Emissions ($SEE_g$).

#### [NEW] [`ecoaudit/cbam/calculator.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/cbam/calculator.py)
- Recursive BOM material footprint aggregator: $PCF_{\text{materials}} = \sum (q_i \times PCF_{C_i})$.
- Capacity-hour production step allocator: $PCF_{\text{step}, k} = \frac{E_{CC_k}}{\text{Capacity Hours}_k} \times \tau_k$.
- Scrap rate adjustment factor: $PCF_{\text{cumulative}} = \frac{PCF_{\text{materials}} + \sum PCF_{\text{step}}}{\eta_{\text{line}}}$.
- Sector rules: Annex II (exclude indirect electricity) vs. Annex IV (include indirect electricity).
- Strict validation that default values do not exceed the 20% European Commission ceiling.

#### [NEW] [`ecoaudit/cbam/exporter.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/cbam/exporter.py)
- European Commission quarterly CBAM XML declaration generator.

#### [NEW] [`tests/test_cbam_engine.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/tests/test_cbam_engine.py)
- Unit tests on synthetic steel and fertilizer production routes verifying Annex II/IV rules, 20% default limit checks, and XML generation.

---

### Milestone 5: Egyptian Compliance & Market Integration Engine
**Goal:** Implement compliance export for Egyptian Financial Regulatory Authority (FRA) mandates and EGX voluntary carbon market CERC retirement.

#### [NEW] [`ecoaudit/compliance/fra_exporter.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/compliance/fra_exporter.py)
- Formats ledger debits into official FRA Decrees 107/108 KPI tables (E1-GHG-S1, E1-GHG-S2, E1-GHG-INT, E2-ENG-DIR, E2-ENG-IND, G1-BRD-DIV).
- Calculates the mandatory 20% CERC offset under FRA Decision 36/2026: $\lceil 0.20 \times (S1 + S2) \rceil$.

#### [NEW] [`ecoaudit/compliance/auditors_room.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/compliance/auditors_room.py)
- Backend endpoints for "The Auditor's Room": generates time-limited, scoped read-only tokens for accredited VVBs (SGS, TÜV, Petrosafe).
- One-click calculation lineage service tracing aggregated figures back to raw invoice scans and SHA-256 chain verification.
- Automated ISO 14064-3 verification dossier compiler (ZIP archive).

#### [NEW] [`tests/test_compliance_engine.py`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/tests/test_compliance_engine.py)
- Tests verifying FRA Decision 36 offset calculation, disclosure tables, and auditor cleanroom token security.

---

### Milestone 6: High-Performance Industrial Frontend (Next.js 15 / ISA-101)
**Goal:** Build the user-facing web dashboard connecting to `api/main.py`, adhering to the ANSI/ISA-101.01 standard and the 5 SAP enterprise reference designs.

#### Directory: `frontend/` (Next.js 15, Tailwind CSS, Tremor, D3.js)
- **Level 1 Display (Executive & Site Overview):**
  - Dark neutral gray (`#2B2B2B`), report-by-exception styling.
  - Gross GHG footprint card, Scope 1/2/3 breakdown, financial carbon intensity, countdown to FRA June 30 and CBAM quarter deadlines.
- **Level 2 Display (Facility & Process Workspace):**
  - Interactive Egyptian industrial zone switcher (10th of Ramadan, 6th of October, Sadat City).
  - Sub-meter load curves with peak vs. off-peak tariff shading.
- **Level 3 Display (Equipment Faceplates & Ingestion Review):**
  - Drag-and-drop bill upload with side-by-side OCR bounding box inspector.
  - HITL review quarantine dashboard with Select-Before-Operate (SBO) confirmation.
- **Level 4 Display ("The Auditor's Room" & Lineage Explorer):**
  - Interactive D3 Directed Acyclic Graph (DAG) tracing high-level disclosures down to invoices.
  - Live SHA-256 cryptographic chain validator with tamper-status badge.
  - One-click CBAM XML and FRA compliance package download modals.

---

### Milestone 7: End-to-End System Integration, Verification & Pitch Demo
**Goal:** Complete integration testing with realistic Egyptian industrial benchmark datasets, full regression passes, and preparation of the competition demo flow.

- Seed realistic demo datasets for two anchor Egyptian profiles:
  1. `Ezz_Steel_Ain_Sokhna_CBAM.csv`: EAF steel production, scrap rates, natural gas DRI, EU export billets.
  2. `CI_Leasing_FRA_Decision36.csv`: NBFI corporate headquarters, fleet fuel, SCEDC electricity bills, 20% CERC offset mandate.
- Full end-to-end automated verification across REST API, database, and export engines.
- Calibrate the 5:45 competition pitch deck with live interactive demo checkpoints.

---

## Verification Plan

### Automated Test Gates
For every milestone, execution follows TDD:
1. Write failing test in `tests/`.
2. Run test to verify expected failure.
3. Write minimal implementation.
4. Run test to confirm green.
5. Verify zero regression across previous test suites:
```bash
python3 -m pytest -v tests/
```

### Manual Verification Gates
- Verify live PostgreSQL connection and RLS tenant data separation.
- Ingest a sample Arabic South Cairo utility invoice image and confirm correct parsing of Eastern Arabic numerals and meter serial.
- Verify that a manipulated ledger entry breaks the SHA-256 state chain and triggers a red alarm in "The Auditor's Room".
- Inspect generated EU CBAM XML against official European Commission schema validators.
