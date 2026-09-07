"""
Google Gemini AI provider for activity classification.

Uses the google-genai SDK for structured JSON output.
This provider is activated only when a GEMINI_API_KEY is available.

The Gemini provider uses the same prompt templates as all other providers
(defined in prompts.py) and returns the same ActivityCandidate schema.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from ecoaudit.ai.prompts import build_batch_prompt, build_classification_prompt
from ecoaudit.ai.schemas import ActivityCandidate, parse_ai_response

logger = logging.getLogger(__name__)


class GeminiClassifier:
    """Gemini-based activity classifier.

    Requires the GEMINI_API_KEY environment variable to be set.

    Args:
        model_name: Gemini model to use. Default: "gemini-2.0-flash".
        temperature: Sampling temperature. Lower = more deterministic.
    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.1,
    ) -> None:
        self._model_name = model_name
        self._temperature = temperature
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazily initialize the Gemini client."""
        if self._client is None:
            try:
                from google import genai
            except ImportError:
                raise ImportError(
                    "google-genai package is not installed. "
                    "Install with: pip install google-genai"
                )

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise EnvironmentError(
                    "GEMINI_API_KEY environment variable is not set. "
                    "Set it with: export GEMINI_API_KEY='your-key-here'"
                )

            self._client = genai.Client(api_key=api_key)

        return self._client

    def classify_row(
        self,
        raw_row: dict[str, str],
        source_row: int | None = None,
    ) -> ActivityCandidate:
        """Classify a single raw data row using Gemini."""
        client = self._get_client()
        prompt = build_classification_prompt(raw_row)
        raw_input = " | ".join(f"{k}: {v}" for k, v in raw_row.items())

        try:
            response = client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config={
                    "temperature": self._temperature,
                    "response_mime_type": "application/json",
                },
            )

            response_text = response.text.strip()
            parsed = self._parse_json_response(response_text)
            parsed["source_row"] = source_row
            parsed["raw_input"] = raw_input

            return parse_ai_response(parsed)

        except Exception as e:
            logger.error("Gemini API call failed: %s", e)
            # Return a safe fallback — unknown with needs_review
            return ActivityCandidate(
                activity_type="unknown",
                quantity="0",
                unit="kWh",
                scope="Scope 1",
                category="Stationary Combustion",
                description="AI classification failed",
                confidence=0.0,
                reasoning=f"Gemini API error: {e}",
                needs_review=True,
                source_row=source_row,
                raw_input=raw_input,
            )

    def classify_batch(
        self,
        raw_rows: list[dict[str, str]],
        start_row: int = 2,
    ) -> list[ActivityCandidate]:
        """Classify multiple rows using Gemini batch prompt."""
        if not raw_rows:
            return []

        # For small batches, use individual calls for reliability
        if len(raw_rows) <= 3:
            return [
                self.classify_row(row, source_row=start_row + i)
                for i, row in enumerate(raw_rows)
            ]

        client = self._get_client()
        prompt = build_batch_prompt(raw_rows)

        try:
            response = client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config={
                    "temperature": self._temperature,
                    "response_mime_type": "application/json",
                },
            )

            response_text = response.text.strip()
            parsed_list = self._parse_json_array_response(response_text)

            results = []
            for i, parsed in enumerate(parsed_list):
                raw_input = " | ".join(
                    f"{k}: {v}" for k, v in raw_rows[i].items()
                ) if i < len(raw_rows) else ""

                parsed["source_row"] = start_row + i
                parsed["raw_input"] = raw_input

                try:
                    results.append(parse_ai_response(parsed))
                except ValueError as e:
                    logger.warning("Failed to parse row %d: %s", i, e)
                    results.append(ActivityCandidate(
                        activity_type="unknown",
                        quantity="0",
                        unit="kWh",
                        scope="Scope 1",
                        category="Stationary Combustion",
                        description="Failed to parse AI response",
                        confidence=0.0,
                        reasoning=f"Parse error: {e}",
                        needs_review=True,
                        source_row=start_row + i,
                        raw_input=raw_input,
                    ))

            return results

        except Exception as e:
            logger.error("Gemini batch API call failed: %s", e)
            # Fall back to individual classification
            return [
                self.classify_row(row, source_row=start_row + i)
                for i, row in enumerate(raw_rows)
            ]

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        """Parse JSON from Gemini response, handling markdown code blocks."""
        # Strip markdown code fences if present
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Gemini response is not valid JSON: {e}\nRaw response: {text[:500]}"
            ) from e

    def _parse_json_array_response(self, text: str) -> list[dict[str, Any]]:
        """Parse a JSON array from Gemini response."""
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Gemini response is not valid JSON array: {e}\nRaw response: {text[:500]}"
            ) from e


class GeminiClient:
    """Generic Gemini client for structured and text generation."""

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.2,
    ) -> None:
        self._model_name = model_name
        self._temperature = temperature
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from google import genai
            except ImportError:
                raise ImportError("google-genai package is not installed.")

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")

            self._client = genai.Client(api_key=api_key)

        return self._client

    def generate_structured(self, prompt: str) -> dict[str, Any] | list[dict[str, Any]]:
        client = self._get_client()
        try:
            response = client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config={
                    "temperature": self._temperature,
                    "response_mime_type": "application/json",
                },
            )
            text = response.text.strip()
            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text)
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)
            cleaned = cleaned.strip()
            return json.loads(cleaned)
        except Exception as e:
            logger.error("Gemini structured generation failed: %s", e)
            raise

    def generate_text(self, prompt: str) -> str:
        client = self._get_client()
        try:
            response = client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config={
                    "temperature": self._temperature,
                },
            )
            return response.text.strip()
        except Exception as e:
            logger.error("Gemini text generation failed: %s", e)
            raise

