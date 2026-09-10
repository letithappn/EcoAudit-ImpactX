import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { SapHeader } from "@/components/sap/sap-header";
import { CorporateBalanceView } from "@/components/sap/views/corporate-balance-view";
import { ProcessInboundsView } from "@/components/sap/views/process-inbounds-view";
import { AnalyzeEsgDataView } from "@/components/sap/views/analyze-esg-data-view";
import { ProductEmissionsView } from "@/components/sap/views/product-emissions-view";
import { SacStoriesView } from "@/components/sap/views/sac-stories-view";
import { ScenarioSimulatorView } from "@/components/sap/views/scenario-simulator-view";

describe("SAP Fiori Enterprise Views & Components", () => {
  it("renders SapHeader with SAP logo and app dropdown", () => {
    const onSelectApp = vi.fn();
    const onTriggerDemo = vi.fn();
    render(
      <SapHeader
        activeApp="corporate-balance"
        onSelectApp={onSelectApp}
        onTriggerDemo={onTriggerDemo}
      />
    );

    expect(screen.getByText("SAP")).toBeInTheDocument();
    expect(screen.getByText("Corporate Balance")).toBeInTheDocument();
    expect(screen.getByText("Run Demo")).toBeInTheDocument();
  });

  it("renders CorporateBalanceView with Sankey diagram and CO2e balance table (Image 1)", () => {
    render(<CorporateBalanceView />);

    expect(screen.getByText("Corporate CO2e Balance")).toBeInTheDocument();
    expect(screen.getByText("Cocoa (C001/1010/SUP01)")).toBeInTheDocument();
    expect(screen.getByText("17.64000 Ton")).toBeInTheDocument();
  });

  it("renders ProcessInboundsView with inbounds table and supplier detail drawer (Image 2)", () => {
    render(<ProcessInboundsView />);

    expect(screen.getByText("Inbounds")).toBeInTheDocument();
    expect(screen.getByText("Frame Main (P123A)")).toBeInTheDocument();
    expect(screen.getByText("BikeTech")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Request Footprint/i })).toBeInTheDocument();
  });

  it("renders AnalyzeEsgDataView with period chips and 10 ESG KPI tiles (Image 3)", () => {
    render(<AnalyzeEsgDataView />);

    expect(screen.getByText("Environmental")).toBeInTheDocument();
    expect(screen.getByText("Gross GHG Emissions – Scope 1")).toBeInTheDocument();
    expect(screen.getByText("330.02K")).toBeInTheDocument();
    expect(screen.getByText("Carbon Credits")).toBeInTheDocument();
  });

  it("renders ProductEmissionsView and opens Download CBAM Reports modal (Image 4)", () => {
    render(<ProductEmissionsView />);

    expect(screen.getByText("Product Emissions")).toBeInTheDocument();
    expect(screen.getAllByText("Steel Sheets (PMV_PRD_02)")[0]).toBeInTheDocument();

    const openModalBtn = screen.getByRole("button", { name: /Download CBAM Reports/i });
    fireEvent.click(openModalBtn);

    expect(screen.getByText("Report Global Data Confirmation")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Download" })).toBeInTheDocument();
  });

  it("renders SacStoriesView with combined finance and GHG story cards (Image 5)", () => {
    render(<SacStoriesView />);

    expect(screen.getByText("Combined GHG and Finance KPIs")).toBeInTheDocument();
    expect(screen.getByText("Finance KPIs")).toBeInTheDocument();
    expect(screen.getByText("KPIs Related to All GHG Scopes")).toBeInTheDocument();
  });

  it("renders ScenarioSimulatorView with intervention sliders, waterfall, and MACC initiatives", () => {
    render(<ScenarioSimulatorView />);

    expect(screen.getByText("Decarbonization Scenario Simulator & Strategic Sandbox")).toBeInTheDocument();
    expect(screen.getByText("Electrification & Fuel Switching")).toBeInTheDocument();
    expect(screen.getByText("Renewable Energy Procurement (PPA)")).toBeInTheDocument();
    expect(screen.getByText("Scenario Abatement Breakdown (Waterfall Decomposition)")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Run Monte Carlo Risk/i })).toBeInTheDocument();
  });
});
