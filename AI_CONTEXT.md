# EcoAudit AI — Complete AI Context Document
**Version:** September 2026 | **Package Version:** `0.1.0` | **Status:** Backend Core & REST API Complete | UI/UX Specification Ready

---

## 🧭 Table of Contents
1. [Business Context](#1-business-context)
2. [Architecture Overview](#2-architecture-overview)
3. [Current Project Status](#3-current-project-status)
4. [Recent Major Updates (September 2026)](#4-recent-major-updates-september-2026)
5. [Repository Structure](#5-repository-structure)
6. [Module-by-Module Reference](#6-module-by-module-reference)
7. [API Specification (FastAPI)](#7-api-specification-fastapi)
8. [Industrial UI/UX Conventions & Enterprise Architecture](#8-industrial-uiux-conventions--enterprise-architecture)
9. [Data & Emission Factors](#9-data--emission-factors)
10. [Test Suite](#10-test-suite)
11. [AI Evaluation Results](#11-ai-evaluation-results)
12. [Key Design Decisions & Rules](#12-key-design-decisions--rules)
13. [Known Gaps & Limitations](#13-known-gaps--limitations)
14. [Next Steps Roadmap](#14-next-steps-roadmap)
15. [Development & Execution Guide](#15-development--execution-guide)

---

## 1. Business Context

### What is EcoAudit AI?
**EcoAudit AI** is the first AI-powered ESG & Carbon Optimization SaaS platform targeting the **Egyptian and MENA export market**. The primary commercial catalyst is the **EU CBAM (Carbon Border Adjustment Mechanism)** — Egyptian manufacturers exporting to Europe (cement, steel, aluminum, fertilizers, textiles) face mandatory carbon footprint accounting or severe carbon tariffs / loss of EU contracts.

### The Problem We Solve
| Pain Point | Traditional Way | EcoAudit AI |
|---|---|---|
| Carbon reporting | Tens of thousands of USD to consultants, 4–8 weeks | Automated, auditor-ready in seconds |
| Data chaos | Scattered across ERPs, messy Excels, paper invoices | Smart CSV normalization + AI classification firewall |
| No actionable insight | Calculators only say *how much* you emitted | AI Consultant simulates dual-impact cost + carbon reduction |
| Legal risk | Hallucinated math from pure LLM tools | 100% deterministic Python calculation with immutable audit traces |

### Business Model
- **B2B SaaS Subscription** — tiered monthly pricing by company size, facility count, and data volume
- **Pay-per-Report** — one-off compliance reports for SME exporters exporting specific shipments

---

## 2. Architecture Overview

### The End-to-End Pipeline

```
Raw CSV / Excel Upload (via Web or REST API)
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ Ingestion & Normalizer (ecoaudit/ingestion/normalizer.py)   │
│  • Dialect detection, column header normalization           │
│  • Public dataset heuristics (Chicago Energy, Austin Fleet) │
│  • Synthetic/ERP messy column extraction                    │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ AI Classification Pipeline (ecoaudit/ai/)                   │
│  • GeminiClassifier (real API) / MockClassifier (test)      │
│  • Post-AI Validation Firewall (validate_candidate)         │
│  • Enforces valid GHG scopes, categories, units, quantities │
│  • Outputs: validated ActivityData objects                  │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ Deterministic Carbon Calculator (ecoaudit/carbon/)          │
│  • Unit normalization & compatibility checking              │
│  • Formula: emissions = normalized_quantity × factor_value   │
│  • Generates immutable CalculationTrace for external audit  │
│  • Outputs: BatchResult (scope totals, category totals)     │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ Carbon Intelligence Layer (ecoaudit/intelligence/)          │
│  • Aggregation: scope, category, activity, facility         │
│  • Hotspot identification (≥5% threshold, severity ranking) │
│  • Pareto concentration analysis & temporal trend detection │
│  • Structured insights (NOT LLM hallucinations)             │
│  • Outputs: CarbonIntelligenceReport                        │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ Optimization & Scenario Engine (ecoaudit/optimization/)     │
│  • Interventions: PercentageReduction, AbsoluteReduction,   │
│    FuelSubstitution (with physical conversion multipliers)  │
│  • Reruns CarbonCalculator deterministically on scenarios   │
│  • Dual-Impact: computes kgCO2e reduction AND cost savings  │
│  • Outputs: ScenarioResult & ScenarioComparison             │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ AI Recommendation Engine (ecoaudit/recommendation/)         │
│  • AI proposes candidate interventions from hotspots        │
│  • Deterministic verification via ScenarioEngine            │
│  • AI writes human-readable executive explanation           │
│  • Statuses: SUPPORTED, REQUIRES_REVIEW, or REJECTED        │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ Presentation & Delivery Layer                               │
│  • FastAPI REST Endpoints (api/main.py)                     │
│  • CLI Runner (scripts/run_pipeline.py)                     │
│  • Frontend Dashboard (Next.js — Next Phase)                │
└─────────────────────────────────────────────────────────────┘
```

### Core Design Principle — "AI is NOT the Calculator"
> **The AI classifies unstructured data and drafts narrative explanations. Deterministic Python `Decimal` code executes all mathematical operations.**
> The exact same inputs + same factor version = the exact same result, always. Every calculation is backed by an immutable [`CalculationTrace`](file:///Users/mezzo/Downloads/EcoAudit-ImpactX-main/ecoaudit/carbon/models.py).

---

## 3. Current Project Status

| Component | Layer | Status | Notes |
|---|---|---|---|
| **Phase 1: Carbon Core** | Python Library | ✅ Complete | GHG Protocol Scopes 1-3, `Decimal` precision, unit conversion engine |
| **Phase 2: Factor Registry** | Python Library | ✅ Complete | Temporal versioning, country/year lookup, DEFRA 2024 factors |
| **Phase 3: Ingestion** | Python Library | ✅ Complete | CSV normalizer + Chicago, Austin, and Synthetic adapters |
| **Phase 4: Calculator** | Python Library | ✅ Complete | Deterministic multiplication, unit normalization, `CalculationTrace` |
| **Phase 5: Intelligence** | Python Library | ✅ Complete | Hotspots (≥5%), Pareto concentration, trends, structured insights |
| **Phase 6: Scenarios** | Python Library | ✅ Complete | 3 intervention types, dual-impact (carbon kgCO2e + financial $) |
| **Phase 7: AI Recommender**| Python Library | ✅ Complete | Propose → verify → explain loop with status tracking |
| **Orchestration** | Core Library | ✅ Complete | `ecoaudit/pipeline.py` provides unified `execute_pipeline()` |
| **REST API** | Web Service | ✅ Complete | FastAPI app with `/runs`, `/activities`, `/evidence`, `/scenarios` |
| **UI/UX Engineering Spec** | Design Docs | ✅ Complete | `Factory Systems UI_UX Conventions.pdf` (ISA-101 industrial HMI) |
| **Enterprise UI References**| Design Assets | ✅ Complete | 5 SAP enterprise sustainability dashboard reference designs |
| **Frontend Web App** | Web UI (Next.js) | ⏳ In Planning | Scheduled next, leveraging ISA-101 and SAP references |
| **Production Factor DB** | Data Engine | ⏳ In Planning | Official EgyptERA/IEA factors needed to replace test data |
| **Persistent DB (Postgres)**| Infrastructure | ⏳ In Planning | Current run store is in-memory |

---

## 4. Recent Major Updates (September 2026)

1. **FastAPI REST API Layer Implemented (`api/`)**:
   - Built a complete, production-ready FastAPI backend (`api/main.py`) with CORS configured for modern web clients (`http://localhost:3000`).
   - Standardized Pydantic DTO schemas in `api/schemas.py` and dataclass serializers in `api/serializers.py`.
   - In-memory asynchronous `RunStore` (`api/store.py`) handling multi-step run lifecycles (`pending` → `running` → `complete` / `failed`).
   - Comprehensive API test suite (`tests/test_api.py`) and robustness edge-case test suite (`tests/test_robustness.py`).

2. **Unified Pipeline Orchestration (`ecoaudit/pipeline.py`)**:
   - Centralized all 7 pipeline stages into `execute_pipeline()`, eliminating duplication between CLI scripts and HTTP handlers.
   - Preserves complete `PipelineExecution` state containing raw rows, classification records, validation metrics, batch results, intelligence reports, and recommendations.

3. **Smart Ingestion Normalizer (`ecoaudit/ingestion/normalizer.py`)**:
   - Auto-detects dialects, handles BOM headers, strips noise, and heuristically normalizes varying CSV formats (including Chicago Benchmarking and Austin Fleet).

4. **Large Real-World Datasets Ingested**:
   - `Chicago_Energy_Benchmarking_20260909.csv` (28,334 real facility rows).
   - `data/demo/competition_demo.csv` (34 curated demo rows).

5. **Industrial UI/UX Engineering Manual & Enterprise Design Assets**:
   - Ingested `Factory Systems UI_UX Conventions.pdf` (22 pages): codified ISA-101/ISA-18.2 standards for high-performance industrial interfaces, 4-tier display hierarchy, and alarm management.
   - Added 5 high-resolution enterprise UI mockups (SAP Sustainability Control Tower / Footprint Management) defining exact expectations for the upcoming Frontend phase.

6. **Superpowers Engineering Methodology & Discipline**:
   - Installed 8 core Superpowers skills in `.agents/skills/` (`using-superpowers`, `test-driven-development`, `systematic-debugging`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `verification-before-completion`, `brainstorming`).
   - Codified `GEMINI.md` enforcing the Iron Law of TDD, Root-Cause-First Debugging, and Evidence Before Completion.

7. **Production PostgreSQL 16+ Database Schemas (`database/schemas/`)**:
   - `001_core_and_tenancy.sql`: Multi-tenant isolation (RLS), facility registers across Egyptian industrial zones, users, RBAC.
   - `002_emission_factors.sql`: Versioned factor registry, EEAA/NREA Egyptian grid factor (`0.4580 tCO2e/MWh`), EGPC industrial fuel calorific standards, freight logistics factors.
   - `003_activity_and_ingestion.sql`: Raw document stores, OCR bilingual extraction tables, HITL review queue (confidence < 0.92), activity batches.
   - `004_double_entry_carbon_ledger.sql`: Chart of Carbon Accounts (COCA), balanced debit/credit journal entries, append-only immutability trigger, SHA-256 cryptographic state chaining function.
   - `005_cbam_and_pcf.sql`: EU 8-digit CN codes, recursive bills of materials with scrap rates, production routing capacity hours, Specific Embedded Emissions ($SEE_g$), quarterly CBAM filings.
   - `006_compliance_and_audit.sql`: FRA Decrees 107/108 & Decision 36/2026 filings (20% CERC offset mandate), CERC order settlement, verifier cleanroom sessions ("The Auditor's Room"), audit trails.

8. **Enterprise Architecture & System Specifications (`docs/architecture/`)**:
   - `01_reverse_engineering_giants.md`: Persefoni/Watershed DAG calculation graphs, double-entry carbon ledger mechanics, SHA-256 state hashing, SAP SFM recursive BOM PCF formulas, ERP connectors, enterprise pricing.
   - `02_egyptian_regulatory_framework.md`: FRA Decrees 107/108/36, EGX voluntary carbon market trading (Decrees 30/31/1732 of 2024), EOS ISO 14064 alignment, Egyptian grid/fuel factor baselines, EU CBAM definitive compliance.
   - `03_system_architecture_and_tech_stack.md`: Bilingual Arabic/English TrOCR pipeline (North/South Cairo bills, Eastern Arabic numerals), HITL queue, FastAPI + PyO3 Rust vector engine, Next.js/Tailwind/ISA-101 UI, ERP connectors (SAP S/4HANA, Odoo).
   - `04_legal_licensing_sovereignty.md`: Egyptian S.A.E. incorporation (Law 72/2017), ITIDA/MCIT IP registration (Law 15/2004), Law 151/2020 Data Protection (DPO, cross-border restrictions), NTRA Tier 3 sovereign cloud hosting, "Auditor's Room" virtual cleanroom.
   - `05_business_model_and_gtm_egypt.md`: Expanded 4 customer segments, EGP hybrid SaaS pricing + advisory retainer with inflation indexing, FEI & D-Carbon channel alliances, 10th of Ramadan & 6th of October beachhead, $80k vs. $24k ROI calculation, and 5:45 pitch strategy.
   - `06_autonomous_agent_blueprint.md`: System architecture Mermaid.js flowchart and complete, runnable Python calculation engine implementation (utility bill → Scope 2 → double-entry ledger with SHA-256 state hashing → FRA compliance report).

---

## 5. Repository Structure

```
EcoAudit-ImpactX-main/
│
├── .agents/skills/              # ⭐ Superpowers Engineering Skills (8 Core Skills)
│
├── api/                         # ⭐ FastAPI REST Service (Complete)
│   ├── __init__.py
│   ├── main.py                  # App entry point, CORS, routes (/runs, /scenarios, etc.)
│   ├── schemas.py               # Pydantic DTOs for requests and responses
│   ├── serializers.py           # Translates internal domain dataclasses to JSON DTOs
│   └── store.py                 # Thread-safe in-memory session run store
│
├── frontend/                    # ⭐ Next.js 15 App (ANSI/ISA-101.01 High-Performance HMI)
│   ├── src/app/                 # App Router pages (/, /runs/[runId], activities, evidence, scenarios)
│   ├── src/components/          # ISA-101 UI components, Dashboard cards, Activity grid, Evidence panel
│   ├── src/hooks/               # Real-time useRunStatus polling hook (600ms)
│   ├── src/lib/                 # Types matching backend DTOs & type-safe apiClient
│   └── __tests__/               # Vitest unit test suite (14 tests passing)
│
├── database/                    # ⭐ Production Database Schemas & Migrations (Complete)
│   └── schemas/
│       ├── 001_core_and_tenancy.sql
│       ├── 002_emission_factors.sql
│       ├── 003_activity_and_ingestion.sql
│       ├── 004_double_entry_carbon_ledger.sql
│       ├── 005_cbam_and_pcf.sql
│       └── 006_compliance_and_audit.sql
│
├── docs/
│   ├── artifacts/               # ⭐ Exported System Artifacts & Metadata
│   ├── architecture/            # ⭐ Complete Technical PRD & Architecture Specs (6 Modules)
│   │   ├── 01_reverse_engineering_giants.md
│   │   ├── 02_egyptian_regulatory_framework.md
│   │   ├── 03_system_architecture_and_tech_stack.md
│   │   ├── 04_legal_licensing_sovereignty.md
│   │   ├── 05_business_model_and_gtm_egypt.md
│   │   └── 06_autonomous_agent_blueprint.md
│   ├── ECOAUDIT_MASTER_PROJECT_DOCUMENT.md # ⭐ Master All-in-One Enterprise PRD & Specification
│   ├── FUTURE_VISION.md         # ⭐ Real-Time Factory IoT & CEMS Telemetry Architecture
│   ├── PITCH_STRATEGY.md        # ⭐ 10-Slide Deck, 5:45 Verbal Pitch Script & Q&A Defense
│   ├── carbon_intelligence.md   # Phase 5 methodology & mathematical specifications
│   └── optimization.md          # Phase 6 scenario calculation methodology
│
├── ecoaudit/                    # Core Python Domain Engine
│   ├── __init__.py              # Package init (v0.1.0)
│   ├── pipeline.py              # ⭐ Unified pipeline execution & PipelineExecution dataclass
│   │
│   ├── carbon/                  # Phases 1 & 4: Core calculation
│   │   ├── calculator.py        # CarbonCalculator (deterministic multiplication & trace)
│   │   ├── data_loader.py       # JSON factor loader into registry
│   │   ├── factors.py           # EmissionFactorRegistry + DEFRA 2024 test factors
│   │   ├── models.py            # ActivityData, EmissionFactor, CalculationResult, Trace
│   │   ├── scopes.py            # GHG Scope & Category enums
│   │   ├── units.py             # Unit enum & deterministic conversion math
│   │   └── validation.py        # Pre-calculation input validation
│   │
│   ├── ingestion/               # Phase 3: Ingestion & Normalization
│   │   ├── normalizer.py        # ⭐ Smart CSV reader & column heuristic mapper
│   │   ├── adapters.py          # ChicagoEnergyAdapter, AustinFleetAdapter, SyntheticAdapter
│   │   └── core.py              # Ingestion utilities
│   │
│   ├── ai/                      # Phase 2: AI Classification & Firewall
│   │   ├── gemini_provider.py   # GeminiClassifier & GeminiClient (Google GenAI SDK)
│   │   ├── mock_provider.py     # Deterministic MockClassifier for testing/offline
│   │   ├── pipeline.py          # ClassificationPipeline (orchestrates classify + validate)
│   │   ├── prompts.py           # Production prompt engineering with few-shot examples
│   │   ├── providers.py         # AIClassifier / AIClient Protocol definitions
│   │   ├── schemas.py           # ActivityCandidate schema & JSON response parser
│   │   └── validation.py        # Post-AI validation firewall (rejects bad units/quantities)
│   │
│   ├── intelligence/            # Phase 5: Carbon Intelligence
│   │   ├── aggregation.py       # Grouping by scope, category, activity, facility
│   │   ├── analyzer.py          # CarbonAnalyzer orchestrator
│   │   ├── hotspots.py          # Material hotspot identification (≥5% threshold)
│   │   ├── insights.py          # Deterministic evidence-based analytical findings
│   │   ├── models.py            # CarbonInsight, Hotspot, ScopeBreakdown, ParetoResult
│   │   └── trends.py            # Multi-period trend and change analysis
│   │
│   ├── optimization/            # Phase 6: Scenario Engine
│   │   ├── comparison.py        # Scenario ranking & comparison
│   │   ├── engine.py            # ScenarioEngine (reruns calculator on modified activities)
│   │   ├── interventions.py     # PercentageReduction, AbsoluteReduction, FuelSubstitution
│   │   └── models.py            # ScenarioDefinition, ScenarioResult, Carbon/FinancialImpact
│   │
│   └── recommendation/          # Phase 7: AI Recommendations
│       ├── engine.py            # RecommendationEngine (propose → verify → explain)
│       ├── models.py            # Recommendation, RecommendationStatus, Evidence
│       ├── prompts.py           # Prompts for candidate proposals and explanation
│       └── schemas.py           # Parsing AI candidate JSON responses
│
├── data/
│   ├── demo/                    # Demo and benchmark files
│   │   ├── competition_demo.csv # Curated 34-row competition dataset
│   │   ├── synthetic_test_dataset.csv
│   │   ├── synthetic_company_data.csv
│   │   └── small_test.csv
│   ├── factors/                 # Emission factor JSON databases
│   │   ├── defra_2024.json      # Official UK DEFRA 2024 factors
│   │   └── egypt_mena_proxy.json# Approximate Egyptian grid factors (0.50 kgCO2e/kWh)
│   ├── raw/                     # Public test datasets
│   └── evaluation/              # AI accuracy benchmarking data
│
├── docs/
│   ├── carbon_intelligence.md   # Phase 5 methodology & mathematical specifications
│   └── optimization.md          # Phase 6 scenario calculation methodology
│
├── scripts/
│   ├── run_pipeline.py          # ⭐ Unified CLI for running pipeline end-to-end
│   ├── demo_end_to_end.py       # Full pipeline demonstrator
│   ├── demo_intelligence.py     # Intelligence layer demonstrator
│   ├── demo_optimization.py     # Scenario engine demonstrator
│   ├── demo_recommendation.py   # AI recommendation engine demonstrator
│   ├── compare_baseline.py      # Compare Mock vs Gemini outputs
│   ├── evaluate_ai.py           # Benchmark AI classifier accuracy
│   └── validate_datasets.py     # Validate ingestion adapters
│
├── tests/                       # 23 test suites (unit, integration, API, robustness)
│   ├── test_api.py              # ⭐ FastAPI endpoint integration tests
│   ├── test_robustness.py       # ⭐ Malformed CSV & boundary tests
│   ├── test_calculator.py       # Deterministic calculator tests
│   ├── test_ai_pipeline.py      # AI classification pipeline tests
│   ├── ... (and 19 more test files)
│
├── validation/                  # Validation reports & accuracy metrics
├── Chicago_Energy_Benchmarking_20260909.csv # 28k-row benchmarking dataset
├── Factory Systems UI_UX Conventions.pdf     # 22-page industrial HMI/ISA-101 design spec
├── 1780332773284.png ... 1780333075006.png  # 5 SAP enterprise dashboard reference mockups
├── pyproject.toml               # Project dependencies (FastAPI, Uvicorn, pytest, etc.)
└── AI_CONTEXT.md                # ⭐ Comprehensive AI context reference (this document)
```

---

## 6. Module-by-Module Reference

### 6.1 `ecoaudit/pipeline.py` (Unified Orchestrator)
- **`execute_pipeline(input_path, provider, year, country, on_progress)`**: Executes the full 7 stages on any CSV. Returns a comprehensive `PipelineExecution` object containing:
  - `statistics`: Total rows, classified rows, validated rows, rejected rows, calculated rows, coverage percentage.
  - `validated_activities`: Clean `ActivityData` ready for auditing.
  - `batch_result`: Total emissions and scope totals.
  - `intelligence`: Hotspots, Pareto breakdowns, insights.
  - `recommendations`: Verified AI recommendations with carbon and cost impact.

### 6.2 `ecoaudit/ingestion/normalizer.py` (Smart CSV Normalizer)
- **`read_csv_rows(filepath_or_buffer)`**:
  - Automatically handles UTF-8, UTF-8-BOM, Latin-1 encodings.
  - Uses `csv.Sniffer` for delimiter detection (comma, semicolon, tab).
  - Matches column aliases (e.g., "Electricity Use (kBtu)", "Power Bill", "Gallons", "Usage Amount") and attaches normalized metadata without losing the raw source fields.

### 6.3 `ecoaudit/carbon/` (Deterministic Math Engine)
- **Formula:** `emissions = normalized_quantity × factor.value`
- Uses `Decimal` exclusively to avoid floating-point errors.
- **`CarbonCalculator.calculate()`**: Validates inputs, normalizes units (via `ecoaudit/carbon/units.py`), performs calculation, and attaches an immutable `CalculationTrace`.
- **`EmissionFactorRegistry`**: Indexes factors by `(activity_type, year, source, country)`. Enforces strict temporal matching — no calculating 2022 emissions with 2024 factors unless explicitly overridden.

### 6.4 `ecoaudit/ai/` (Classification & Safety Firewall)
- **`GeminiClassifier`**: Uses Google GenAI SDK (`gemini-3.6-flash`) with structured JSON schema output and few-shot guidance.
- **`MockClassifier`**: Deterministic rule-based classifier for offline testing.
- **`validate_candidate()` (The Firewall)**: Evaluates raw AI outputs:
  - Quantity must be positive numeric `Decimal`.
  - Unit must exist in `Unit` enum.
  - Scope and Category must match GHG Protocol definitions.
  - Incompatible or hallucinated pairs are rejected immediately before reaching the calculator.

### 6.5 `ecoaudit/intelligence/` (Analytics & Hotspots)
- **`CarbonAnalyzer.analyze()`**:
  - Calculates contribution percentages across scopes, categories, and facilities.
  - **Hotspot Detection**: Sources accounting for ≥5% of total footprint. Classifies severity (`CRITICAL` ≥25%, `HIGH` ≥10%, `MEDIUM` ≥5%) and actionability (`Scope 1/2` = Actionable, `Scope 3` = Influencable).
  - **Pareto Concentration**: Measures how few sources generate 80% of emissions.
  - **Structured Insights**: Generates typed analytical findings (e.g., `SCOPE_DOMINANCE`, `SINGLE_SOURCE_DOMINANCE`).

### 6.6 `ecoaudit/optimization/` (Scenario Engine)
- Simulates operational interventions:
  - `PercentageReduction(percentage)`
  - `AbsoluteReduction(amount)`
  - `FuelSubstitution(new_activity, new_unit, conversion_multiplier)`
- Recalculates modified activities deterministically using the same `CarbonCalculator`.
- Computes `CarbonImpact` (absolute & % reduction) and `FinancialImpact` (savings $, only if cost metadata is present).

### 6.7 `ecoaudit/recommendation/` (AI Advisory)
- Proposes candidates from identified hotspots.
- Passes candidates to `ScenarioEngine` for deterministic verification.
- Rejects ungrounded proposals (`status = REJECTED`).
- If verified, prompts LLM to draft a clear, human-readable executive explanation.

---

## 7. API Specification (FastAPI)

The REST API service runs via `uvicorn api.main:app --reload` on port `8000`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/runs` | Upload CSV dataset, specify `provider` (`mock` or `gemini`), `year`, and `country`. Starts pipeline and returns `run_id`. |
| `GET` | `/runs/{run_id}` | Returns run status (`pending`, `running`, `complete`, `failed`). |
| `GET` | `/runs/{run_id}/summary` | Full summary: KPIs, scope breakdown, top hotspots, Pareto points, data quality, and recommendations. |
| `GET` | `/runs/{run_id}/activities` | Paginated list of ingested activities, their validation state, and calculated emissions. |
| `GET` | `/runs/{run_id}/evidence` | Audit-grade provenance trace for any specific activity (exact factor ID, formula, source URL). |
| `GET` | `/runs/{run_id}/recommendations`| Verified AI recommendations with dual carbon/cost impacts. |
| `POST` | `/runs/{run_id}/scenarios` | Custom "what-if" simulation: user supplies intervention parameters, returns deterministic impact. |

---

## 8. Industrial UI/UX Conventions & Enterprise Architecture

The workspace includes comprehensive design specifications for building the SaaS interface:
1. `Factory Systems UI_UX Conventions.pdf` (ISA-101 / ISA-18.2 standards)
2. 5 high-resolution SAP Sustainability Control Tower reference dashboards

### 8.1 Industrial Design Standards (from `Factory Systems UI_UX Conventions.pdf`)
- **ANSI/ISA-101.01 (High-Performance HMI)**:
  - **Report-by-Exception**: Use flat, desaturated neutral gray backgrounds (#C0C0C0 to #D4D4D4 for light, #2B2B2B to #383838 for dark). Saturated colors (red, amber, yellow) are reserved exclusively for abnormal process deviations, trips, and alarms.
  - **4-Level Display Hierarchy**:
    - **Level 1 (Site Overview)**: <5-second comprehension window. High-level KPIs, total mass balances, site alarm tallies. Read-only.
    - **Level 2 (Process Unit/Line)**: Primary operator workspace. Process flow, setpoint deviation sparklines, primary trend lines.
    - **Level 3 (Equipment Detail & Faceplates)**: Tactical troubleshooting, diagnostic views, interlock matrices.
    - **Level 4 (Diagnostics & Documentation)**: Audit logs, SOPs, raw I/O tables.
  - **Select-Before-Operate (SBO)**: Prohibits single-touch execution on high-consequence operations. Requires: Select item → Open context faceplate → Configure parameter → Explicit confirmation button.
  - **Physical Ergonomics**: Touch targets ≥10×10 mm for bare finger, ≥19×19 mm for gloved operators, with 3–5 mm inactive padding.

### 8.2 Enterprise Screen References (The 5 Reference PNGs)
1. **GHG & Financial KPI Dashboard (`1780332773284.png`)**:
   - Top KPI cards: Gross GHG Emissions (tCO2e), GHG Intensity on Operating Income, GHG Intensity on Net Revenue, Operating Income ($), Gross Margin ($).
   - Pie charts: Scope 1 breakdown (Stationary vs Mobile), Scope 2 (Purchased electricity/heat), Scope 3 (Waste, Logistics, Travel).
   - Data Quality breakdown: Primary measured data vs Secondary industry average vs Proxy data.
2. **Product Carbon Footprint & CBAM Download (`1780332773920.png`)**:
   - Product list with ERP ID, Supplier ID, **CN Code (Combined Nomenclature code for EU customs)**, reporting period, and carbon intensity (tCO2e/tonne).
   - Modal dialog for **"Download CBAM Reports"** with quarter selection, legal signature, and verification checkboxes.
3. **ESG Target vs. Actuals (`1780333073297.png`)**:
   - Environmental metric tiles with multi-year bar charts comparing Actual vs Target (2022–2025).
   - Scope 1, Scope 2, Scope 3, Carbon Credits, Emissions to Air/Water/Soil.
4. **Scope 3 Supplier Portal / Inbound Footprint (`1780333074180.png`)**:
   - Inbound purchased materials table with Product ID, Supplier ID, Activity Status (`Requested`, `Received`, `Not requested`), and Footprint Status (`Valid`, `No Data`).
   - Action drawer allowing one-click "Request Footprint" from upstream suppliers.
5. **Corporate CO2e Sankey Flow Diagram (`1780333075006.png`)**:
   - Sankey flow diagram tracking emissions from emission categories (Stationary Combustion, Electricity, Purchased Goods, Capital Goods) → Scopes 1, 2, 3 → Total Emissions → Allocation to finished sold products (e.g., Product A vs Product B) vs Non-Product overhead.

---

## 9. Data & Emission Factors

### Authoritative Datasets in Repository
- `data/factors/defra_2024.json`: Official UK Department for Energy Security and Net Zero (DESNZ) / DEFRA 2024 factors (Stationary Diesel, Mobile Diesel, Petrol, Natural Gas, UK Grid Electricity).
- `data/factors/egypt_mena_proxy.json`: Estimated Egyptian national grid factor (0.50 kgCO2e/kWh, based on ~88% fossil gas generation mix). Flagged as `is_test_data = true` to warn auditors.
- `Chicago_Energy_Benchmarking_20260909.csv`: 28,334 real facility rows for high-volume stress testing.
- `data/demo/competition_demo.csv`: 34 representative corporate rows.

---

## 10. Test Suite

The project includes **23 comprehensive test modules**:
- `tests/test_api.py`: FastAPI endpoints, file upload handling, run session retrieval, scenario simulation.
- `tests/test_robustness.py`: Handles malformed CSVs, empty rows, invalid headers, out-of-range parameters.
- `tests/test_calculator.py`: Validates deterministic `Decimal` math, trace generation, and batch aggregation.
- `tests/test_ai_pipeline.py`: Pipeline execution, classification tracking, validation rejection.
- `tests/test_ai_validation.py`: Unit tests for the post-AI security firewall.
- `tests/test_hotspots.py`, `tests/test_optimization.py`, `tests/test_recommendation.py`: Full domain tests.

---

## 11. AI Evaluation Results

From `validation/ai_evaluation_results.json` (evaluated against 100 labeled test records):
- **Activity Type Accuracy:** 82%
- **GHG Scope Classification Accuracy:** 91%
- **Category Classification Accuracy:** 85%
- **Physical Unit Normalization Accuracy:** 100%
- **Firewall Rejection / Review Rate:** Successfully caught 45% ambiguous records and flagged 55% for manual audit review.

---

## 12. Key Design Decisions & Rules

1. **Deterministic Calculation**: Never use an LLM to multiply numbers or calculate emissions. Code does math; AI provides semantic classification and narrative explanation.
2. **Immutable Traceability**: Every calculated number must retain its provenance: source document, emission factor version, year, and formula.
3. **No Financial Hallucination**: Financial savings are only calculated if explicit unit costs or invoices exist in activity metadata. The engine never guesses monetary savings.
4. **Temporal Consistency**: 2022 activity data must be mapped to 2022 emission factors.

---

## 13. Known Gaps & Limitations

1. **Production Egypt/MENA Emission Factors**: `egypt_mena_proxy.json` is an approximation. An audited production deployment requires official licensed factors from IEA or EgyptERA.
2. **Scope 3 Supply Chain Coverage**: Categories 1 (Purchased Goods) and 4 (Transportation) require expanded factor tables.
3. **In-Memory Run Store**: Current `RunStore` (`api/store.py`) stores sessions in memory. Needs migration to PostgreSQL with Redis for background queueing.
4. **OCR Engine**: Document OCR for PDF invoices/scanned receipts is not yet integrated into the automated ingestion route.

---

## 14. Next Steps Roadmap

### 🚀 Priority 1: Frontend MVP (Next.js SaaS Dashboard)
- **Goal:** Build the user-facing web platform connecting to `api/main.py`.
- **Architecture**: Next.js 14+ (App Router), Tailwind CSS, shadcn/ui.
- **Pages**:
  1. **Upload & Ingestion Screen**: Drag-and-drop CSV/Excel with real-time column mapping and AI validation confidence preview.
  2. **Executive ESG Dashboard (Level 1)**: High-performance HMI style (neutral grays, high contrast for alerts), showing Gross Footprint (tCO2e), Scope 1/2/3 breakdown, and financial intensity.
  3. **CBAM Product Manager**: Table with CN codes, product emissions (tCO2e/t), and a one-click **"Download CBAM Report"** modal matching `1780332773920.png`.
  4. **Interactive Optimization Playground (Level 2/3)**: Interactive sliders to adjust efficiency percentages or switch fuels, live-updating carbon and cost savings.
  5. **Sankey Emissions Allocation**: Visualizing emission flows from source to finished products matching `1780333075006.png`.

### 🚨 Priority 2: Production Emission Factors (Data Engine)
- License or ingest official IEA Egyptian grid emission factors.
- Ingest complete DEFRA 2024 & 2025 sets covering logistics, freight (GLEC framework), and materials.

### 🗄️ Priority 3: PostgreSQL Database & Persistence
- Replace `api/store.py` with SQLAlchemy / SQLModel + PostgreSQL.
- Add multi-tenant organization isolation (row-level security).
- Implement persistent immutable audit tables.

### 📄 Priority 4: CBAM-Compliant PDF Generator
- Generate officially formatted European Commission CBAM quarterly report templates with digital signature placeholders.

---

## 15. Development & Execution Guide

### Prerequisites
- Python ≥ 3.10 (compatible with 3.9+ via `__future__.annotations`)
- Standard dependencies: `pip install -e ".[dev]"`

### Running the REST API Service
```bash
uvicorn api.main:app --reload --port 8000
```
Interactive API documentation will be available at: `http://localhost:8000/docs`.

### Running the CLI Pipeline
```bash
# Run with Deterministic Mock AI
python scripts/run_pipeline.py data/demo/synthetic_test_dataset.csv --provider mock --year 2024 --country UK

# Run with Google Gemini AI
export GEMINI_API_KEY="your-api-key"
python scripts/run_pipeline.py data/demo/synthetic_test_dataset.csv --provider gemini --year 2024 --country UK
```

### Running Standalone Demonstrations
```bash
python scripts/demo_intelligence.py    # Hotspot & Pareto analysis
python scripts/demo_optimization.py    # Scenario simulation
python scripts/demo_recommendation.py  # AI recommendation loop
python scripts/demo_end_to_end.py      # Full 7-phase demo
```

---
*Last updated: September 10, 2026 — EcoAudit AI Engineering Team*
