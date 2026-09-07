"""Tests for the unified backend pipeline script."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.run_pipeline import main


@pytest.fixture
def test_dataset_path(tmp_path: Path) -> Path:
    """Create a temporary CSV for testing."""
    csv_path = tmp_path / "test_data.csv"
    content = [
        "Date,Facility,Type,Amount,Unit",
        "2024-01-01,HQ,Power Bill,1000,kWh",
        "2024-01-02,HQ,Water,500,gallons",  # Should be rejected
    ]
    csv_path.write_text("\n".join(content), encoding="utf-8")
    return csv_path


def test_pipeline_mock_execution(test_dataset_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Test the pipeline runs successfully in mock mode."""
    test_args = [
        "run_pipeline.py",
        str(test_dataset_path),
        "--provider",
        "mock",
        "--year",
        "2024",
        "--country",
        "UK"
    ]
    
    with patch.object(sys, "argv", test_args):
        main()
        
    captured = capsys.readouterr()
    output = captured.out
    
    assert "Loaded 6 real factors." in output
    assert "Ingested 2 rows" in output
    assert "Classified & Validated: 1" in output
    assert "Rejected: 1" in output  # Water should be rejected
    assert "Total Carbon Footprint: 207.05 kgCO2e" in output


def test_pipeline_json_output(test_dataset_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Test the pipeline produces valid JSON when requested."""
    test_args = [
        "run_pipeline.py",
        str(test_dataset_path),
        "--provider",
        "mock",
        "--year",
        "2024",
        "--country",
        "UK",
        "--json"
    ]
    
    with patch.object(sys, "argv", test_args):
        main()
        
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify the output is valid JSON
    result = json.loads(output)
    
    assert "statistics" in result
    assert result["statistics"]["total_rows"] == 2
    assert result["statistics"]["validated"] == 1
    assert result["statistics"]["rejected_ai"] == 1
    
    assert "carbon_footprint" in result
    assert round(result["carbon_footprint"]["total_kgCO2e"], 2) == 207.05


def test_pipeline_missing_file(capsys: pytest.CaptureFixture) -> None:
    """Test the pipeline handles missing files gracefully."""
    test_args = [
        "run_pipeline.py",
        "nonexistent_file.csv",
        "--provider",
        "mock"
    ]
    
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
            
    assert exc_info.value.code == 1
