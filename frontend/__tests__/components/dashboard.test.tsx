import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import { KpiCards } from "@/components/dashboard/kpi-cards";
import { HotspotTable } from "@/components/dashboard/hotspot-table";
import { RunSummaryResponse } from "@/lib/types";

const mockSummary: Partial<RunSummaryResponse> = {
  run_id: "test-run-123",
  total_emissions: "572.5000",
  emissions_unit: "tCO2e",
  scope_totals: {
    "Scope 1": "210.0000",
    "Scope 2": "362.5000",
    "Scope 3": "0.0000",
  },
  statistics: {
    coverage_percentage: 95.5,
    recommendations_supported: 3,
    total_rows: 33,
    calculated: 29,
  },
  data_quality: {
    total_results: 29,
    results_with_ai_classification: 29,
    results_needing_review: 2,
    average_ai_confidence: "0.94",
    min_ai_confidence: "0.82",
    results_with_test_factors: 0,
    factor_sources: ["UK DEFRA 2024"],
  },
  hotspots: [
    {
      label: "Heavy Fuel Oil Boiler #1",
      dimension: "Equipment",
      emissions: "185.2000",
      percentage_of_total: "32.35",
      percentage_of_scope: "88.19",
      severity: "critical",
      rank: 1,
      actionability: "high",
      contributing_activities: 4,
      result_ids: ["res-1", "res-2"],
      parent_scope: "Scope 1",
      parent_category: "Stationary Combustion",
    },
  ],
};

describe("Dashboard Components", () => {
  it("renders KpiCards with exact string values from backend", () => {
    render(<KpiCards summary={mockSummary as RunSummaryResponse} />);
    expect(screen.getByText("572.5000")).toBeInTheDocument();
    expect(screen.getByText("tCO2e")).toBeInTheDocument();
    expect(screen.getByText("95.5%")).toBeInTheDocument();
  });

  it("renders HotspotTable with ranked emission hotspots", () => {
    render(<HotspotTable hotspots={mockSummary.hotspots!} emissionsUnit="tCO2e" />);
    expect(screen.getByText("Heavy Fuel Oil Boiler #1")).toBeInTheDocument();
    expect(screen.getByText("185.2000 tCO2e")).toBeInTheDocument();
    expect(screen.getByText("32.35%")).toBeInTheDocument();
  });
});
