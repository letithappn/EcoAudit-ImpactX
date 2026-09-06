"""
AI provider abstraction.

Defines the protocols that all AI providers must implement.
This allows swapping providers (Gemini, OpenAI, mock) without changing
the pipeline.
"""

from __future__ import annotations

from typing import Any, Protocol

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
        ...

    def classify_batch(
        self,
        raw_rows: list[dict[str, str]],
        start_row: int = 2,
    ) -> list[ActivityCandidate]:
        ...


class AIClient(Protocol):
    """Protocol for a generic AI client capable of structured and text generation."""
    
    def generate_structured(
        self,
        prompt: str,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Generate a structured JSON response from the given prompt.
        
        Args:
            prompt: The full prompt string including context and instructions.
            
        Returns:
            Parsed JSON object or list.
        """
        ...
        
    def generate_text(
        self,
        prompt: str,
    ) -> str:
        """Generate a raw text response from the given prompt.
        
        Args:
            prompt: The full prompt string.
            
        Returns:
            The raw text string.
        """
        ...
