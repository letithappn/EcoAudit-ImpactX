"""
Data ingestion and adaptation layer.

This module provides the boundary between external real-world datasets
(e.g., public CSVs, corporate data dumps) and the internal ActivityData model.
"""

from collections.abc import Iterator
from typing import Protocol

from ecoaudit.carbon.models import ActivityData


class DatasetAdapter(Protocol):
    """Protocol for dataset adapters.
    
    A DatasetAdapter reads external data (like a CSV file) and deterministically
    normalizes it into a stream of ActivityData objects ready for calculation.
    """

    def normalize(self, filepath: str) -> Iterator[ActivityData]:
        """Normalize the external dataset into ActivityData records.

        Args:
            filepath: Path to the raw data file (e.g., CSV).

        Yields:
            ActivityData objects.
        """
        ...
