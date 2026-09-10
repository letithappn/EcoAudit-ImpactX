import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import { ScenarioResultView } from "@/components/scenarios/scenario-result";
import { EvidencePanel } from "@/components/evidence/evidence-panel";
import { ScenarioDTO, EvidenceDTO } from "@/lib/types";

const mockScenario: ScenarioDTO = {
  name: "20% Natural Gas Electrification",
  description: "Heat pump substitution for low-temp processes",
  intervention_type: "PercentageReduction",
  target_activity_ids: ["act-1"],
  assumptions: ["Grid factor assumes 2024 regional baseline"],
  carbon_impact: {
    baseline_emissions: "100.0000",
    scenario_emissions: "80.0000",
    absolute_reduction: "20.0000",
    percentage_reduction: "20.00",
    emissions_unit: "tCO2e",
  },
  financial_impact: {
    baseline_cost: "50000.00",
    scenario_cost: "42000.00",
    absolute_savings: "8000.00",
    percentage_savings: "16.00",
    is_available: true,
    missing_reason: "",
  },
  baseline_result_ids: ["res-1"],
  scenario_evidence: [],
};

const mockEvidence: EvidenceDTO[] = [
  {
    result_id: "res-1",
    activity_id: "act-1",
    activity_description: "Natural gas combustion in boiler",
    original_row: { fuel: "Gas", kwh: "10000" },
    emissions_value: "18.5200",
    emissions_unit: "tCO2e",
    factor: {
      factor_id: "defra-gas-2024",
      source: "UK DEFRA",
      dataset: "Government GHG Conversion Factors",
      year: 2024,
      version: "1.0",
      methodology: "Direct fuel chemical stoichiometry",
      applicability_notes: "Commercial natural gas net CV",
      country: "UK",
      factor_value: "0.1852",
      factor_unit: "kg CO2e / kWh",
      is_proxy: false,
    },
    trace: {
      input_quantity: "10000.00",
      input_unit: "kWh",
      normalized_quantity: "10000.00",
      normalized_unit: "kWh",
      conversion_factor_applied: "1.0",
      emission_factor_value: "0.1852",
      emission_factor_unit: "kg CO2e / kWh",
      emission_factor_id: "defra-gas-2024",
      emission_factor_source: "UK DEFRA",
      emission_factor_year: 2024,
      formula_description: "quantity * emission_factor / 1000",
      scope: "Scope 1",
      category: "Stationary Combustion",
    },
    source_row: 4,
  },
];

describe("Scenarios and Evidence Components", () => {
  it("renders ScenarioResultView showing carbon reduction and financial savings", () => {
    render(<ScenarioResultView scenario={mockScenario} />);
    expect(screen.getByText("20% Natural Gas Electrification")).toBeInTheDocument();
    expect(screen.getByText("20.0000 tCO2e")).toBeInTheDocument();
    expect(screen.getByText("20.00%")).toBeInTheDocument();
    expect(screen.getByText("$8000.00")).toBeInTheDocument();
  });

  it("renders EvidencePanel displaying calculation trace and factor source", () => {
    render(<EvidencePanel evidence={mockEvidence} rejections={[]} />);
    expect(screen.getByText("Natural gas combustion in boiler")).toBeInTheDocument();
    expect(screen.getByText("UK DEFRA")).toBeInTheDocument();
    expect(screen.getByText("18.5200 tCO2e")).toBeInTheDocument();
  });
});
