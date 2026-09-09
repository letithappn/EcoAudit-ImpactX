"""
AI Classification Pipeline.

Orchestrates the full flow:
    Raw Row → AI Classification → Post-AI Validation → ActivityData

This is the single entry point for AI-assisted data processing.
The pipeline uses the existing deterministic engine for calculations —
it only replaces the hardcoded adapter logic with AI-powered classification.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace

from ecoaudit.ai.providers import AIClassifier
from ecoaudit.ai.schemas import ActivityCandidate
from ecoaudit.ai.validation import validate_candidate
from ecoaudit.carbon.models import ActivityData
from ecoaudit.ingestion.normalizer import PreparedRow, prepare_row, read_csv_rows

logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    """Statistics from a pipeline run."""

    total_rows: int = 0
    successfully_parsed: int = 0
    activity_records: int = 0
    classified: int = 0
    validated: int = 0
    rejected: int = 0
    unsupported: int = 0
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
        classification_row: dict[str, str] | None = None,
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
            candidate = self._classifier.classify_row(
                classification_row or raw_row,
                source_row=source_row,
            )
            record.candidate = candidate
        except Exception as e:
            record.error = f"AI classification failed: {e}"
            logger.error("Classification error on row %s: %s", source_row, e)
            return record

        return self._validate_record(record)

    def _validate_record(self, record: ClassificationRecord) -> ClassificationRecord:
        """Apply the post-AI firewall to a candidate already produced."""
        if record.candidate is None:
            return record

        try:
            validation_result = validate_candidate(record.candidate)
            record.validation_result = validation_result
        except Exception as e:
            record.error = f"Validation failed: {e}"
            logger.error("Validation error on row %s: %s", record.source_row, e)
            return record

        # Step 3: Extract validated ActivityData (if valid)
        if validation_result.is_valid:
            record.activity_data = validation_result.activity_data

        return record

    def _record_stats(self, record: ClassificationRecord, stats: PipelineStats) -> None:
        stats.activity_records += 1
        if record.error:
            stats.rejected += 1
            stats.errors.append(f"Row {record.source_row}: {record.error}")
            return

        stats.classified += 1
        if record.candidate and record.candidate.activity_type.lower().strip() == "unknown":
            stats.unknown_activity += 1
            stats.unsupported += 1

        if record.validation_result and record.validation_result.is_valid:
            stats.validated += 1
            if record.activity_data and record.activity_data.metadata:
                if record.activity_data.metadata.get("ai_needs_review"):
                    stats.needs_review += 1
        else:
            stats.rejected += 1
            if record.validation_result:
                for error in record.validation_result.errors:
                    stats.errors.append(f"Row {record.source_row}: {error}")
            if record.candidate and record.candidate.needs_review:
                stats.needs_review += 1

    def process_rows(
        self,
        raw_rows: list[dict[str, str]],
        *,
        batch_size: int = 25,
    ) -> tuple[list[ClassificationRecord], PipelineStats]:
        """Process already-read rows while isolating failures per activity.

        Batching uses the provider's structured batch interface when available
        (important for real Gemini use), while validation remains row-by-row.
        A wide source row may yield several activity records, but all records
        retain the same source row and original data for traceability.
        """
        records: list[ClassificationRecord] = []
        stats = PipelineStats(
            total_rows=len(raw_rows),
            successfully_parsed=len(raw_rows),
        )
        pending: list[PreparedRow] = []

        def flush(items: list[PreparedRow]) -> None:
            if not items:
                return
            try:
                candidates = self._classifier.classify_batch(
                    [item.classification_row for item in items],
                    start_row=items[0].source_row,
                )
            except Exception as error:
                logger.error("Batch classification failed: %s", error)
                candidates = []

            if len(candidates) != len(items):
                # Providers can return a short/malformed batch. Retry each row
                # independently so one bad response cannot discard the batch.
                for item in items:
                    record = self.classify_and_validate(
                        item.raw_row,
                        source_row=item.source_row,
                        classification_row=item.classification_row,
                    )
                    records.append(record)
                    self._record_stats(record, stats)
                return

            for item, candidate in zip(items, candidates):
                # Source row identity belongs to the input file, not to a
                # provider's batch-relative numbering.
                candidate = replace(candidate, source_row=item.source_row)
                record = self._validate_record(
                    ClassificationRecord(
                        raw_row=item.raw_row,
                        source_row=item.source_row,
                        candidate=candidate,
                    )
                )
                records.append(record)
                self._record_stats(record, stats)

        for source_row, raw_row in enumerate(raw_rows, start=2):
            try:
                prepared = prepare_row(raw_row, source_row)
            except Exception as error:
                record = ClassificationRecord(
                    raw_row=raw_row,
                    source_row=source_row,
                    error=f"Input normalization failed: {error}",
                )
                records.append(record)
                self._record_stats(record, stats)
                continue

            pending.extend(prepared)
            if len(pending) >= batch_size:
                flush(pending)
                pending = []

        flush(pending)
        logger.info(
            "Pipeline complete: %d source rows, %d activity records, %d validated, %d rejected, %d review",
            stats.total_rows,
            stats.activity_records,
            stats.validated,
            stats.rejected,
            stats.needs_review,
        )
        return records, stats

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
        return self.process_rows(read_csv_rows(filepath))

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
