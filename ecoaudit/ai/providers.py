"""
AI provider abstraction.

Defines the AIClassifier protocol that all AI providers must implement.
This allows swapping providers (Gemini, OpenAI, mock) without changing
the pipeline.
"""

from __future__ import annotations

from typing import Protocol

from ecoaudit.ai.schemas import ActivityCandidate


class AIClassifier(Protocol):
    """Protocol for AI activity classifiers.

    Any provider (Gemini, OpenAI, mock) must implement this interface.
    The pipeline depends only on this protocol, never on a concrete provider.
    """

    def classify_row(
        self,
        raw_row: dict[str, str],
        source_row: int | None = None,
    ) -> ActivityCandidate:
        """Classify a single raw data row into an ActivityCandidate.

        Args:
            raw_row: Dict of column_name -> value from the raw data.
            source_row: Optional row number for traceability.

        Returns:
            An ActivityCandidate with the AI's classification.
        """
        ...

    def classify_batch(
        self,
        raw_rows: list[dict[str, str]],
        start_row: int = 2,
    ) -> list[ActivityCandidate]:
        """Classify multiple raw data rows.

        Default implementation calls classify_row in a loop.
        Providers may override for batch-optimized API calls.

        Args:
            raw_rows: List of raw data row dicts.
            start_row: Row number offset for the first row.

        Returns:
            List of ActivityCandidates, one per input row.
        """
        ...
