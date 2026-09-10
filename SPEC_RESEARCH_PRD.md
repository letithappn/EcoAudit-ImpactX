You are acting as a Principal Climate-Tech Enterprise Architect, a B2B SaaS Venture Builder, and a Senior Egyptian Environmental Regulatory Lawyer. 

Our mission is to launch a next-generation corporate carbon accounting and ESG compliance SaaS platform specifically designed for the Egyptian market (the "Watershed / Persefoni / SAP Sustainability for Egypt"). 

Your output must serve as a comprehensive Technical PRD, System Architecture Specification, and Business Strategy Blueprint. It will be ingested directly into an autonomous AI agent to generate the codebase, database schemas, and compliance workflows.

Avoid generic summaries or high-level filler. Provide exhaustive, production-grade technical depth, concrete database schemas, calculation formulas, and step-by-step regulatory roadmaps across the following 6 modules:

---

### MODULE 1: Reverse Engineering the Global Giants (Watershed, Persefoni, SAP)
1. **Architecture & Calculation Engines:**
   - Deconstruct how Persefoni and Watershed build their calculation engines (GHG Protocol scopes 1, 2, and 3). 
   - How do they implement double-entry carbon ledgers, audit logging, and immutability (version control of emission factors)?
   - How does SAP Sustainability Footprint Management calculate Product Carbon Footprints (PCF) at the Bill of Materials (BOM) level?
2. **Data Ingestion & Extraction Pipelines:**
   - How do these platforms automate ingestion across structured data (ERP connectors like SAP/NetSuite, utility APIs) and unstructured data (travel manifests, PDF utility bills, procurement ledgers)?
3. **Business Model & GTM:**
   - Detailed teardown of their pricing structures (subscription tiers, asset-under-management/revenue-based pricing, platform fee vs. implementation services).
   - Enterprise sales cycles and land-and-expand strategies.

---

### MODULE 2: Egyptian Regulatory, Standards & Data Localization
1. **Financial Regulatory Authority (FRA) Mandates:**
   - Exhaustive analysis of FRA Decrees No. 107 & 108 (2021) and Decision No. 36 (2026) regarding ESG, TCFD, and carbon disclosures for EGX-listed companies and Non-Bank Financial Institutions (NBFIs).
   - What exact reporting templates, quantitative KPIs, and governance annexes does the FRA require?
   - How does Egypt’s regulated voluntary carbon market on the EGX work, and how can the software integrate direct carbon certificate procurement/retirement?
2. **Egyptian Organization for Standardization and Quality (EOS):**
   - National standards mirroring ISO 14064-1 (organizational inventories), ISO 14064-2 (project-level), ISO 14064-3 (verification/validation), and ISO 14067 (product carbon footprints).
   - What specific conformity criteria must an Egyptian software output fulfill to pass an EOS-aligned third-party audit?
3. **National Emission Factors & Grid Baselines (IEA, EEAA, NREA):**
   - Exact methodology to build and update the Egyptian National Emission Factor Database:
     * Location-based vs. Market-based Egyptian national electricity grid emission factor (tCO2e/MWh) using EEAA and NREA official data.
     * Egyptian fuel emission factors (Mazut, Solar/Diesel, Natural Gas, Octane 92/95) according to local calorific values.
     * Transport and logistics factors calibrated to the Egyptian vehicle fleet and distribution networks.
4. **EU CBAM Readiness for Egyptian Exporters:**
   - Calculation engine requirements to compute embedded direct and indirect emissions for Egyptian industrial exporters (steel, cement, aluminum, fertilizers) facing EU Carbon Border Adjustment Mechanism (CBAM) quarterly reporting.

---

### MODULE 3: Tailored Product Architecture & Tech Stack for Egypt
1. **Solving the "Dirty Data / Paper-Heavy" Reality:**
   - Architecture for a native Arabic & English OCR and document-parsing pipeline (handling photographed/scanned Egyptian paper electricity bills from South/North Cairo Electricity Distribution Co., handwritten fuel slips, and PDF procurement invoices).
   - Human-in-the-loop (HITL) review dashboard for anomaly detection and manual data validation.
2. **Recommended Technology Stack:**
   - **Backend:** High-performance, deterministic calculation engine (e.g., Python FastAPI / Go / Rust) capable of recalculating historical footprints upon emission factor updates.
   - **Frontend:** Modern, audit-friendly UI framework (Next.js/React, Tailwind, modular data visualization with Tremor/D3).
   - **Database Architecture:** Multi-tenant PostgreSQL with schema-level isolation, time-series data handling, and immutable audit logs.
   - Provide a complete **PostgreSQL Schema (DDL)** covering:
     * `tenants` and `facilities`
     * `activity_data` (energy, fuel, spend, travel)
     * `emission_factors` (with versioning, geographic tags, and source metadata)
     * `carbon_ledger_entries` (immutable debit/credit calculation outputs)
     * `audit_trails`
3. **API & Integration Layer:**
   - Connectors for local and enterprise ERPs (SAP S/4HANA, Odoo, Oracle, Microsoft Dynamics).

---

### MODULE 4: Egyptian Legal, Licensing, Data Sovereignty & Auditing
1. **Permits, Registrations & IP:**
   - Step-by-step roadmap to legally incorporate and register the software in Egypt (ITIDA registration, Intellectual Property deposit at the Ministry of Communications and Information Technology - MCIT).
   - Do software platforms need direct licensing from the FRA, Ministry of Environment (EEAA), or Supreme Council for Media Regulation?
2. **Data Residency & Cyber Laws:**
   - Compliance with Egyptian Personal Data Protection Law (Law No. 151 of 2020) and National Telecommunications Regulatory Authority (NTRA) cloud licensing requirements.
   - On-premise vs. Sovereign Cloud hosting recommendations within Egypt (e.g., local data centers, telecom clouds, or regional hyperscalers with Egyptian localization compliance).
3. **Audit Readiness & Third-Party Assurance:**
   - How to design the software’s output package (the "Auditor’s Room") so accredited verifiers (SGS Egypt, TÜV Nord, DNV, Bureau Veritas, and local FRA-registered verifiers) can review calculation lineage in one click.

---

### MODULE 5: Business Model, Pricing & Go-To-Market for the Egyptian Market
1. **Pricing Model:**
   - How to price in Egyptian Pounds (EGP) without cannibalizing margins: Hybrid model combining SaaS recurring software fees with a "Tech-Enabled Advisory" onboarding retainer.
   - Tiered pricing structure tailored for:
     * Mid-tier suppliers/manufacturers (SME tier)
     * EGX-listed corporations and NBFIs (Enterprise tier)
     * Heavy industrial exporters needing CBAM compliance (Export tier)
2. **Go-To-Market (GTM) Strategy:**
   - Partnership channel strategy with Egyptian accounting/auditing firms, ESG consultancies (e.g., D-Carbon), and business federations (Federation of Egyptian Industries - FEI).
   - Strategy to win early design partners in 10th of Ramadan, 6th of October, and Sadat City industrial zones.

---

### MODULE 6: Autonomous Agent Blueprint & System PRD Output
1. Provide a structured **System Architecture Flowchart** (in clear Mermaid.js format).
2. Write a production-ready **Calculation Engine Algorithm** in pseudocode or Python demonstrating how an uploaded utility bill (activity data) is converted into Scope 2 emissions, logged into an immutable carbon ledger, and formatted into an FRA compliance report.