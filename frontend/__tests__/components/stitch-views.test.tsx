import { describe, it, expect, vi } from "vitest";
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { StitchSidebar } from "@/components/stitch/stitch-sidebar";
import { StitchHeader } from "@/components/stitch/stitch-header";
import { ExecutiveOverviewView } from "@/components/stitch/views/executive-overview-view";
import { CarbonBalanceView } from "@/components/stitch/views/carbon-balance-view";
import { ScenarioSimulatorView } from "@/components/stitch/views/scenario-simulator-view";
import { StitchIngestionModal } from "@/components/stitch/stitch-ingestion-modal";

describe("Stitch Design System Components", () => {
  it("renders StitchSidebar and handles navigation clicks", () => {
    const handleSelect = vi.fn();
    render(
      <StitchSidebar
        activeView="executive-overview"
        onSelectView={handleSelect}
        isGeminiActive={true}
      />
    );

    expect(screen.getByText("EcoAudit")).toBeDefined();
    expect(screen.getByText("v3.4 Audited")).toBeDefined();

    const cbamButton = screen.getByText("CBAM & Product Footprints");
    fireEvent.click(cbamButton);
    expect(handleSelect).toHaveBeenCalledWith("cbam-and-product-footprints");
  });

  it("renders StitchHeader and triggers upload modal", () => {
    const handleUpload = vi.fn();
    render(
      <StitchHeader
        onOpenUpload={handleUpload}
        isGeminiActive={false}
      />
    );

    expect(screen.getByText("Dr. Aris Thorne")).toBeDefined();
    expect(screen.getByText("CBAM Readiness: 94.2% Audit Ready")).toBeDefined();

    const uploadButton = screen.getByText("+ New Ingestion / Audit Run");
    fireEvent.click(uploadButton);
    expect(handleUpload).toHaveBeenCalled();
  });

  it("renders ExecutiveOverviewView with high-density KPI cards", () => {
    render(
      <ExecutiveOverviewView
        summary={null}
        activities={[]}
      />
    );

    expect(screen.getByText("Executive Carbon & Financial Command")).toBeDefined();
    expect(screen.getByText("Total Gross GHG Footprint")).toBeDefined();
    expect(screen.getByText("Revenue Carbon Intensity")).toBeDefined();
    expect(screen.getByText("Carbon Pricing & Risk")).toBeDefined();
    expect(screen.getByText("Audit & Telemetry Integrity")).toBeDefined();
  });

  it("renders CarbonBalanceView with zero delta parity audit badge", () => {
    render(
      <CarbonBalanceView
        summary={null}
        activities={[]}
      />
    );

    expect(screen.getByText("Corporate Carbon Balance & Value-Stream Allocation")).toBeDefined();
    expect(screen.getByText("ZERO DELTA")).toBeDefined();
    expect(screen.getByText("100% Balanced")).toBeDefined();
  });

  it("renders ScenarioSimulatorView with interactive sliders", () => {
    render(
      <ScenarioSimulatorView
        summary={null}
        activities={[]}
        activeRunId={null}
      />
    );

    expect(screen.getByText("Decarbonization Scenario Simulator & Strategic Sandbox")).toBeDefined();
    expect(screen.getByText("Electrification & Fuel Switching")).toBeDefined();
    expect(screen.getByText("Renewable Energy Procurement (PPA)")).toBeDefined();
  });

  it("renders StitchIngestionModal with Option A sample datasets", () => {
    const handleClose = vi.fn();
    const handleCreated = vi.fn();

    render(
      <StitchIngestionModal
        isOpen={true}
        onClose={handleClose}
        onRunCreated={handleCreated}
      />
    );

    expect(screen.getByText("New Ingestion & Audit Run")).toBeDefined();
    expect(screen.getByText("Egypt Heavy Industry")).toBeDefined();
    expect(screen.getByText("Chicago Energy Benchmark")).toBeDefined();
    expect(screen.getByText("Drag and drop your activity CSV file here")).toBeDefined();
  });
});
