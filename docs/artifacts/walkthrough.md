# EcoAudit AI — SAP Sustainability Footprint Management & ESG Analytics

## Complete UI/UX Overhaul: Enterprise SAP Fiori Horizon Standard

We have completely remade the UI/UX to match the enterprise standard shown in your reference images: **SAP Sustainability Footprint Management (SFM)** and **SAP Analytics Cloud (SAC)**.

---

### The 5 Faithfully Recreated Views (Matching Images 1–5)

#### 1. Corporate Balance & Interactive Sankey Flow (Image 1)
- **Top Sankey Ribbon Diagram**:
  - Direct visualization of emission flows: **Categories** (`Stationary Combustion`, `Purchased Electricity`, `Purchased Goods`, `Capital Goods`, `Travel`) $\rightarrow$ **Scopes** (`Scope 1`, `Scope 2`, `Scope 3`) $\rightarrow$ **Total Emissions Center Pillar** ($72.82\text{ Ton}$) $\rightarrow$ **Product Outflow Allocations** (`Sold Products` in Magenta flowing into `VeganBar` and `SunnyBar`, `Closing Inventory`, and `Non-Product Emissions`).
- **Corporate CO2e Balance (24) Data Table**:
  - Item, Item Subtype, Item Subcategory, Plant, Item Type, and Total CO2e with enterprise hover states and export controls.

#### 2. Process Inbounds & Side Inspector (Image 2)
- **Header Filter Bar**: Product ID with copy action, Supplier ID with copy action, Activity Status dropdown, Footprint Status dropdown.
- **Inbounds Table (122 Items)**: Multi-select checkbox column, Product ID, Supplier ID, colored Activity Status (`Requested` in blue, `Received` in green, `Not requested`), Footprint Status (`Valid` in green, `No Data` in gray).
- **Interactive Side Inspector Drawer (`BikeTech`)**:
  - Product Footprint card with active status link.
  - Inbound Process card with comment textarea and primary action button **"Request Footprint"**.
  - Activity history section.

#### 3. Analyze ESG Data — Target-Driven KPI Tiles (Image 3)
- **Filter Bar**: Search, active period chips (`2022 ✕`, `2023 ✕`, `2024 ✕`, `2025 ✕`), Reporting Structure (`=Business Location ✕`), Group Name, Metric Name, "Go", and "Clear".
- **Environmental Section with 10 KPI Tiles**:
  1. Gross GHG Emissions – Scope 1 ($330.02\text{K}\uparrow$ in red vs Target $294.42\text{K}$)
  2. Gross GHG Emissions – Scope 2, Location-Based ($87.34\text{K}\uparrow$ in red vs Target $66.18\text{K}$)
  3. Gross GHG Emissions – Scope 3 ($1.76\text{M}\uparrow$ in red vs Target $1.56\text{M}$)
  4. Total Gross GHG Emissions ($2.17\text{M}\uparrow$ in red vs Target $1.92\text{M}$)
  5. Carbon Credits ($30.00\downarrow$ in green vs Target $29.34$)
  6. Emissions to Air ($1.64\text{M}\uparrow$ in green vs Target $1.92\text{M}$)
  7. Emissions to Water ($444.97\text{K}\uparrow$ in red vs Target $431.42\text{K}$)
  8. Emissions to Soil ($85.55\text{K}\uparrow$ in red vs Target $72.89\text{K}$)
  9. Percentage of Scope 1 Emissions Under Mandate ($27.93\%$ in red vs Target $30.00\%$)
  10. GHG Emission Intensity ($4.78\text{K}/\text{tM USD}$ in red vs Target $447.79$)
  - Each tile features a mini column bar chart across years 2021–2025 with a black target threshold line and legend.

#### 4. Manage Product Emissions & Download CBAM Reports (Image 4)
- **Product Emissions Table**: ERP ID, Supplier ID, 8-digit CN Codes (`7301`, `7303 00`, `7606`, `7614`), Reporting Period (`Q1 2025`, `Q4 2024`), Data Status (`Actuals` in green, `Defaults` in blue), Total Emission per ton.
- **Interactive "Download CBAM Reports" Modal**:
  - Modal subtabs: *General Information*, *Reporting Period*, *Signature*.
  - Global data confirmation checkboxes.
  - Quarter selector (`Q1, 2025`).
  - Signatory inputs: Signature Place (`Madrid`), Signature (`Tania Solano`), Position of Person (`Sustainability Manager`).
  - Action button: Blue **"Download"** button exporting valid European Commission CBAM XML declarations.

#### 5. SAP Analytics Cloud (SAC) — GHG Emissions Overview Stories (Image 5)
- **Collapsible Left Filter Drawer**: Applied to All Pages (Currency USD, Unit Ton, Fiscal Year 2024, Period, Profit Center, Segment).
- **Combined GHG and Finance KPIs**: GHG Emissions ($159\text{ tCO2e}$), Operating Income, Gross Margin, Net Revenue.
- **All GHG Scopes Donut Charts**: Data Quality Characteristic (Primary Measured $3\%$, Secondary Industry Average $21\%$, Secondary Proxy $76\%$), Mode of Transport (Road $58\%$, Inland waterway $24\%$, Sea $14\%$, Pipeline $4\%$).
- **Scope 1/2/3 Pie Breakdown**: Stationary vs Mobile combustion, Scope 3 Franchise and Waste distributions.

---

### Gemini AI Integration
- The Gemini API key provided has been securely stored in `.env` and `frontend/.env.local` (both strictly gitignored and excluded from version control).
- The Python backend's `GeminiClassifier` has been verified to initialize successfully with live Gemini multimodal capabilities for parsing unstructured Arabic/English invoices and generating decarbonization recommendations.

---

### Fresh Verification Evidence
- **Vitest Unit Tests**: **20 tests passed (100% Green)** across 6 test suites (`sap-views`, `api-client`, `isa-ui`, `dashboard`, `scenarios-evidence`, `csv-uploader`).
- **Next.js Production Build**: `next build` compiled in **1.2s** with zero errors.
- **FastAPI Backend Pipeline**: Verified against the 33-row benchmark dataset producing exact deterministic results ($34,805.42\text{ kgCO2e}$).
