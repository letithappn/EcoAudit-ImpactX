# Module 1: Reverse Engineering Global Enterprise Carbon Engines
**Architectural Blueprint: Persefoni, Watershed & SAP Sustainability Footprint Management**

---

## 1. Computational Graph & Calculation Architecture

Enterprise climate-tech platforms (Watershed, Persefoni, SAP SFM) decouple data ingestion and storage from computation using **Directed Acyclic Graphs (DAG)**. In this model, calculations are not flat database stored-procedure queries; they are vectorized graph traversals.

```
       [Raw Operational Data / ERP Vouchers]
                          │
                          ▼
            [Unit Normalization Node]
       (e.g., US Gallons -> Litres -> m3)
                          │
                          ▼
         [Temporal & Spatial Alignment Node]
     (Matching Invoice Date -> Valid EF Vintage & Region)
                          │
                          ▼
             [GWP Formulation Engine]
         (IPCC AR5 / AR6 Metric Weighting)
                          │
                          ▼
             [Double-Entry Ledger Post]
    (Debit: Facility Liability | Credit: Clearing)
```

### 1.1 The Generalized Formulation Engine
At each computational graph node, the engine evaluates:
$$E = Q_{\text{norm}} \times EF_{i,j,t} \times (1 - CF) \times GWP_{g,k}$$

Where:
- $E$: Total greenhouse gas emissions in metric tonnes ($\text{tCO}_2\text{e}$).
- $Q_{\text{norm}}$: Operational activity metric converted deterministically into standard base units (e.g., $\text{kWh}$, $\text{L}$, $\text{m}^3$, $\text{Tonne}$).
- $EF_{i,j,t}$: Emission factor specific to activity type $i$, geographic boundary $j$, and temporal vintage period $t$.
- $CF$: Contractual curtailment or instrument factor (e.g., zero-emission PPA or retired EAC/I-REC).
- $GWP_{g,k}$: Global Warming Potential of constituent greenhouse gases ($\text{CO}_2, \text{CH}_4, \text{N}_2\text{O}, \text{HFCs}, \text{PFCs}, \text{SF}_6, \text{NF}_3$) under IPCC assessment report $k$ (AR5 vs. AR6).

---

## 2. Double-Entry Carbon General Ledger & Immutability

Traditional software records emissions as a single scalar column in an activity table. This approach collapses during third-party financial assurance audits because it lacks balanced accounting controls and cannot trace retroactive adjustments.

Watershed and Persefoni solve this by mirroring **Financial General Ledgers (GAAP / IFRS)**:

### 2.1 The Debit / Credit Mechanics of Carbon
In financial accounting:
$$\text{Assets} = \text{Liabilities} + \text{Equity}$$
In environmental ledger accounting:
$$\text{Carbon Footprint (Liability)} + \text{Surrendered Offsets (Asset)} = \text{Total Absorbed Impact (Clearing)}$$

| Transaction Event | Debit Account | Credit Account | Operational Meaning |
|---|---|---|---|
| **Grid Electricity Invoiced** | `2300-Scope2-Electricity-Liability` | `1000-Clearing-Absorption` | Incurs legal Scope 2 carbon liability |
| **Diesel Burned in Generator**| `2120-Scope1-Stationary-Solar` | `1000-Clearing-Absorption` | Incurs legal Scope 1 direct liability |
| **EGX Carbon Credit Retired** | `1500-Offset-CERC-Reserve` | `2300-Scope2-Electricity-Liability`| Retires carbon asset to discharge liability |

### 2.2 Immutability & SHA-256 State Chaining
Data is strictly **append-only**. When a utility invoice is adjusted or an emission factor is corrected, the database executes a **compensating reversal entry** rather than an `UPDATE` statement.

Cryptographic lineage across all ledger transactions is enforced via sequential state chaining:
$$H_n = \text{SHA256}\left(H_{n-1} \parallel T_{\text{event}} \parallel Q_{\text{norm}} \parallel EF_{\text{id}} \parallel \text{Payload}\right)$$

If an attacker or rogue administrator modifies an invoice quantity in the past, all downstream state hashes break, immediately alerting external verifiers during an ISO 14064-3 assurance audit.

