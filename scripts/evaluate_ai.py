"""
AI Evaluation Script.

Measures AI classification accuracy against the manually labeled
benchmark dataset. Reports measured metrics — never invents them.

Usage:
    python scripts/evaluate_ai.py
"""

import csv
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ecoaudit.ai.mock_provider import MockClassifier
from ecoaudit.ai.pipeline import ClassificationPipeline


BENCHMARK_PATH = Path("data/evaluation/labeled_benchmark.csv")
RESULTS_DIR = Path("validation")


def main() -> None:
    pipeline = ClassificationPipeline(MockClassifier())

    # Read labeled benchmark
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    activity_correct = 0
    scope_correct = 0
    category_correct = 0
    unit_correct = 0
    rejected = 0
    needs_review_count = 0
    invalid_output = 0

    details: list[dict] = []

    for i, row in enumerate(rows, start=2):
        raw_row = {
            "Facility": row.get("raw_description", ""),
            "Utility": row.get("raw_description", ""),
            "Usage Amount": row.get("raw_quantity", ""),
            "UOM": row.get("raw_unit", ""),
        }
        expected_activity = row.get("expected_activity_type", "").strip()
        expected_scope = row.get("expected_scope", "").strip().lower()
        expected_category = row.get("expected_category", "").strip().lower()
        expected_unit = row.get("expected_unit", "").strip().lower()

        record = pipeline.classify_and_validate(raw_row, source_row=i)

        if record.candidate is None:
            invalid_output += 1
            rejected += 1
            details.append({
                "row": i,
                "input": row.get("raw_description", ""),
                "error": record.error or "No candidate",
                "expected_activity": expected_activity,
                "predicted_activity": None,
                "match": False,
            })
            continue

        candidate = record.candidate
        predicted_activity = candidate.activity_type.lower().strip()
        predicted_scope = candidate.scope.lower().strip()
        predicted_category = candidate.category.lower().strip()
        predicted_unit = candidate.unit.lower().strip()

        act_match = predicted_activity == expected_activity
        scope_match = predicted_scope == expected_scope
        cat_match = predicted_category == expected_category
        unit_match = predicted_unit == expected_unit

        if act_match:
            activity_correct += 1
        if scope_match:
            scope_correct += 1
        if cat_match:
            category_correct += 1
        if unit_match:
            unit_correct += 1

        if candidate.needs_review or (record.activity_data and record.activity_data.metadata and record.activity_data.metadata.get("ai_needs_review")):
            needs_review_count += 1

        if record.validation_result and not record.validation_result.is_valid:
            rejected += 1

        details.append({
            "row": i,
            "input": row.get("raw_description", "")[:60],
            "expected_activity": expected_activity,
            "predicted_activity": predicted_activity,
            "activity_match": act_match,
            "expected_scope": expected_scope,
            "predicted_scope": predicted_scope,
            "scope_match": scope_match,
            "expected_category": expected_category,
            "predicted_category": predicted_category,
            "category_match": cat_match,
            "confidence": candidate.confidence,
            "needs_review": candidate.needs_review,
        })

    # Report
    print("=" * 60)
    print("EcoAudit AI Evaluation Report (Mock Provider)")
    print("=" * 60)
    print(f"Total records:            {total}")
    print(f"Activity accuracy:        {activity_correct}/{total} ({activity_correct/total*100:.1f}%)")
    print(f"Scope accuracy:           {scope_correct}/{total} ({scope_correct/total*100:.1f}%)")
    print(f"Category accuracy:        {category_correct}/{total} ({category_correct/total*100:.1f}%)")
    print(f"Unit accuracy:            {unit_correct}/{total} ({unit_correct/total*100:.1f}%)")
    print(f"Rejected/invalid:         {rejected}/{total} ({rejected/total*100:.1f}%)")
    print(f"Flagged for review:       {needs_review_count}/{total} ({needs_review_count/total*100:.1f}%)")
    print()

    # Show mismatches
    mismatches = [d for d in details if not d.get("activity_match", False)]
    if mismatches:
        print(f"--- Activity Mismatches ({len(mismatches)}) ---")
        for m in mismatches[:15]:
            print(f"  Row {m['row']}: '{m['input'][:40]}' -> expected={m['expected_activity']}, got={m.get('predicted_activity', 'N/A')}")
        if len(mismatches) > 15:
            print(f"  ... and {len(mismatches) - 15} more")

    # Save detailed results
    RESULTS_DIR.mkdir(exist_ok=True)
    results = {
        "total_records": total,
        "activity_accuracy": round(activity_correct / total, 4),
        "scope_accuracy": round(scope_correct / total, 4),
        "category_accuracy": round(category_correct / total, 4),
        "unit_accuracy": round(unit_correct / total, 4),
        "rejection_rate": round(rejected / total, 4),
        "review_rate": round(needs_review_count / total, 4),
        "details": details,
    }

    with open(RESULTS_DIR / "ai_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to {RESULTS_DIR / 'ai_evaluation_results.json'}")


if __name__ == "__main__":
    main()
