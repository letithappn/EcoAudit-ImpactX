# Module 2: Egyptian Regulatory Framework, Standards & Data Baselines
**Compliance Blueprint: FRA Mandates, EGX Carbon Market, EOS Standards & EU CBAM Alignment**

---

## 1. Financial Regulatory Authority (FRA) Mandates

The Egyptian Financial Regulatory Authority (الهيئة العامة للرقابة المالية - FRA) has legally transitioned corporate sustainability and greenhouse gas accounting from voluntary public relations exercises into mandatory regulatory filings backed by statutory penalties and licensing conditions.

### 1.1 Legislative Foundation: Decrees 107 & 108 of 2021
Issued in July 2021, these decrees established the initial disclosure requirements for capital market participants:

1. **FRA Decree No. 107 of 2021:**
   - **Target Group:** All companies listed on the Egyptian Exchange (EGX) and all Non-Bank Financial Institutions (NBFIs) — including leasing, factoring, microfinance, consumer finance, mortgage finance, and insurance firms — with an issued capital or net equity of at least **100 million EGP**.
   - **Requirement:** Mandatory annual submission of Environmental, Social, and Governance (ESG) performance filings concurrently with the annual Board of Directors report.

2. **FRA Decree No. 108 of 2021:**
   - **Target Group:** Large EGX-listed enterprises and NBFIs with issued capital or net equity of at least **500 million EGP**.
   - **Requirement:** Mandatory climate-related financial disclosures aligned directly with the recommendations of the **Task Force on Climate-related Financial Disclosures (TCFD)**, now superseded and codified under **IFRS S2 (Climate-related Disclosures)**. Disclosures must document board oversight, strategic transition risks, climate scenario analysis, and quantified Scope 1 and Scope 2 emissions.

```
       ┌─────────────────────────────────────────────────────────────┐
       │                 FRA Mandatory Scope Matrix                  │
       ├──────────────────────────────┬──────────────────────────────┤
       │ Capital / Equity ≥ 100M EGP  │ Capital / Equity ≥ 500M EGP  │
       ├──────────────────────────────┼──────────────────────────────┤
       │ • FRA Decree 107/2021        │ • FRA Decree 108/2021        │
       │ • Quantitative ESG KPIs      │ • TCFD / IFRS S2 Disclosures │
       │ • Energy & Carbon Footprint  │ • Transition Risk Scenarios  │
       │ • Board Governance Annex     │ • Scope 1 & 2 Audited Report │
       └──────────────────────────────┴──────────────────────────────┘
```

---

### 1.2 The 2026 Regulatory Catalyst: FRA Decision No. 36 of 2026
Enacted in February 2026, **FRA Decision No. 36 of 2026** fundamentally altered the carbon landscape in Egypt by establishing direct operational and financial liabilities:

- **Mandatory Annual Accounting:** All NBFIs with issued capital or net equity exceeding 100 million EGP must measure, calculate, and report their verified Scope 1 and Scope 2 operational carbon footprint annually by **June 30**.
- **Third-Party Verification Requirement:** Carbon footprint reports must be validated and certified by an independent **Validation and Verification Body (VVB)** registered on the official FRA register (e.g., EOS Verification Unit, Petrosafe, SGS Egypt, TÜV Nord).
- **The Mandatory 20% CERC Offset Obligation (Article 2):**
  Covered institutions must legally neutralize a minimum of **20% of their verified annual Scope 1 and Scope 2 emissions**:
  $$CERC_{\text{obligation}} = \left\lceil 0.20 \times \left( E_{\text{Scope 1}} + E_{\text{Scope 2}} \right) \right\rceil$$
- **Settlement & Retirement Window:** The offset must be fulfilled within **90 calendar days** following the June 30 filing deadline by purchasing and surrendering registered **Carbon Emission Reduction Certificates (CERCs)** through the regulated voluntary carbon market on the EGX.
- **Licensing Sanction:** Compliance is an explicit condition of maintaining the institution's NBFI operating license under Capital Market Law No. 95 of 1992 and Non-Bank Financial Market Regulation Law No. 10 of 2009. Failure to submit verified footprints or retire the required certificates triggers administrative fines, suspension of license renewal, or public market censure.

