"""Integration tests for the run-oriented FastAPI adapter."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app


def _complete_run(client: TestClient, run_id: str) -> dict:
    for _ in range(100):
        response = client.get(f"/api/runs/{run_id}/status")
        assert response.status_code == 200
        status = response.json()
        if status["status"] in {"complete", "complete_with_review", "failed"}:
            return status
        time.sleep(0.01)
    raise AssertionError("run did not complete")


def _create_run(client: TestClient) -> str:
    path = Path("data/demo/small_test.csv")
    with path.open("rb") as source:
        response = client.post(
            "/api/runs",
            files={"file": (path.name, source, "text/csv")},
            params={"provider": "mock", "year": 2024, "country": "UK"},
        )
    assert response.status_code == 202
    return response.json()["run_id"]


def test_run_api_exposes_decimal_safe_summary_and_evidence() -> None:
    client = TestClient(app)
    run_id = _create_run(client)
    status = _complete_run(client, run_id)

    assert status["statistics"]["recommendations_supported"] >= 1

    summary = client.get(f"/api/runs/{run_id}/summary")
    assert summary.status_code == 200
    payload = summary.json()
    assert isinstance(payload["total_emissions"], str)
    assert isinstance(next(iter(payload["scope_totals"].values())), str)
    assert payload["hotspots"]

    activities = client.get(f"/api/runs/{run_id}/activities").json()["activities"]
    assert activities[0]["original_row"]
    assert activities[0]["activity_id"].startswith("AI-")
    assert "reasoning" in activities[0]

    evidence = client.get(f"/api/runs/{run_id}/evidence").json()["evidence"]
    assert evidence[0]["original_row"]
    assert evidence[0]["trace"]["formula_description"]
    assert isinstance(evidence[0]["factor"]["factor_value"], str)


def test_run_api_evaluates_scenario_in_backend() -> None:
    client = TestClient(app)
    run_id = _create_run(client)
    _complete_run(client, run_id)
    activities = client.get(f"/api/runs/{run_id}/activities").json()["activities"]
    activity_id = next(item["activity_id"] for item in activities if item["activity_id"])

    response = client.post(
        f"/api/runs/{run_id}/scenarios",
        json={
            "target_activity_ids": [activity_id],
            "intervention_type": "PercentageReduction",
            "reduction_percentage": "10",
        },
    )
    assert response.status_code == 200
    impact = response.json()["scenario"]["carbon_impact"]
    assert isinstance(impact["absolute_reduction"], str)
    assert impact["percentage_reduction"] == "10.0"


def test_run_api_rejects_non_csv_upload() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/runs",
        files={"file": ("data.xlsx", b"not a csv", "application/vnd.ms-excel")},
    )
    assert response.status_code == 415


def test_ai_status_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "configured" in data
    assert "provider" in data
    assert "model" in data
    assert "status" in data


def test_ai_config_endpoint() -> None:
    client = TestClient(app)
    # Rejects empty key
    res_bad = client.post("/api/ai/config", json={"api_key": ""})
    assert res_bad.status_code == 422

    # Sets key and model
    res_ok = client.post("/api/ai/config", json={"api_key": "test-key-12345", "model": "gemini-2.5-flash"})
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["success"] is True
    assert data["model"] == "gemini-2.5-flash"

    # Status reflects configuration
    status = client.get("/api/ai/status").json()
    assert status["configured"] is True
    assert status["model"] == "gemini-2.5-flash"


def test_ai_test_endpoint() -> None:
    client = TestClient(app)
    # Rejects empty key
    res_bad = client.post("/api/ai/test", json={"api_key": ""})
    assert res_bad.status_code == 422

    # Tests key and returns structured diagnostic
    res = client.post("/api/ai/test", json={"api_key": "invalid-dummy-key", "model": "gemini-2.5-flash"})
    assert res.status_code == 200
    data = res.json()
    assert "success" in data
    assert "message" in data
    assert data["model"] == "gemini-2.5-flash"

