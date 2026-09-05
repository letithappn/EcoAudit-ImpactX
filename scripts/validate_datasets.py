"""
Phase 3 Dataset Validation Script.

Reads the raw CSV datasets, adapts them into ActivityData, runs them
through the CarbonCalculator, and produces a final validation report.
"""

import json
from pathlib import Path

from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.data_loader import load_factors_from_json
from ecoaudit.carbon.factors import EmissionFactorRegistry
from ecoaudit.ingestion.adapters import (
    AustinFleetAdapter,
    ChicagoEnergyAdapter,
    SyntheticCompanyAdapter,
)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
DEMO_DIR = DATA_DIR / "demo"
FACTORS_DIR = DATA_DIR / "factors"
VALIDATION_DIR = Path("validation")

def main() -> None:
    # 1. Initialize Registry and Calculator with REAL data
    registry = EmissionFactorRegistry()
    load_factors_from_json(FACTORS_DIR / "defra_2024.json", registry, is_test_data=False)
    load_factors_from_json(FACTORS_DIR / "egypt_mena_proxy.json", registry, is_test_data=False)
    
    calculator = CarbonCalculator(registry)
    
    results_summary = []
    
    # 2. Process Datasets
    datasets = [
        ("Chicago Energy Benchmarking", RAW_DIR / "chicago_energy_2022.csv", ChicagoEnergyAdapter(), 2024, "UK"),
        ("Austin Fleet Fuel", RAW_DIR / "austin_fleet_fuel.csv", AustinFleetAdapter(), 2024, "UK"),
        ("Synthetic Company Data", DEMO_DIR / "synthetic_company_data.csv", SyntheticCompanyAdapter(), 2024, "Egypt")
    ]
    
    report_lines = [
        "# Phase 3 End-to-End Validation Report\n",
        "This report demonstrates the end-to-end ingestion and calculation of public activity datasets using the deterministic carbon engine.\n"
    ]
    
    for name, filepath, adapter, year, country in datasets:
        print(f"Processing {name}...")
        
        # Ingest
        activities = list(adapter.normalize(str(filepath)))
        
        # Calculate
        batch_inputs = []
        rejected = 0
        for act in activities:
            try:
                # We need to map activity to factor manually in batch prep
                factor = registry.lookup(
                    activity_type=act.metadata["activity_type"],
                    year=year,
                    country=country,
                    category=act.category
                )
                batch_inputs.append((act, factor))
            except Exception as e:
                rejected += 1
                print(f"Warning: Rejected activity {act.activity_id}: {e}")
                
        batch_result = calculator.calculate_batch(batch_inputs)
        
        # Summarize
        summary = {
            "dataset": name,
            "total_records_ingested": len(activities),
            "successfully_calculated": len(batch_result.results),
            "rejected_records": rejected,
            "total_emissions_kgCO2e": float(batch_result.total_emissions),
            "scope_totals": {k.value: float(v) for k, v in batch_result.scope_totals.items()}
        }
        results_summary.append(summary)
        
        # Add to markdown report
        report_lines.extend([
            f"## {name}",
            f"- **Records Ingested:** {len(activities)}",
            f"- **Successfully Calculated:** {len(batch_result.results)}",
            f"- **Rejected Records (Missing Factor):** {rejected}",
            f"- **Total Emissions:** {batch_result.total_emissions:,.2f} kgCO2e",
            ""
        ])
        for scope, val in batch_result.scope_totals.items():
            report_lines.append(f"  - **{scope.value}:** {val:,.2f} kgCO2e")
        report_lines.append("\n---\n")
        
    # Write JSON results
    with open(VALIDATION_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)
        
    # Write Markdown report
    with open(VALIDATION_DIR / "validation_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"\nValidation complete. Reports written to {VALIDATION_DIR}/")


if __name__ == "__main__":
    main()