---

### 1.3 Official FRA ESG & Carbon Disclosure Schema
The platform's compliance export engine must generate structured disclosure packages conforming exactly to the FRA standard reporting template:

| Regulatory Code | Disclosure Parameter | Metric Unit | Accounting Methodology & Validation Mandate |
|---|---|---|---|
| **E1-GHG-S1** | Direct Scope 1 GHG Emissions | $\text{tCO}_2\text{e}$ | Stationary combustion (boilers, generators), mobile fleet combustion, and fugitive refrigerant leakage. |
| **E1-GHG-S2** | Indirect Scope 2 GHG Emissions | $\text{tCO}_2\text{e}$ | Metered national grid electricity consumption, chilled water, and purchased steam. |
| **E1-GHG-INT** | Operational Carbon Intensity | $\text{tCO}_2\text{e} / \text{M EGP}$ | Total $(\text{Scope 1} + \text{Scope 2})$ divided by annual gross operating turnover in Million EGP. |
| **E2-ENG-DIR** | Direct Energy Consumption | Gigajoules ($\text{GJ}$) | Disaggregated thermal consumption: Natural Gas, Solar/Diesel, Mazut, and Motor Gasoline. |
| **E2-ENG-IND** | Indirect Electrical Energy | $\text{MWh}$ | Total active electrical energy drawn from Egyptian Electricity Holding Company (EEHC) grids. |
| **E3-WAT-REC** | Water Influx & Recycling | Cubic Meters ($\text{m}^3$) | Municipal water utility intake, licensed groundwater extraction, and onsite wastewater recycling ratio. |
| **E4-WST-HAZ** | Hazardous & Industrial Waste | Metric Tonnes | Mass of hazardous chemical waste, electronic waste, and general manufacturing scrap. |
| **G1-BRD-DIV** | Board Gender Diversity | Percentage ($\%$) | Minimum 25% female board representation or at least two female directors (FRA Decree 109/2021). |

---

## 2. Regulated Voluntary Carbon Market on the Egyptian Exchange (EGX)

Egypt launched Africa’s first regulated voluntary carbon trading market, operationalized under Prime Ministerial Decree No. 4664 of 2022 and formalized through FRA regulations:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   EGX Regulated Carbon Market Flow                     │
└────────────────────────────────────────────────────────────────────────┘
    1. Project Registration   ──▶ FRA National Carbon Registry (Decree 30/2024)
    2. Verification           ──▶ FRA-Registered VVB (ISO 14064-2/3)
    3. Listing & Quotation    ──▶ EGX Environmental Trading Board (Decree 31/2024)
    4. Brokerage Execution    ──▶ Licensed Broker Interface (Decree 1732/2024)
    5. Registry Surrender     ──▶ Automated Retirement Serial Tracking -> FRA Filing
