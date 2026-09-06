# Carbon Intelligence Methodology

## 1. Overview

EcoAudit's Carbon Intelligence layer transforms raw emission calculation results into structured analytical outputs. All calculations are deterministic — no LLM or probabilistic model is involved in any numerical analysis.

### Architecture Position

```
Validated ActivityData
    |
    v
Deterministic Carbon Engine (Phases 1-2)
    |
    v
BatchResult (scope/category totals, individual results)
    |
    v
Carbon Intelligence Layer (this module)
    |
    v
CarbonIntelligenceReport
  - Scope breakdown with percentages
  - Category breakdown per scope
  - Activity-level contributions
  - Ranked hotspots
  - Pareto concentration analysis
  - Time trends
  - Data quality summary
  - Structured insights
```

## 2. Definitions

| Term | Definition |
|------|-----------|
| **Emission** | Quantity of greenhouse gases (GHG) expressed in kgCO2e (kilograms of CO2 equivalent). |
| **Scope** | GHG Protocol classification: Scope 1 (direct), Scope 2 (purchased energy), Scope 3 (value chain). |
| **Category** | Sub-classification within a scope (e.g., Stationary Combustion, Mobile Combustion, Purchased Electricity). |
| **Contribution** | A source's absolute emissions and percentage of a reference total. |
| **Hotspot** | An emission source exceeding a configurable contribution threshold. |
| **Pareto analysis** | Cumulative contribution of sources ranked by emissions (concentration analysis). |
| **Trend** | Period-over-period comparison of emissions. |
| **Insight** | A structured, evidence-based analytical finding with severity classification. |

## 3. Aggregation Logic

### 3.1 General Formula

```
contribution_percentage = (source_emissions / total_emissions) * 100
```

Where:
- `source_emissions` = sum of `emissions_value` for all `CalculationResult` objects in the group
- `total_emissions` = the reference total (company-wide, scope-level, or category-level)
- All arithmetic uses Python `Decimal` for exact reproducibility

### 3.2 Edge Cases

| Condition | Behavior |
|-----------|----------|
| `total_emissions = 0` | All percentages = 0%. No hotspots identified. |
| Single activity | 100% contribution. Still produces a valid report. |
| Equal contributions | All sources get the same percentage. Ranking is alphabetical for stability. |

### 3.3 Supported Dimensions

| Dimension | Grouping Key | Source |
|-----------|-------------|--------|
| `scope` | `activity.scope` (Scope enum) | ActivityData |
| `category` | `activity.category` (Category enum) | ActivityData |
| `activity_type` | `activity.metadata["activity_type"]` | ActivityData.metadata |
| `facility` | Description prefix before " - " | ActivityData.description |

## 4. Hotspot Methodology

### 4.1 Threshold-Based Identification

A **hotspot** is any emission source contributing >= `threshold`% of total emissions.

- **Default threshold:** 5%
- **Configurable:** `CarbonAnalyzer(hotspot_threshold=Decimal("10"))` raises the bar to 10%.

**Justification for 5% default:** Based on GHG Protocol guidance that Scope 3 categories contributing >= 5% of total footprint should be reported and managed. We apply the same materiality principle across all dimensions.

### 4.2 Severity Classification

| Severity | Threshold | Meaning |
|----------|-----------|---------|
| **CRITICAL** | >= 25% of total | Dominant emission source — must be addressed first |
| **HIGH** | >= 10% of total | Major contributor — high-priority target |
| **MEDIUM** | >= 5% of total | Significant contributor — should be monitored |
| **LOW** | < 5% of total | Minor contributor — not flagged as hotspot by default |

### 4.3 Actionability Classification

| Scope | Actionability | Rationale |
|-------|-------------|-----------|
| Scope 1 | ACTIONABLE | Company directly controls the emission source |
| Scope 2 | ACTIONABLE | Company can switch suppliers, improve efficiency, or self-generate |
| Scope 3 | PARTIALLY_ACTIONABLE | Company can influence but does not directly control |

## 5. Pareto / Concentration Analysis

### 5.1 Methodology

Sources are ranked by emissions (descending). Cumulative contribution is calculated:

```
Point 1: top 1 source  → X₁% of total
Point 2: top 2 sources → X₂% of total
...
Point N: all N sources → 100% of total
```

### 5.2 Interpretation

If the top 3 out of 10 sources account for 80% of emissions, the footprint is "highly concentrated" — a small number of interventions could address most of the problem.

## 6. Time-Based Analysis

### 6.1 Period Detection

The system extracts time periods from (in priority order):
1. `metadata["period"]` — explicit period label
2. `metadata["year"]` — explicit year
3. `metadata["date"]` — parseable date string
4. Activity description — year pattern (e.g., "Q1 2024")
5. `factor.year` — emission factor year (last resort)

### 6.2 Trend Calculation

```
total_change = last_period_emissions - first_period_emissions
percentage_change = (total_change / first_period_emissions) * 100
```

### 6.3 Insufficient Data

The system explicitly identifies when data is insufficient:
- Minimum 2 distinct periods required for trend analysis
- If only 1 period exists: `is_sufficient_data = False` with explanation
- No trends are inferred from insufficient data

## 7. Data Quality Awareness

The intelligence layer does **not** invent quality scores. It uses only metadata that actually exists on the results:

| Metric | Source | Meaning |
|--------|--------|---------|
| `results_with_ai_classification` | `metadata["ai_confidence"]` | How many results were AI-classified |
| `results_needing_review` | `metadata["ai_needs_review"]` | How many are flagged for human review |
| `average_ai_confidence` | Mean of `ai_confidence` values | Overall AI reliability |
| `min_ai_confidence` | Min of `ai_confidence` values | Worst-case AI reliability |
| `results_with_test_factors` | `factor.is_test_data` | How many use non-production factors |
| `factor_sources` | `factor.source` | Which factor databases are being used |

## 8. Insight Generation

Insights are structured, deterministic findings — not LLM-generated text:

| Insight Type | Trigger Condition | Severity |
|-------------|-------------------|----------|
| Scope dominance | One scope >= 60% of total | HIGH |
| Single source dominance | One scope >= 80% of total | CRITICAL |
| Category concentration | One category >= 60% of its scope | MEDIUM |
| Hotspot identified | Source >= threshold of total | Based on hotspot severity |
| Pareto concentration | Top N sources >= 80% and N <= 30% of sources | HIGH |
| Trend change | Emissions increased >= 10% | HIGH |
| Data quality | Results needing review or using test factors | MEDIUM |

## 9. Limitations

1. **No financial analysis** — emissions are in kgCO2e only, no carbon pricing or cost.
2. **No recommendations** — the layer identifies hotspots but does not suggest interventions.
3. **Facility extraction is heuristic** — based on description prefix convention, not structured facility IDs.
4. **Time granularity limited by data** — if all activities have the same year, no trend is possible.
5. **Scope 3 categories not yet populated** — the system supports Scope 3 analysis but no Scope 3 data exists in current datasets.
6. **Equal-weight aggregation** — all activities are weighted equally (no uncertainty weighting yet).

## 10. Assumptions

1. All emissions values are in kgCO2e (guaranteed by the deterministic engine).
2. Percentages are calculated relative to the total within the relevant context (company-wide, scope, or category).
3. Rankings are deterministic: ties broken alphabetically by label.
4. The 5% hotspot threshold is based on GHG Protocol materiality guidance but is configurable.
5. Actionability is based on GHG Protocol scope definitions, not company-specific assessments.
