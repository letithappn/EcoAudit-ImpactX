"""Real-world CSV robustness and partial-processing coverage."""

from pathlib import Path

from fastapi.testclient import TestClient

from api import main as api_main
from api.main import app
from ecoaudit.ai.mock_provider import MockClassifier
from ecoaudit.ai.pipeline import ClassificationPipeline
from ecoaudit.pipeline import execute_pipeline


def test_csv_normalization_handles_bom_aliases_order_and_duplicates(tmp_path: Path) -> None:
    path = tmp_path / "messy.csv"
    path.write_bytes(
        "UNIT,Qty,UTILITY,Date\n"
        "kWh,\"1,000\",Electricity,2024-01-01\n"
        "kWh,\"1,000\",Electricity,2024-01-01\n"
        ",,,\n".encode("utf-8-sig")
    )

    records, stats = ClassificationPipeline(MockClassifier()).process_csv(str(path))

    assert stats.total_rows == 2
    assert stats.successfully_parsed == 2
    assert stats.validated == 2
    assert len(records) == 2
    assert all(record.activity_data is not None for record in records)


def test_wide_dataset_produces_partial_results_without_guessing(tmp_path: Path) -> None:
    path = tmp_path / "wide.csv"
    path.write_text(
        "ID,Electricity Use (kBtu),Natural Gas Use (kBtu),District Steam Use (kBtu),Total GHG Emissions (Metric Tons CO2e)\n"
        "1,1000,2000,3000,12\n"
        "2,,,500,3\n",
        encoding="utf-8",
    )

    execution = execute_pipeline(path, provider="mock", year=2024, country="UK")
    stats = execution.statistics

    assert stats["total_rows"] == 2
    assert stats["calculated_rows"] == 1
    assert stats["coverage_percentage"] == 50.0
    assert stats["unsupported"] >= 2
    assert stats["calculated"] == 2
    assert execution.batch_result.total_emissions > 0


def test_upload_limit_is_configurable_and_clear(monkeypatch) -> None:
    monkeypatch.setattr(api_main, "MAX_UPLOAD_BYTES", 10)
    monkeypatch.setattr(api_main, "MAX_UPLOAD_MB", 1)
    response = TestClient(app).post(
        "/api/runs",
        files={"file": ("large.csv", b"a,b\n" + b"1,1234567890")},
    )

    assert response.status_code == 413
    assert "configured 1 MB" in response.json()["detail"]


def test_activity_endpoint_paginates_expanded_records() -> None:
    client = TestClient(app)
    path = Path("data/demo/small_test.csv")
    with path.open("rb") as source:
        created = client.post(
            "/api/runs",
            files={"file": (path.name, source, "text/csv")},
            params={"provider": "mock", "year": 2024, "country": "UK"},
        )
    run_id = created.json()["run_id"]
    for _ in range(100):
        status = client.get(f"/api/runs/{run_id}/status").json()
        if status["status"] in {"complete", "complete_with_review", "failed"}:
            break

    response = client.get(f"/api/runs/{run_id}/activities?offset=0&limit=1")
    payload = response.json()
    assert response.status_code == 200
    assert payload["total"] >= 1
    assert payload["limit"] == 1
    assert len(payload["activities"]) == 1


def test_large_chicago_dataset_is_a_real_integration_run() -> None:
    execution = execute_pipeline(
        "Chicago_Energy_Benchmarking_20260909.csv",
        provider="mock",
        year=2024,
        country="UK",
    )

    assert execution.statistics["total_rows"] == 28329
    assert execution.statistics["calculated_rows"] > 20000
    assert execution.statistics["coverage_percentage"] > 70
    assert execution.statistics["unsupported"] > 0
    assert execution.intelligence.hotspots
    assert execution.recommendations