```

### 2.1 The Regulatory Triad (Decrees 30, 31, and 1732 of 2024)
1. **FRA Decree No. 30 of 2024:** Established the **National Database for Carbon Emission Reduction Projects**. Accredits voluntary registries (e.g., Gold Standard, Verra, or Egyptian National Carbon Registry) that meet stringent additionality, permanence, and traceability guidelines aligned with ICROA standards.
2. **FRA Decree No. 31 of 2024:** Codified rules for listing, delisting, and continuous trading of CERCs on the EGX, officially defining carbon certificates as tradeable non-equity financial instruments.
3. **FRA Decree No. 1732 of 2024:** Defined licensing criteria, capital adequacy rules, and electronic order-routing requirements for environmental securities brokerage firms authorized to broker CERCs.

### 2.2 Direct Software Integration with CERC Procurement & Retirement
EcoAudit AI bridges carbon calculation with statutory offset settlement:
1. **Obligation Calculation:** Upon closing the fiscal year ledger, the engine determines $CERC_{\text{obligation}} = \lceil 0.20 \times (\text{Scope 1} + \text{Scope 2}) \rceil$.
2. **Order Placement via Broker API:** Through a secure FIX / REST protocol integration with an FRA-licensed environmental broker, the system constructs a buy order for qualifying Egyptian CERCs (e.g., local afforestation, solar irrigation, or biogas projects).
3. **Execution & Custody Tracking:** Upon trade settlement on the EGX clearinghouse, the platform records:
   - Certificate Serial Numbers (UUID format conforming to the National Registry schema).
   - Vintage Year and Issuing Project ID.
   - Settlement price per certificate in EGP.
4. **Automated Retirement Posting:** The engine executes a double-entry retirement posting in the carbon ledger:
   $$\text{Debit: 1500-Offset-CERC-Reserve} \quad \Big\vert \quad \text{Credit: 2300-Scope2-Electricity-Liability}$$
   The certificate status is marked as `RETIRED_FOR_FRA_DECISION_36` and appended with a SHA-256 certificate proof hash, satisfying FRA annual compliance checks.

---

## 3. Egyptian Organization for Standardization and Quality (EOS)

The Egyptian Organization for Standardization and Quality (الهيئة المصرية العامة للمواصفات والجودة - EOS) administers national standards aligned with international standards:

- **ES ISO 14064-1:** Quantification and reporting of greenhouse gas emissions and removals at the organization level.
- **ES ISO 14064-2:** Quantification, monitoring, and reporting of GHG emission reductions at the project level.
- **ES ISO 14064-3:** Specification with guidance for the verification and validation of greenhouse gas statements.
- **ES ISO 14067:** Carbon footprint of products (requirements and guidelines for quantification).

### 3.1 Conformity Criteria for Independent Third-Party Assurance
To pass an audit by Egyptian Accreditation Council (EGAC) accredited VVBs (SGS Egypt, TÜV Nord, Petrosafe, EOS Verification Unit), software outputs must fulfill five core criteria:

1. **Organizational Boundary Justification:** Clear mathematical segregation under either **Operational Control** (100% of emissions from facilities where the entity dictates operating policies) or **Equity Share** (economic interest percentage).
2. **Factor Lineage & Vintage Mapping:** Every calculation must cite the specific publishing authority, release year, calorific basis (NCV vs. GCV), and IPCC assessment report (AR5 vs. AR6).
3. **Root-Sum-of-Squares Uncertainty Propagation:**
   ISO 14064-1 mandates uncertainty disclosure. The calculation engine implements standard error propagation across all activity records $i$:
   $$U_{\text{inventory}} = \frac{\sqrt{\sum_{i=1}^{n} \left( U_{\text{data}, i} \times E_i \right)^2 + \left( U_{\text{factor}, i} \times E_i \right)^2}}{\sum_{i=1}^{n} E_i}$$
   Where $U_{\text{data}, i}$ is the measurement instrument error (e.g., Class 0.5 utility meter = $\pm 0.5\%$) and $U_{\text{factor}, i}$ is the published statistical variance of the emission factor.
4. **Biogenic Carbon Segregation:**
   Biogenic emissions (e.g., bagasse combustion in sugar mills, rice straw burning, biofuel blends) must be quantified and reported outside the gross Scope 1 total as a memo item.
5. **Base Year Recalculation Threshold:**
   A structural change (acquisition, divestiture, or recalculation of emission factors) altering the base year emissions by $\ge 5\%$ triggers an automated recalculation flag in the system.

---

## 4. National Emission Factor Database & Baselines

A fatal flaw of foreign carbon SaaS platforms in Egypt is their reliance on generic European or global proxies. EcoAudit AI embeds the official national baseline factors established by the **Egyptian Environmental Affairs Agency (EEAA)**, the **New and Renewable Energy Authority (NREA)**, and the **Egyptian Electricity Holding Company (EEHC)**.

### 4.1 Egyptian National Electricity Grid Emission Factor
The Egyptian national transmission grid is a unified, synchronized synchronous network. Base-load generation is anchored by high-efficiency Siemens combined-cycle natural gas mega-plants (Beni Suef, Burullus, New Capital; 14.4 GW total capacity), supported by hydro (Aswan High Dam), wind (Zafarana, Gulf of El-Zayt, Ras Ghareb), and utility-scale solar (Benban Solar Park, 1.8 GW).

The location-based grid emission factor is derived via:
$$EF_{\text{grid, loc}} = \frac{\sum_{m} \left( \text{Fuel Consumed}_m \times NCV_m \times EF_{\text{fuel}, m} \right)}{\text{Total Net Generation Generated (MWh)} \times \left(1 - \text{Transmission Loss Rate}\right)}$$

Based on official EEHC operational data and high-voltage transmission losses ($\sim 7.2\%$):
$$\mathbf{EF_{\text{grid, loc}} = 0.4580 \, \text{tCO}_2\text{e / MWh}} \quad \left(0.4580 \, \text{kgCO}_2\text{e / kWh}\right)$$

```
┌────────────────────────────────────────────────────────────────────────┐
│             Egyptian National Grid Factor Breakdown (2025–2026)         │
├──────────────────────────────┬──────────────┬──────────────────────────┤
│ Component                    │ Value        │ Source Authority         │
├──────────────────────────────┼──────────────┼──────────────────────────┤
│ Gross Generation Baseline    │ 0.4250 t/MWh │ EEAA Inventory Report    │
│ High-Voltage Transmission Loss│ 7.2%         │ EEHC Annual Bulletin     │
│ Net Location-Based Factor    │ 0.4580 t/MWh │ EEAA / NREA Unified Stat │
│ Market-Based Certified PPA   │ 0.0000 t/MWh │ NREA Green Certificate  │
│ Residual Grid Mix Factor     │ 0.4580 t/MWh │ National Baseline        │
└──────────────────────────────┴──────────────┴──────────────────────────┘
```

---

### 4.2 Egyptian Industrial Fuel Emission Factors & Calorific Values
Egyptian industrial fuels deviate from international generic defaults due to domestic refinery blending specs set by the Egyptian General Petroleum Corporation (EGPC) and Egyptian Natural Gas Holding Company (EGAS):

| Egyptian Fuel Identifier | Arabic Identifier | Net Calorific Value (NCV) | Density | Carbon Content Factor | Final Emission Factor | Primary Regulatory Authority |
|---|---|---|---|---|---|---|
| **Natural Gas** | الغاز الطبيعي | $38.20 \, \text{MJ/m}^3$ | $0.730 \, \text{kg/m}^3$ | $56,100 \, \text{kg CO}_2/\text{TJ}$ | **$2.1430 \, \text{kg CO}_2\text{e / m}^3$** | EEAA / EGAS Pipeline Specs |
| **Solar / Gasoil** | سولار | $43.00 \, \text{MJ/kg}$ | $0.845 \, \text{kg/L}$ | $74,100 \, \text{kg CO}_2/\text{TJ}$ | **$2.6925 \, \text{kg CO}_2\text{e / L}$** | EGPC Industrial Diesel Standard |
| **Mazut (HFO)** | مازوت | $40.40 \, \text{MJ/kg}$ | $0.965 \, \text{kg/L}$ | $77,400 \, \text{kg CO}_2/\text{TJ}$ | **$3.1270 \, \text{tCO}_2\text{e / Ton}$** | EEAA Industrial Emissions Code |
| **Octane 92** | بنزين ٩٢ | $44.30 \, \text{MJ/kg}$ | $0.742 \, \text{kg/L}$ | $69,300 \, \text{kg CO}_2/\text{TJ}$ | **$2.2780 \, \text{kg CO}_2\text{e / L}$** | EGPC Fuel Distribution Standard |
| **Octane 95** | بنزين ٩٥ | $44.50 \, \text{MJ/kg}$ | $0.750 \, \text{kg/L}$ | $69,300 \, \text{kg CO}_2/\text{TJ}$ | **$2.3105 \, \text{kg CO}_2\text{e / L}$** | EGPC Premium Standard |

---

### 4.3 Domestic Transport & Logistics Fleet Factors
Calibrated to the age, maintenance standards, and operating profiles of Egypt's commercial transport fleet:

- **Heavy-Duty Articulated Diesel Truck ($> 32\text{ metric tonnes}$):** $\mathbf{0.0885 \, \text{kg CO}_2\text{e / tonne-km}}$
- **Rigid Commercial Truck ($7.5 - 16\text{ metric tonnes}$):** $\mathbf{0.1942 \, \text{kg CO}_2\text{e / tonne-km}}$
- **Light Commercial Van ($< 3.5\text{ metric tonnes}$):** $\mathbf{0.3120 \, \text{kg CO}_2\text{e / km}}$

---

## 5. EU CBAM Readiness for Egyptian Industrial Exporters

Under **European Union Regulation (EU) 2023/956** and **Implementing Regulation (EU) 2025/2547**, the Carbon Border Adjustment Mechanism entered its **definitive compliance phase on January 1, 2026**.

Egyptian industrial exporters in four primary sectors—**Iron & Steel, Aluminum, Cement, and Fertilizers**—can no longer access the European common market without submitting accredited Specific Embedded Emissions ($SEE_g$) data, or face penal border carbon certificate tariffs matching the weekly EU Emissions Trading System (EU ETS) allowance prices (~€65–€95 / $\text{tCO}_2\text{e}$).

### 5.1 The Specific Embedded Emissions Formulation
For any covered good $g$ manufactured within an Egyptian production installation:
$$SEE_g = \frac{\text{Direct Embedded Emissions} + \text{Indirect Embedded Emissions}}{\text{Net Output Production Quantity (metric tonnes)}}$$

```
                ┌────────────────────────────────────────────────┐
                │          Sectoral CBAM Rules for Egypt         │
                ├───────────────────────┬────────────────────────┤
                │ Annex II Goods        │ Annex IV Goods         │
                │ (Iron/Steel, Aluminum)│ (Cement, Fertilizers)  │
                ├───────────────────────┼────────────────────────┤
                │ • Direct emissions    │ • Direct emissions     │
                │   obligatory.         │   obligatory.          │
                │ • Indirect emissions  │ • Indirect electricity │
                │   excluded from       │   included in          │
                │   certificate         │   certificate          │
                │   surrender.          │   surrender.           │
                └───────────────────────┴────────────────────────┘
