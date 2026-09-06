# Phase 6: Optimization & Scenario Engine Methodology

## 1. Overview

The Optimization & Scenario Engine transforms EcoAudit from a passive calculation tool into a deterministic decision-support platform. It answers the question: *"Given the company's measured emissions and identified hotspots, what happens if the company changes a relevant operational variable?"*

The engine calculates the carbon and financial impact of deterministic interventions, using the existing carbon calculator for all evaluations to ensure absolute methodological consistency between baseline and scenario results.

### Architectural Flow

```
Carbon Intelligence (Hotspot Identified)
        |
        v
Scenario Definition (Target Activities + Intervention)
        |
        v
Scenario Engine (Modifies Target ActivityData)
        |
        v
Carbon Calculator (Reruns modified ActivityData)
        |
        v
Scenario Result
  - Baseline Emissions & Cost
  - Scenario Emissions & Cost
  - Carbon Impact (Absolute & Percentage Reduction)
  - Financial Impact (Absolute & Percentage Savings)
  - Full Audit Trace
```

## 2. Core Concepts

*   **Baseline:** The original, un-modified `ActivityData` and its resulting `CalculationResult` (which includes cost data if available).
*   **Intervention:** A deterministic modification to an `ActivityData` record (e.g., reducing the quantity, changing the fuel type).
*   **Scenario Definition:** A named wrapper around an Intervention and the specific activity IDs it targets, including explicit human-readable assumptions.
*   **Scenario Result:** The combined output containing the baseline calculation, the new scenario calculation, and the computed impacts.
*   **Scenario Comparison:** A collection of `ScenarioResult` objects that can be ranked by metrics such as highest carbon reduction or greatest financial savings.

## 3. Intervention Types

The system supports the following deterministic interventions:

### 3.1 Percentage Reduction (`PercentageReduction`)
Reduces the volume of an activity by a specified percentage (0-100%).
*   **Assumptions:** Costs scale linearly with volume reduction.

### 3.2 Absolute Reduction (`AbsoluteReduction`)
Reduces the volume of an activity by a fixed absolute amount.
*   **Assumptions:** Activity cannot drop below zero. Costs scale linearly with volume reduction.

### 3.3 Fuel Substitution (`FuelSubstitution`)
Replaces one activity type with another (e.g., switching from diesel to grid electricity). This requires:
1.  The new activity type, scope, and category.
2.  The new unit of measurement.
3.  A conversion multiplier (e.g., 1 Litre Diesel = 10 kWh Electricity).
4.  (Optional) A new unit price.
*   **Assumptions:** Energy/volume equivalence is explicitly defined by the conversion multiplier.

## 4. Carbon Impact Calculation

All carbon impacts are calculated using `Decimal` arithmetic based on the difference between the baseline and scenario `CalculationResult` outputs.

```
Absolute Reduction = Baseline Emissions - Scenario Emissions
Percentage Reduction = (Absolute Reduction / Baseline Emissions) * 100
```
*(Positive values indicate a reduction/improvement)*

## 5. Financial Impact Calculation

Financial impact relies exclusively on explicit data found in the `ActivityData.metadata` field, specifically `total_cost`. The system **will never invent financial savings**.

*   If all targeted activities in both the baseline and scenario have valid cost data, the engine calculates:
    ```
    Absolute Savings = Baseline Cost - Scenario Cost
    Percentage Savings = (Absolute Savings / Baseline Cost) * 100
    ```
*   If *any* target activity lacks cost data (or if a fuel substitution does not provide a new unit price), the financial impact is explicitly marked as `is_available = False` and the fields are set to `None`.

## 6. Constraints and Limitations

1.  **No AI in Numerical Core:** The scenario engine is purely deterministic. AI recommendations will sit above this layer to suggest parameters, but the evaluation happens here.
2.  **No Extrapolated Costs:** Missing costs mean missing financial impacts.
3.  **Positive Quantities:** Activity quantities cannot be reduced below zero.
4.  **Unit Compatibility:** Fuel substitutions require explicit conversion multipliers. The engine does not guess energy densities.

## 7. Auditability and Traceability

Because the scenario engine reuses the exact same `CarbonCalculator`, every scenario result includes a complete `CalculationTrace`. You can inspect the exact emission factor, unit conversion, and formula used to generate the scenario emissions, providing full transparency for audits and judge reviews.
