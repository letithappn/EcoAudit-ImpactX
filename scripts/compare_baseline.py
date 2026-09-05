"""
Baseline Comparison Script.

Compares:
- Method A: Deterministic SyntheticCompanyAdapter (Phase 3)
- Method B: AI-assisted ClassificationPipeline (Phase 4)

Same input → Same calculator → Only the interpretation layer differs.

Usage:
    python scripts/compare_baseline.py
"""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ecoaudit.ai.mock_provider import MockClassifier
from ecoaudit.ai.pipeline import ClassificationPipeline
from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.data_loader import load_factors_from_json
from ecoaudit.carbon.factors import EmissionFactorRegistry
from ecoaudit.ingestion.adapters import SyntheticCompanyAdapter

DATA_FILE = Path("data/demo/synthetic_company_data.csv")
FACTORS_DIR = Path("data/factors")


def run_deterministic_baseline() -> dict:
    """Method A: Deterministic adapter from Phase 3."""
    registry = EmissionFactorRegistry()
    load_factors_from_json(FACTORS_DIR / "defra_2024.json", registry, is_test_data=False)
    load_factors_from_json(FACTORS_DIR / "egypt_mena_proxy.json", registry, is_test_data=False)
    calculator = CarbonCalculator(registry)

    adapter = SyntheticCompanyAdapter()
    activities = list(adapter.normalize(str(DATA_FILE)))

    calculated = 0
    rejected = 0
    total_emissions = Decimal("0")

    for act in activities:
        try:
            factor = registry.lookup(
                activity_type=act.metadata["activity_type"],
                year=2024,
                country="UK",
                category=act.category,
            )
            result = calculator.calculate(act, factor)
            total_emissions += result.emissions_value
            calculated += 1
        except Exception:
            rejected += 1

    return {
        "method": "Deterministic Adapter (Phase 3)",
        "total_rows_in_file": 7,  # Known from the CSV
        "activities_extracted": len(activities),
        "successfully_calculated": calculated,
        "rejected": rejected,
        "total_emissions_kgCO2e": float(total_emissions),
    }


def run_ai_pipeline() -> dict:
    """Method B: AI-assisted classification pipeline."""
    registry = EmissionFactorRegistry()
    load_factors_from_json(FACTORS_DIR / "defra_2024.json", registry, is_test_data=False)
    load_factors_from_json(FACTORS_DIR / "egypt_mena_proxy.json", registry, is_test_data=False)
    calculator = CarbonCalculator(registry)

    pipeline = ClassificationPipeline(MockClassifier())
    records, stats = pipeline.process_csv(str(DATA_FILE))
    validated_activities = pipeline.get_validated_activities(records)

    calculated = 0
    rejected_calc = 0
    total_emissions = Decimal("0")

    for act in validated_activities:
        try:
            factor = registry.lookup(
                activity_type=act.metadata["activity_type"],
                year=2024,
                country="UK",
                category=act.category,
            )
            result = calculator.calculate(act, factor)
            total_emissions += result.emissions_value
            calculated += 1
        except Exception:
            rejected_calc += 1

    return {
        "method": "AI Pipeline (Phase 4, Mock Provider)",
        "total_rows_in_file": stats.total_rows,
        "activities_extracted": len(validated_activities),
        "pipeline_rejected": stats.rejected,
        "flagged_for_review": stats.needs_review,
        "successfully_calculated": calculated,
        "rejected_at_calculation": rejected_calc,
        "total_emissions_kgCO2e": float(total_emissions),
    }


def main() -> None:
    print("=" * 60)
    print("EcoAudit: Deterministic vs AI Pipeline Comparison")
    print("=" * 60)
    print(f"Input: {DATA_FILE}")
    print()

    result_a = run_deterministic_baseline()
    result_b = run_ai_pipeline()

    print("--- Method A: Deterministic Adapter ---")
    for k, v in result_a.items():
        print(f"  {k}: {v}")
    print()

    print("--- Method B: AI Pipeline ---")
    for k, v in result_b.items():
        print(f"  {k}: {v}")
    print()

    print("--- Comparison ---")
    print(f"  Deterministic extracted: {result_a['activities_extracted']} activities")
    print(f"  AI extracted:           {result_b['activities_extracted']} activities")
    print(f"  Deterministic emissions: {result_a['total_emissions_kgCO2e']:.2f} kgCO2e")
    print(f"  AI emissions:           {result_b['total_emissions_kgCO2e']:.2f} kgCO2e")

    # Key insight
    if result_b["activities_extracted"] >= result_a["activities_extracted"]:
        print("\n  [OK] AI pipeline extracted at least as many valid activities.")
    else:
        print("\n  [WARN] AI pipeline extracted fewer activities -- needs investigation.")

    print("\n  Note: The CALCULATION ENGINE is identical in both methods.")
    print("  Only the data INTERPRETATION layer differs.")


if __name__ == "__main__":
    main()