```

### 5.2 Sector-Specific Compliance Architectures
1. **Iron & Steel (Annex II):**
   - Covers Direct Reduced Iron (DRI), Electric Arc Furnace (EAF) billets, rebar, hot-rolled coils, and wire rod (CN codes `7206` through `7229`).
   - Indirect emissions from electricity are excluded from certificate surrender; calculations focus on natural gas consumption in DRI reformers, graphite electrodes, and process recarburizers.
2. **Aluminum (Annex II):**
   - Covers unwrought aluminum, wire, bars, and extrusions (CN codes `7601` through `7608`).
   - Excludes indirect emissions from certificate surrender under Annex II. Directly calculates perfluorocarbon ($CF_4$ and $C_2F_6$) anode effect emissions alongside thermal holding furnace combustion.
3. **Cement (Annex IV):**
   - Covers grey clinker and Portland cements (CN codes `2523 10 00`, `2523 29 00`).
   - Surrender covers both direct process calcination ($\text{CaCO}_3 \to \text{CaO} + \text{CO}_2$) and heavy indirect electricity consumption from raw meal grinding and ball mills.
4. **Fertilizers (Annex IV):**
   - Covers anhydrous ammonia, urea, and ammonium nitrate (CN codes `2814`, `3102`).
   - Includes direct Scope 1 natural gas feedstock reforming and nitrous oxide ($\text{N}_2\text{O}$) process emissions, plus indirect finishing electricity.

### 5.3 The 20% Default Value Ceiling
Under European Commission rules taking full effect in 2026, **default values are capped at a maximum of 20% of total embedded emissions for complex industrial goods**. 

At least **80% of reported embedded footprints must derive from primary, installation-specific verified data**. If an Egyptian exporter fails to monitor primary production lines via an auditable system, EU customs authorities will penalize the shipment with the highest default emissions of the worst-performing 10% of EU installations, resulting in millions of euros in unnecessary carbon border levies.
