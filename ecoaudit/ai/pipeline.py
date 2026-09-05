"""
AI Classification Pipeline.

Orchestrates the full flow:
    Raw Row → AI Classification → Post-AI Validation → ActivityData

This is the single entry point for AI-assisted data processing.
The pipeline uses the existing deterministic engine for calculations —
it only replaces the hardcoded adapter logic with AI-powered classification.
"""

from __future__ import annotations

import csv
import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

from ecoaudit.ai.providers import AIClassifier
from ecoaudit.ai.schemas import ActivityCandidate, CandidateValidationResult
from ecoaudit.ai.validation import validate_candidate
from ecoaudit.carbon.models import ActivityData

logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    """Statistics from a pipeline run."""

    total_rows: int = 0
    classified: int = 0
    validated: int = 0
    rejected: int = 0
    needs_review: int = 0
    unknown_activity: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Fraction of rows that produced valid ActivityData."""
        return self.validated / self.total_rows if self.total_rows > 0 else 0.0

    @property
    def review_rate(self) -> float:
        """Fraction of rows flagged for human review."""
        return self.needs_review / self.total_rows if self.total_rows > 0 else 0.0


@dataclass
class ClassificationRecord:
    """A complete record of one row's journey through the pipeline.

    Captures everything from raw input through AI classification to
    validation outcome, enabling full auditability and debugging.
    """

    raw_row: dict[str, str]
    source_row: int
    candidate: ActivityCandidate | None = None
    validation_result: CandidateValidationResult | None = None
    activity_data: ActivityData | None = None
    error: str | None = None


class ClassificationPipeline:
    """AI-powered classification pipeline.

    Replaces hardcoded deterministic adapters with AI classification
    while preserving the same output contract (ActivityData objects).

    Usage:
        from ecoaudit.ai.mock_provider import MockClassifier
        pipeline = ClassificationPipeline(MockClassifier())
        results = pipeline.process_csv("data/demo/synthetic_company_data.csv")
    """

    def __init__(self, classifier: AIClassifier) -> None:
        """Initialize the pipeline with an AI classifier.

        Args:
            classifier: An AI provider implementing the AIClassifier protocol.
        """
        self._classifier = classifier

    def classify_and_validate(
        self,
        raw_row: dict[str, str],
        source_row: int | None = None,
    ) -> ClassificationRecord:
        """Process a single raw row through the full pipeline.

        Args:
            raw_row: Dict of column_name -> value from the raw data.
            source_row: Optional row number for traceability.

        Returns:
            A ClassificationRecord with the full audit trail.
        """
        record = ClassificationRecord(
            raw_row=raw_row,
            source_row=source_row or 0,
        )

        # Step 1: AI Classification
        try:
            candidate = self._classifier.classify_row(raw_row, source_row=source_row)
            record.candidate = candidate
        except Exception as e:
            record.error = f"AI classification failed: {e}"
            logger.error("Classification error on row %s: %s", source_row, e)
            return record

        # Step 2: Post-AI Validation (the firewall)
        try:
            validation_result = validate_candidate(candidate)
            record.validation_result = validation_result
        except Exception as e:
            record.error = f"Validation failed: {e}"
            logger.error("Validation error on row %s: %s", source_row, e)
            return record

        # Step 3: Extract validated ActivityData (if valid)
        if validation_result.is_valid:
            record.activity_data = validation_result.activity_data

        return record

    def process_csv(
        self,
        filepath: str,
    ) -> tuple[list[ClassificationRecord], PipelineStats]:
        """Process an entire CSV file through the AI pipeline.

        Args:
            filepath: Path to the CSV file.

        Returns:
            Tuple of (list of ClassificationRecords, PipelineStats).
        """
        records: list[ClassificationRecord] = []
        stats = PipelineStats()

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2):
                stats.total_rows += 1

                record = self.classify_and_validate(row, source_row=row_idx)
                records.append(record)

                if record.error:
                    stats.rejected += 1
                    stats.errors.append(
                        f"Row {row_idx}: {record.error}"
                    )
                    continue

                stats.classified += 1

                if record.candidate and record.candidate.activity_type == "unknown":
                    stats.unknown_activity += 1

                if record.validation_result and record.validation_result.is_valid:
                    stats.validated += 1
                    # Check if flagged for review
                    if record.activity_data and record.activity_data.metadata:
                        if record.activity_data.metadata.get("ai_needs_review"):
                            stats.needs_review += 1
                else:
                    stats.rejected += 1
                    if record.validation_result:
                        for err in record.validation_result.errors:
                            stats.errors.append(f"Row {row_idx}: {err}")

                    # Also count flagged-for-review rejects
                    if record.candidate and record.candidate.needs_review:
                        stats.needs_review += 1

        logger.info(
            "Pipeline complete: %d rows, %d validated, %d rejected, %d review",
            stats.total_rows,
            stats.validated,
            stats.rejected,
            stats.needs_review,
        )

        return records, stats

    def get_validated_activities(
        self,
        records: list[ClassificationRecord],
    ) -> list[ActivityData]:
        """Extract only the validated ActivityData from pipeline records.

        This is the list of activities safe to feed into the deterministic
        carbon engine.

        Args:
            records: List of ClassificationRecords from process_csv.

        Returns:
            List of validated ActivityData objects.
        """
        return [
            record.activity_data
            for record in records
            if record.activity_data is not None
        ]
