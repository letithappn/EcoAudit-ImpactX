"""EcoAudit AI unified end-to-end pipeline CLI."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ecoaudit.pipeline import PipelineExecution, execute_pipeline


logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger("pipeline")


def _compact_output(execution: PipelineExecution) -> dict[str, object]:
    return {
        "statistics": execution.statistics,
        "carbon_footprint": {
            "total_kgCO2e": float(execution.batch_result.total_emissions),
            "scope_totals": {
                key.value: float(value)
                for key, value in execution.batch_result.scope_totals.items()
            },
        },
        "hotspots": [
            {
                "label": hotspot.label,
                "percentage": float(hotspot.percentage_of_total),
                "emissions": float(hotspot.emissions),
            }
            for hotspot in execution.intelligence.hotspots
        ],
        "recommendations": [
            {
                "title": recommendation.title,
                "status": recommendation.status.value,
                "rationale": recommendation.rationale,
                "explanation": recommendation.explanation,
                "carbon_savings_kgCO2e": (
                    float(recommendation.scenario_result.carbon_impact.absolute_reduction)
                    if recommendation.scenario_result else None
                ),
                "cost_savings": (
                    float(recommendation.scenario_result.financial_impact.absolute_savings)
                    if recommendation.scenario_result
                    and recommendation.scenario_result.financial_impact.is_available
                    else None
                ),
            }
            for recommendation in execution.recommendations
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="EcoAudit AI Unified Pipeline")
    parser.add_argument("input", type=str, help="Path to the input CSV dataset")
    parser.add_argument(
        "--provider",
        choices=["mock", "gemini"],
        default="mock",
        help="AI provider to use",
    )
    parser.add_argument("--year", type=int, default=2024, help="Target factor year")
    parser.add_argument("--country", type=str, default="UK", help="Factor country")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    try:
        execution = execute_pipeline(
            args.input,
            provider=args.provider,
            year=args.year,
            country=args.country,
        )
    except FileNotFoundError as error:
        logger.error(str(error))
        raise SystemExit(1) from error
    except Exception as error:
        logger.error("Pipeline failed: %s", error)
        raise SystemExit(1) from error

    if args.json:
        print(json.dumps(_compact_output(execution), indent=2))
        return

    stats = execution.statistics
    print("=== EcoAudit AI Pipeline ===")
    print(f"Loaded {execution.factor_count} real factors.")
    print(f"Ingested {stats['total_rows']} rows from {Path(args.input).name}")
    print("Using Deterministic Mock AI." if args.provider == "mock" else "Using Gemini API.")
    print(f"Successfully parsed: {stats['successfully_parsed']} rows")
    print(f"AI classified: {stats['ai_classified']} rows")
    print(f"Classified & Validated: {stats['validated']}")
    print(f"Needs review: {stats['needs_review']}")
    print(f"Unsupported: {stats['unsupported']}")
    print(f"Rejected: {stats['rejected_ai']}")
    print(f"Successfully calculated: {stats['calculated']} activity records")
    print(f"Calculated source rows: {stats['calculated_rows']}")
    print(f"Coverage: {stats['coverage_percentage']:.2f}%")
    print(f"Calculation rejections: {stats['rejected_calculation']}")
    print(f"Total Carbon Footprint: {execution.batch_result.total_emissions:,.2f} kgCO2e")
    print(f"Generated {len(execution.intelligence.insights)} insights.")
    print(f"Identified {len(execution.intelligence.hotspots)} hotspots.")
    print(f"Generated {len(execution.recommendations)} recommendations.")


if __name__ == "__main__":
    main()
