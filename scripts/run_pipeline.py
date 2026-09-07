"""
EcoAudit AI Unified End-to-End Pipeline.

This script executes all 7 backend phases on an arbitrary CSV file.
Usage:
    python scripts/run_pipeline.py data/demo/synthetic_test_dataset.csv --provider mock --year 2024 --country UK
"""

import argparse
import csv
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ecoaudit.ai.mock_provider import MockClassifier
from ecoaudit.ai.gemini_provider import GeminiClient, GeminiClassifier
from ecoaudit.ai.pipeline import ClassificationPipeline
from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import FactorNotFoundError, EmissionFactorRegistry
from ecoaudit.carbon.data_loader import load_factors_from_json
from ecoaudit.carbon.validation import ValidationError
from ecoaudit.intelligence.analyzer import CarbonAnalyzer
from ecoaudit.optimization.engine import ScenarioEngine
from ecoaudit.recommendation.engine import RecommendationEngine

logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger("pipeline")


def _print_section(title: str) -> None:
    print(f"\n{'-' * 60}")
    print(f" {title.upper()}")
    print(f"{'-' * 60}")


def main() -> None:
    parser = argparse.ArgumentParser(description="EcoAudit AI Unified Pipeline")
    parser.add_argument("input", type=str, help="Path to the input CSV dataset")
    parser.add_argument("--provider", type=str, choices=["mock", "gemini"], default="mock", help="AI Provider to use")
    parser.add_argument("--year", type=int, default=2024, help="Target year for emission factors")
    parser.add_argument("--country", type=str, default="UK", help="Target country for emission factors")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    args = parser.parse_args()

    # Disable stdout prints if --json is passed
    original_stdout = sys.stdout
    if args.json:
        sys.stdout = open(os.devnull, 'w')

    print("=== EcoAudit AI Pipeline ===\n")
    
    # ---------------------------------------------------------
    # 1. SETUP
    # ---------------------------------------------------------
    _print_section("[1/7] Initialization & Ingestion")
    
    csv_path = Path(args.input)
    if not csv_path.exists():
        logger.error(f"Input file not found: {csv_path}")
        sys.exit(1)

    print(f"Loading emission factors for Year: {args.year}, Country: {args.country}")
    registry = EmissionFactorRegistry()
    factors_dir = Path(__file__).parent.parent / "data" / "factors"
    load_factors_from_json(factors_dir / "defra_2024.json", registry, is_test_data=False)
    load_factors_from_json(factors_dir / "egypt_mena_proxy.json", registry, is_test_data=False)
    calculator = CarbonCalculator(registry)
    print(f"Loaded {len(registry)} real factors.")

    raw_rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_rows.append(row)
    print(f"Ingested {len(raw_rows)} rows from {csv_path.name}")

    # ---------------------------------------------------------
    # 2 & 3. AI CLASSIFICATION & VALIDATION
    # ---------------------------------------------------------
    _print_section("[2/7 & 3/7] AI Classification & Validation")
    
    if args.provider == "gemini":
        print("Using Gemini API...")
        ai_provider = GeminiClassifier()
        rec_ai_provider = GeminiClient()
    else:
        print("Using Deterministic Mock AI...")
        ai_provider = MockClassifier()
        rec_ai_provider = MockClassifier()

    pipeline = ClassificationPipeline(ai_provider)
    valid_activities = []
    invalid_count = 0
    needs_review_count = 0

    for i, row in enumerate(raw_rows, start=2):
        record = pipeline.classify_and_validate(row, source_row=i)
        if record.activity_data:
            valid_activities.append(record.activity_data)
            if record.activity_data.metadata and record.activity_data.metadata.get("ai_needs_review"):
                needs_review_count += 1
        else:
            invalid_count += 1
            if record.validation_result and record.validation_result.errors:
                err_str = ", ".join(record.validation_result.errors)
                print(f"Row {i} REJECTED: {err_str}")
            else:
                print(f"Row {i} REJECTED: {record.error or 'Invalid candidate'}")

    print(f"\nStats:")
    print(f"  Classified & Validated: {len(valid_activities)}")
    print(f"  Rejected: {invalid_count}")
    print(f"  Flagged for Review: {needs_review_count}")

    if not valid_activities:
        print("\nNo valid activities generated. Pipeline stopping.")
        sys.exit(0)

    # ---------------------------------------------------------
    # 4. CARBON CALCULATION
    # ---------------------------------------------------------
    _print_section("[4/7] Deterministic Carbon Calculation")
    
    calculable_pairs = []
    calc_errors = 0

    for act in valid_activities:
        # 1. Exact match attempt
        try:
            factor = registry.lookup(
                activity_type=act.metadata["activity_type"],
                year=args.year,
                country=args.country,
                category=act.category
            )
        except FactorNotFoundError:
            # 2. Relaxed match attempt
            try:
                factor = registry.lookup(
                    activity_type=act.metadata["activity_type"],
                    year=args.year,
                    country=args.country
                )
            except FactorNotFoundError:
                print(f"Activity {act.activity_id} REJECTED: No emission factor found for '{act.metadata['activity_type']}'")
                calc_errors += 1
                continue
        
        # 3. Validation
        try:
            calculator.calculate(act, factor)
            calculable_pairs.append((act, factor))
        except ValidationError as ve:
            print(f"Activity {act.activity_id} REJECTED: {ve}")
            calc_errors += 1

    if not calculable_pairs:
        print("\nNo calculable activities remaining. Pipeline stopping.")
        sys.exit(0)

    batch_result = calculator.calculate_batch(calculable_pairs)
    print(f"Successfully calculated: {len(batch_result.results)}")
    print(f"Calculation rejections: {calc_errors}")
    print(f"Total Carbon Footprint: {batch_result.total_emissions:,.2f} kgCO2e")

    # ---------------------------------------------------------
    # 5. CARBON INTELLIGENCE
    # ---------------------------------------------------------
    _print_section("[5/7] Carbon Intelligence & Hotspots")
    
    analyzer = CarbonAnalyzer()
    report = analyzer.analyze(batch_result)
    
    print(f"Generated {len(report.insights)} insights.")
    print(f"Identified {len(report.hotspots)} hotspots.")
    if report.hotspots:
        top_hotspot = report.hotspots[0]
        print(f"Top Hotspot: {top_hotspot.label} ({top_hotspot.percentage_of_total:.1f}%)")

    # ---------------------------------------------------------
    # 6 & 7. SCENARIOS & RECOMMENDATIONS
    # ---------------------------------------------------------
    _print_section("[6/7 & 7/7] Scenarios & AI Recommendations")
    
    scenario_engine = ScenarioEngine(calculator)
    rec_engine = RecommendationEngine(rec_ai_provider, scenario_engine)
    
    recommendations = rec_engine.generate_recommendations(report, batch_result)
    
    supported_recs = 0
    rejected_recs = 0

    print("Generated Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        if str(rec.status) in ("RecommendationStatus.SUPPORTED", "RecommendationStatus.REQUIRES_REVIEW"):
            supported_recs += 1
            print(f"  [{i}] {rec.title} ({rec.status.value.upper()})")
            c_impact = rec.scenario_result.carbon_impact
            f_impact = rec.scenario_result.financial_impact
            print(f"      Carbon: {c_impact.absolute_reduction:,.2f} kgCO2e saved")
            if f_impact.is_available:
                print(f"      Financial: ${f_impact.absolute_savings:,.2f} saved")
            else:
                print("      Financial: UNAVAILABLE (Missing cost data)")
        else:
            rejected_recs += 1
            print(f"  [{i}] {rec.title} (REJECTED)")
            if rec.validation_errors:
                print(f"      Reason: {rec.validation_errors[0]}")
    
    # ---------------------------------------------------------
    # FINAL JSON OUTPUT (if requested)
    # ---------------------------------------------------------
    if args.json:
        out = {
            "statistics": {
                "total_rows": len(raw_rows),
                "validated": len(valid_activities),
                "rejected_ai": invalid_count,
                "needs_review": needs_review_count,
                "calculated": len(batch_result.results),
                "rejected_calculation": calc_errors,
                "recommendations_generated": len(recommendations),
                "recommendations_supported": supported_recs,
                "recommendations_rejected": rejected_recs,
            },
            "carbon_footprint": {
                "total_kgCO2e": float(batch_result.total_emissions),
                "scope_totals": {k.value: float(v) for k, v in batch_result.scope_totals.items()}
            },
            "hotspots": [
                {"label": h.label, "percentage": float(h.percentage_of_total), "emissions": float(h.emissions)}
                for h in report.hotspots
            ],
            "recommendations": [
                {
                    "title": r.title,
                    "status": r.status.value,
                    "rationale": r.rationale,
                    "explanation": r.explanation,
                    "carbon_savings_kgCO2e": float(r.scenario_result.carbon_impact.absolute_reduction) if r.scenario_result else None,
                    "cost_savings": float(r.scenario_result.financial_impact.absolute_savings) if r.scenario_result and r.scenario_result.financial_impact.is_available else None
                }
                for r in recommendations
            ]
        }
        print(json.dumps(out, indent=2), file=original_stdout)
    else:
        _print_section("=== RESULTS SUMMARIZED ===")
        print("Done.")

if __name__ == "__main__":
    main()
