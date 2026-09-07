"""
End-to-End Pipeline Demonstration.

This script executes ALL 7 phases of the EcoAudit AI backend in a single chain:
1. Data Ingestion (Reads CSV)
2. AI Classification (Mock or Gemini)
3. Domain Validation
4. Deterministic Carbon Calculation
5. Carbon Intelligence / Hotspot Analysis
6. Scenario Simulation
7. AI Recommendations

Usage:
    python scripts/demo_end_to_end.py
"""

import csv
import sys
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ecoaudit.ai.mock_provider import MockClassifier
from ecoaudit.ai.pipeline import ClassificationPipeline
from ecoaudit.carbon.calculator import CarbonCalculator
from ecoaudit.carbon.factors import FactorNotFoundError, EmissionFactorRegistry
from ecoaudit.carbon.data_loader import load_factors_from_json
from ecoaudit.intelligence.analyzer import CarbonAnalyzer
from ecoaudit.optimization.engine import ScenarioEngine
from ecoaudit.recommendation.engine import RecommendationEngine

def main() -> None:
    print("=" * 70)
    print("   ECOAUDIT AI : END-TO-END PIPELINE (PHASES 1-7)")
    print("=" * 70)

    # ---------------------------------------------------------
    # PHASE 1 & 2: Set up the Deterministic Core & Emission Factors
    # ---------------------------------------------------------
    print("\n[1/7] Loading deterministic core and emission factors...")
    registry = EmissionFactorRegistry()
    factors_dir = Path(__file__).parent.parent / "data" / "factors"
    load_factors_from_json(factors_dir / "defra_2024.json", registry, is_test_data=False)
    load_factors_from_json(factors_dir / "egypt_mena_proxy.json", registry, is_test_data=False)
    
    calculator = CarbonCalculator(registry)
    print(f"      Loaded {len(registry)} emission factors from real datasets.")

    # ---------------------------------------------------------
    # PHASE 3: Read Dataset
    # ---------------------------------------------------------
    print("\n[2/7] Ingesting messy corporate dataset...")
    csv_path = Path(__file__).parent.parent / "data" / "demo" / "synthetic_company_data.csv"
    
    raw_rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            raw_rows.append(row)
            
    print(f"      Read {len(raw_rows)} raw rows from {csv_path.name}")

    # ---------------------------------------------------------
    # PHASE 4: AI Extraction & Classification
    # ---------------------------------------------------------
    print("\n[3/7] AI Extraction & Classification Pipeline...")
    # NOTE: We use MockClassifier so it runs instantly without an API key.
    # To use real AI: from ecoaudit.ai.gemini_provider import GeminiClient
    ai_provider = MockClassifier()
    pipeline = ClassificationPipeline(ai_provider)
    
    valid_activities = []
    invalid_count = 0
    
    for i, row in enumerate(raw_rows, start=2):
        record = pipeline.classify_and_validate(row, source_row=i)
        if record.activity_data:
            valid_activities.append(record.activity_data)
        else:
            invalid_count += 1
            
    print(f"      Valid Activity Records Extracted: {len(valid_activities)}")
    print(f"      Validation Errors/Rejections: {invalid_count}")

    # ---------------------------------------------------------
    # PHASE 1: Deterministic Carbon Calculation
    # ---------------------------------------------------------
    from ecoaudit.carbon.validation import ValidationError

    print("\n[4/7] Running Deterministic Carbon Calculation Engine...")
    
    # We must pair each valid activity with the correct emission factor
    calculable_pairs = []
    for act in valid_activities:
        # Use a default fallback of 2024 / UK for this demo
        try:
            # First try exact match
            factor = registry.lookup(
                activity_type=act.metadata["activity_type"],
                year=2024,
                country="UK",
                category=act.category
            )
            # Pre-validate compatibility to avoid crashing the batch
            try:
                calculator.calculate(act, factor)
                calculable_pairs.append((act, factor))
            except ValidationError as ve:
                print(f"      Warning: Activity {act.activity_id} rejected: {ve}")
        except FactorNotFoundError:
            try:
                # Try without category constraint
                factor = registry.lookup(
                    activity_type=act.metadata["activity_type"],
                    year=2024,
                    country="UK"
                )
                try:
                    calculator.calculate(act, factor)
                    calculable_pairs.append((act, factor))
                except ValidationError as ve:
                    print(f"      Warning: Activity {act.activity_id} rejected: {ve}")
            except FactorNotFoundError:
                print(f"      Warning: No emission factor found for {act.metadata['activity_type']}")
            
    batch_result = calculator.calculate_batch(calculable_pairs)
    print(f"      Successfully Calculated: {len(batch_result.results)}")
    print(f"      Total Footprint Calculated: {batch_result.total_emissions:,.2f} kgCO2e")

    # ---------------------------------------------------------
    # PHASE 5: Carbon Intelligence & Hotspot Analysis
    # ---------------------------------------------------------
    print("\n[5/7] Carbon Intelligence & Hotspot Analysis...")
    analyzer = CarbonAnalyzer()
    report = analyzer.analyze(batch_result)
    
    print(f"      Insights Generated: {len(report.insights)}")
    if report.hotspots:
        top_hotspot = report.hotspots[0]
        print(f"      Critical Hotspot Identified: '{top_hotspot.label}' "
              f"({top_hotspot.percentage_of_total:.1f}% of total emissions)")

    # ---------------------------------------------------------
    # PHASES 6 & 7: Optimization & AI Recommendation Engine
    # ---------------------------------------------------------
    print("\n[6/7] Generating AI Recommendations & Simulating Interventions...")
    scenario_engine = ScenarioEngine(calculator)
    rec_engine = RecommendationEngine(ai_provider, scenario_engine)
    
    recommendations = rec_engine.generate_recommendations(report, batch_result)

    print("\n" + "=" * 70)
    print("   FINAL AI RECOMMENDATION OUTPUT")
    print("=" * 70)
    
    if not recommendations:
        print("No valid recommendations generated.")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"[{i}] {rec.title}")
        print(f"    Status: {rec.status.value.upper()}")
        print(f"    Rationale: {rec.rationale}")
        print(f"    AI Explanation: {rec.explanation}")
        
        if rec.scenario_result:
            c_impact = rec.scenario_result.carbon_impact
            print(f"    Deterministic Verification -> "
                  f"Reduces emissions by {c_impact.absolute_reduction:,.2f} kgCO2e "
                  f"({c_impact.percentage_reduction:.1f}%)")
        print("-" * 70)
        
    print("\nPipeline execution complete!")

if __name__ == "__main__":
    main()
