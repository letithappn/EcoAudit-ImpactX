# Live Light MVP Implementation Plan (Stitch Frontend Design + Live CSV Upload)

Create a live, light-themed enterprise MVP web application faithfully implementing the **Stitch design system** (`stitch_ecoaudit_ai_decarbonization_platform`) with real end-to-end **CSV upload**, 1-click sample dataset quick loading (Option A), and dynamic binding to the backend carbon calculation engine.

## User Review Required

> [!IMPORTANT]
> **Stitch Design System Tokens**: The app will use the exact Stitch visual architecture:
> - Light canvas background (`#f8f9ff`) with crisp white elevated cards (`#ffffff`).
> - Fixed deep navy sidebar (`#0e1c2f`) with the official EcoAudit AI logo, "v3.4 Audited" badge, and 6 core views.
> - High-contrast royal blue (`#1d4ed8`) primary highlights and emerald green (`#069669`) audit/verification indicators.
> - Typography: Google Fonts `Plus Jakarta Sans`, `Inter`, and `Material Symbols Outlined`.

> [!NOTE]
> **Option A (Selected)**: The ingestion modal will feature a drag-and-drop custom CSV uploader plus 1-click Quick-Load buttons for existing repository datasets:
> 1. `Chicago Energy Benchmarking 2026` (Commercial real estate Scope 1 & 2)
> 2. `Competition Demo / Heavy Industry` (Egypt Steel & Aluminum Scope 1, 2 & 3)
> 3. `Fleet & Synthetic Logistics` (Mobile combustion & fuel telemetry)

---

## Proposed Changes

Grouped by layer and component:

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx              [MODIFY] (Inject Google Fonts & Material Symbols)
│   │   ├── globals.css             [MODIFY] (Add Stitch color tokens & typography classes)
│   │   └── page.tsx                [MODIFY] (Stitch shell state, view routing, run binding)
│   ├── components/
│   │   └── stitch/                 [NEW DIRECTORY]
│   │       ├── stitch-sidebar.tsx  [NEW] (Deep navy w-72 navigation sidebar)
│   │       ├── stitch-header.tsx   [NEW] (Top command bar: facility selector, search, + Ingest)
│   │       ├── stitch-ingestion-modal.tsx [NEW] (CSV dropzone + 1-click dataset buttons)
│   │       └── views/              [NEW DIRECTORY]
│   │           ├── executive-overview-view.tsx [NEW] (Screen 1: KPIs, Donut, Decoupling, Levers)
│   │           ├── carbon-balance-view.tsx     [NEW] (Screen 4: Sankey, Mass Allocation, Ledger)
│   │           ├── scenario-simulator-view.tsx [NEW] (Screen 3: Sandbox sliders & live simulation)
│   │           ├── cbam-products-view.tsx      [NEW] (Screen 2: Product footprints & CBAM declaration)
│   │           ├── scope3-suppliers-view.tsx   [NEW] (Screen 6: Tier-1 suppliers & spend breakdown)
│   │           └── esg-targets-view.tsx        [NEW] (Screen 5: Multi-year SBTi trajectory)
│   └── lib/
│       └── stitch-mock-data.ts     [NEW] (Authoritative baseline fallback data matching Stitch)
└── __tests__/
    └── components/
        └── stitch-views.test.tsx   [NEW] (Vitest unit tests for Stitch views and CSV uploader)
