import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { IsaCard } from "@/components/ui/isa-card";
import { IsaBadge } from "@/components/ui/isa-badge";
import { IsaProgress } from "@/components/ui/isa-progress";
import { SboButton } from "@/components/ui/sbo-button";

describe("ISA-101 Design System Components", () => {
  describe("IsaCard", () => {
    it("renders children with neutral surface style by default", () => {
      render(<IsaCard title="Scope 1 Emissions"><div>Card content</div></IsaCard>);
      expect(screen.getByText("Scope 1 Emissions")).toBeInTheDocument();
      expect(screen.getByText("Card content")).toBeInTheDocument();
    });

    it("applies critical alarm indicator when severity is critical", () => {
      const { container } = render(
        <IsaCard title="Anomaly Detected" severity="critical">
          <div>Alert</div>
        </IsaCard>
      );
      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain("border-[#D32F2F]");
    });
  });

  describe("IsaBadge", () => {
    it("renders severity variant with correct styling", () => {
      render(<IsaBadge severity="critical">Critical Alarm</IsaBadge>);
      const badge = screen.getByText("Critical Alarm");
      expect(badge).toBeInTheDocument();
      expect(badge.className).toContain("text-[#D32F2F]");
    });
  });

  describe("IsaProgress", () => {
    it("renders progress percentage and stage name", () => {
      render(<IsaProgress stage="Carbon Calculation" progress={65} />);
      expect(screen.getByText("Carbon Calculation")).toBeInTheDocument();
      expect(screen.getByText("65%")).toBeInTheDocument();
    });
  });

  describe("SboButton (Select-Before-Operate)", () => {
    it("requires two clicks: first to 'Arm/Select', second to 'Operate/Confirm'", () => {
      const onConfirm = vi.fn();
      render(
        <SboButton onConfirm={onConfirm}>
          Execute Scenario
        </SboButton>
      );

      const button = screen.getByRole("button");
      expect(button).toHaveTextContent("Execute Scenario");

      // First click: Select/Arm
      fireEvent.click(button);
      expect(onConfirm).not.toHaveBeenCalled();
      expect(button).toHaveTextContent("Confirm Execute Scenario?");

      // Second click: Operate/Execute
      fireEvent.click(button);
      expect(onConfirm).toHaveBeenCalledTimes(1);
    });
  });
});
