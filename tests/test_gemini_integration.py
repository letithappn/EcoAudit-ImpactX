"""Integration tests for the Gemini provider (Mocked API)."""

import json
from unittest.mock import MagicMock, patch

import pytest
from ecoaudit.ai.gemini_provider import GeminiClassifier
from ecoaudit.ai.schemas import ActivityCandidate


@pytest.fixture
def mock_genai_client():
    with patch("google.genai.Client") as mock_client_cls:
        with patch("os.environ.get", return_value="dummy_key"):
            mock_client = MagicMock()
            mock_client_cls.return_value = mock_client
            yield mock_client


def test_classify_row_success(mock_genai_client):
    classifier = GeminiClassifier()
    
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "activity_type": "grid_electricity",
        "quantity": "500",
        "unit": "kWh",
        "scope": "Scope 2",
        "category": "Purchased Electricity",
        "description": "Grid power",
        "confidence": 0.95,
        "reasoning": "Test",
        "needs_review": False
    })
    mock_genai_client.models.generate_content.return_value = mock_response
    
    row = {"Utility": "Electric", "Usage": "500"}
    result = classifier.classify_row(row, source_row=2)
    
    assert isinstance(result, ActivityCandidate)
    assert result.activity_type == "grid_electricity"
    assert result.quantity == "500"
    assert result.scope == "Scope 2"


def test_classify_row_api_error_fallback(mock_genai_client):
    classifier = GeminiClassifier()
    
    # Simulate an API timeout or quota error
    mock_genai_client.models.generate_content.side_effect = Exception("API Timeout")
    
    row = {"Utility": "Electric", "Usage": "500"}
    result = classifier.classify_row(row, source_row=2)
    
    assert isinstance(result, ActivityCandidate)
    assert result.activity_type == "unknown"
    assert result.needs_review is True
    assert "API error: API Timeout" in result.reasoning


def test_classify_batch_success(mock_genai_client):
    classifier = GeminiClassifier()
    
    mock_response = MagicMock()
    json_list = [
        {
            "activity_type": "diesel",
            "quantity": "100",
            "unit": "litre",
            "scope": "Scope 1",
            "category": "Mobile Combustion",
            "description": "Diesel fuel",
            "confidence": 0.95,
            "reasoning": "Test",
            "needs_review": False
        },
        {
            "activity_type": "natural_gas",
            "quantity": "200",
            "unit": "m3",
            "scope": "Scope 1",
            "category": "Stationary Combustion",
            "description": "Gas",
            "confidence": 0.95,
            "reasoning": "Test",
            "needs_review": False
        }
    ]
    mock_response.text = json.dumps(json_list + json_list)
    mock_genai_client.models.generate_content.return_value = mock_response
    
    rows = [{"Utility": "Diesel", "Usage": "100"}, {"Utility": "Gas", "Usage": "200"}]
    # Needs to be > 3 to trigger batch logic
    rows = rows + rows
    
    results = classifier.classify_batch(rows, start_row=2)
    
    assert len(results) == 4
    assert results[0].activity_type == "diesel"