```

---

## Step-by-Step Implementation Tasks

### Task 1: Stitch Typography, Google Fonts & Theme Design Tokens
- **Files**:
  - `frontend/src/app/layout.tsx`
  - `frontend/src/app/globals.css`
- **Actions**:
  - Add Google Fonts preconnect and stylesheets (`Inter:wght@400;500;600;700`, `Plus+Jakarta+Sans:wght@600;700;800`, `Material+Symbols+Outlined`).
  - Configure Tailwind / CSS variables for Stitch colors (`bg-surface`, `surface-container-lowest`, `primary-container`, `secondary`, etc.).
  - Add utility typography classes (`font-display-lg`, `font-headline-xl`, `font-metric-xl`, `font-mono-data`, etc.).

### Task 2: Master Stitch Sidebar and Header Navigation Shell
- **Files**:
  - [NEW] `frontend/src/components/stitch/stitch-sidebar.tsx`
  - [NEW] `frontend/src/components/stitch/stitch-header.tsx`
- **Actions**:
  - Implement fixed 72-unit (`w-72`) deep navy sidebar with EcoAudit AI logo, "v3.4 Audited" badge, and 6 active view buttons with Material Symbols icons.
  - Implement fixed top header with facility selector, "CBAM Readiness: 94.2% Audit Ready", Quick Search, `+ New Ingestion / Audit Run` button, notifications, and user avatar.

### Task 3: Stitch-Native CSV Ingestion & Quick-Load Modal
- **Files**:
  - [NEW] `frontend/src/components/stitch/stitch-ingestion-modal.tsx`
- **Actions**:
  - Drag-and-drop CSV upload dropzone accepting `.csv` files.
  - 1-click Quick-Load buttons for existing datasets:
    - `Chicago Energy Benchmarking 2026`
    - `Competition Demo`
    - `Synthetic Company Data`
  - Provider toggle (Gemini Vision AI vs Deterministic Mock AI).
  - Country / emission factor grid selector (Egypt EEAA, UK DEFRA 2024, EU Average).
  - Connect to `POST /api/runs` and `POST /api/demo` with live progress indicator.

### Task 4: Stitch Core Views (Executive Overview & Carbon Balance Ledger)
- **Files**:
  - [NEW] `frontend/src/lib/stitch-mock-data.ts`
  - [NEW] `frontend/src/components/stitch/views/executive-overview-view.tsx`
  - [NEW] `frontend/src/components/stitch/views/carbon-balance-view.tsx`
- **Actions**:
  - **Executive Overview**: 4 high-density KPI cards, Scope 1/2/3 breakdown donut chart, hierarchical collapsible drilldown table, financial-carbon decoupling SVG chart, facility energy mix, and activity table. Bind live run values (`total_emissions`, `scope_totals`, `statistics`, `activities`).
  - **Carbon Balance**: Mass balance cards, Sankey flow topology, double-entry ledger transactions, and zero-delta verification badge.

### Task 5: Stitch Scenario Simulator, CBAM Products, Scope 3 & ESG Targets
- **Files**:
  - [NEW] `frontend/src/components/stitch/views/scenario-simulator-view.tsx`
  - [NEW] `frontend/src/components/stitch/views/cbam-products-view.tsx`
  - [NEW] `frontend/src/components/stitch/views/scope3-suppliers-view.tsx`
  - [NEW] `frontend/src/components/stitch/views/esg-targets-view.tsx`
- **Actions**:
  - **Scenario Simulator**: Strategic Sandbox sliders for fuel switching (H₂ co-fire), PPA clean energy, circular scrap feed, supplier mandates, and dynamic ETS shadow carbon price. Connect to backend `POST /api/runs/{run_id}/scenarios` for live calculation of abated kgCO2e and financial savings!
  - **CBAM Products**: Product carbon intensity table with embedded emissions per tonne, EU CBAM quarter declaration summary.
  - **Scope 3 & Suppliers**: Value chain upstream categories and supplier decarbonization readiness.
  - **ESG Targets**: Multi-year SBTi net-zero target tracking.

### Task 6: Assemble Master Page & Dynamic State Orchestration
- **Files**:
  - `frontend/src/app/page.tsx`
- **Actions**:
  - Integrate `StitchSidebar`, `StitchHeader`, dynamic view switching, `StitchIngestionModal`, and pipeline progress banner.
  - Wire run status polling with `useRunStatus(activeRunId)` and load fresh summary & activities upon completion.

### Task 7: Unit Testing & Build Verification
- **Files**:
  - [NEW] `frontend/__tests__/components/stitch-views.test.tsx`
- **Actions**:
  - Write Vitest tests verifying view switching, CSV uploader modal opening/closing, and live data rendering.
  - Run `npm test -- --run` to ensure 100% test pass rate.
  - Run `npm run build` with Turbopack to verify zero TypeScript/compilation errors.

---

## Verification Plan

### Automated Tests
1. **Frontend Vitest Suite**:
   ```bash
   cd frontend && npm test -- --run
   ```
2. **Next.js Production Build**:
   ```bash
   cd frontend && npm run build
   ```
3. **Backend Pytest Suite**:
   ```bash
   python3 -m pytest tests/
   ```

### Manual & Interactive Verification
1. Launch the FastAPI backend on port 8000 and Next.js frontend on port 3000.
2. Verify initial load renders the crisp Stitch light theme with deep navy sidebar and Executive Overview.
3. Click `+ New Ingestion / Audit Run` -> Click "Quick Load: Chicago Energy Benchmarking" -> Verify pipeline progress bar advances through stages and updates the dashboard with live emissions.
4. Click `+ New Ingestion / Audit Run` -> Drag and drop a custom CSV -> Verify upload succeeds, parses rows, and updates the activities table and Scope 1/2/3 breakdown.
5. Switch to **Decarbonization Simulator** -> Adjust H₂ co-firing and PPA sliders -> Verify simulation updates emissions abated and financial exposure.
6. Switch through all 6 Stitch navigation views to ensure seamless fidelity and responsiveness.