---

## 3. SAP SFM: Product Carbon Footprints (PCF) at the Bill of Materials Level

While Watershed focuses on corporate organizational footprints, **SAP Sustainability Footprint Management** solves industrial product-level footprinting for cross-border carbon border adjustments (such as EU CBAM).

Spend-based economic allocation is legally prohibited under definitive CBAM rules. SAP SFM calculates bottom-up footprints through recursive Bill of Materials traversal and machine-hour capacity routing:

### 3.1 Precursor Materials Footprint
$$PCF_{\text{materials}} = \sum_{i=1}^{m} \left( q_i \times PCF_{C_i} \right)$$
Where $q_i$ is the mass or volume of raw material or precursor $C_i$ required per unit of finished product.

### 3.2 Production Step Operational Allocation
Scope 1 thermal energy and Scope 2 electricity are allocated across production lines based on active run times and sub-metered equipment capacity:
$$PCF_{\text{step}, k} = \frac{E_{CC_k}}{\text{Total Capacity Hours}_k} \times \tau_{\text{order}, k}$$

### 3.3 Line Scrap and Yield Adjustment
Manufacturing scrap inflates the embedded carbon per unit of saleable finished product:
$$PCF_{\text{cumulative}} = \frac{PCF_{\text{materials}} + \sum_k PCF_{\text{step}, k}}{\eta_{\text{line}}}$$
Where $\eta_{\text{line}} \in (0, 1]$ represents the line-level yield factor.

---

## 4. Enterprise Data Ingestion Pipelines

Enterprise carbon accounting platforms integrate with existing business backbones across two distinct channels:

### 4.1 Structured ERP Connectors
- **SAP S/4HANA**: Leverages SAP Core Data Services (CDS) views exposed over OData v4. Queries material documents (`MATDOC`) for fuel and feedstock receipts, and general ledger vouchers (`ACDOCA`) for freight expenditures.
- **Odoo (v14–v18)**: Interfaces via JSON-RPC / XML-RPC endpoints to poll manufacturing orders (`mrp.production`), bills of materials (`mrp.bom`), and vendor bills (`account.move`).
- **Oracle Cloud & NetSuite**: Utilizes SuiteTalk REST Web Services with token-based authentication (TBA) to extract purchase order lines and utility payments.

### 4.2 Unstructured Data Ingestion (Utility Invoices & Receipts)
Documents pass through a vision-language extraction pipeline:
1. **Preprocessing**: OpenCV adaptive thresholding, Radon deskewing, and noise binarization.
2. **Layout Segmentation**: YOLO-based object detection isolating meter serials, consumption numbers, and billing periods.
3. **Bilingual OCR**: Transformer-based optical character recognition (TrOCR) resolving mixed Arabic/English corporate invoices and converting Eastern Arabic numerals ($\text{٠-٩}$) to standard digits.
4. **Automated Cross-Validation**: Checking meter delta against active billed energy, and cross-referencing billed totals against official regulated tariff schedules.
5. **Human-in-the-Loop (HITL)**: Extractions with confidence scores below $92\%$ route to an exception dashboard.

---

## 5. Enterprise Commercial Models & GTM Comparison

Global enterprise platforms charge premium subscription tiers based on compliance urgency and enterprise scale:

| Platform | Core Value Proposition | Commercial Pricing Structure | Target Customer Profile |
|---|---|---|---|
| **Persefoni** | Financial-grade footprinting & PCAF financed emissions | $50,000 to $250,000+ USD/year | Tier 1 Banks, Private Equity, Fortune 500 |
| **Watershed** | Corporate Scope 1-3 footprinting & climate action plans | $35,000 to $150,000+ USD/year | Tech enterprises, multinational consumer brands |
| **SAP SFM** | Bottom-up ERP BOM product carbon footprinting | Add-on to SAP S/4HANA licenses | Heavy manufacturing, automotive, global supply chains |
| **EcoAudit AI** | Sovereign Egyptian & MENA compliance, CBAM & FRA | **$24,000 to $50,000 USD / year** (denominated in EGP) | Egyptian heavy exporters, EGX-listed, NBFIs |
