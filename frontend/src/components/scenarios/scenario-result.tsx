"use client";

import React from "react";
import { ScenarioDTO } from "@/lib/types";
import { IsaCard } from "@/components/ui/isa-card";
import { IsaBadge } from "@/components/ui/isa-badge";
import { TrendingDown, DollarSign, Leaf, Layers, CheckCircle2 } from "lucide-react";

interface ScenarioResultViewProps {
  scenario: ScenarioDTO;
  className?: string;
}

export function ScenarioResultView({ scenario, className = "" }: ScenarioResultViewProps) {
  const { carbon_impact, financial_impact } = scenario;

  return (
    <IsaCard
      title={scenario.name}
      subtitle={scenario.description}
      severity="safe"
      className={className}
      actions={
        <IsaBadge severity="safe" size="sm">
          {scenario.intervention_type}
        </IsaBadge>
      }
    >
      <div className="flex flex-col gap-5 font-mono text-xs">
        {/* Metric Cards: Carbon Reduction & Financial Arbitrage */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Carbon Abatement Box */}
          <div className="p-4 rounded bg-[#2B2B2B] border border-[#43A047]/60 flex flex-col justify-between">
            <div className="flex items-center justify-between text-[#9E9E9E] mb-2">
              <div className="flex items-center gap-1.5">
                <Leaf className="w-4 h-4 text-[#43A047]" />
                <span className="font-bold text-[#E0E0E0] uppercase">Carbon Abatement</span>
              </div>
              <span className="text-xs font-bold text-[#43A047]">
                {carbon_impact.percentage_reduction}%
              </span>
            </div>

            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-[#43A047]">
                {carbon_impact.absolute_reduction} {carbon_impact.emissions_unit}
              </span>
              <span className="text-[10px] text-[#9E9E9E]">Abated</span>
            </div>

            <div className="flex items-center justify-between pt-3 mt-3 border-t border-[#383838] text-[11px] text-[#9E9E9E]">
              <span>Baseline: {carbon_impact.baseline_emissions}</span>
              <span>→</span>
              <span className="text-[#E0E0E0] font-semibold">
                Scenario: {carbon_impact.scenario_emissions} {carbon_impact.emissions_unit}
              </span>
            </div>
          </div>

          {/* Financial Savings Box */}
          <div className="p-4 rounded bg-[#2B2B2B] border border-[#00ACC1]/60 flex flex-col justify-between">
            <div className="flex items-center justify-between text-[#9E9E9E] mb-2">
              <div className="flex items-center gap-1.5">
                <DollarSign className="w-4 h-4 text-[#00ACC1]" />
                <span className="font-bold text-[#E0E0E0] uppercase">Financial Optimization</span>
              </div>
              {financial_impact.percentage_savings && (
                <span className="text-xs font-bold text-[#00ACC1]">
                  {financial_impact.percentage_savings}%
                </span>
              )}
            </div>

            <div className="flex items-baseline gap-2 mt-1">
              {financial_impact.is_available && financial_impact.absolute_savings ? (
                <span className="text-2xl font-bold text-[#00ACC1]">
                  ${financial_impact.absolute_savings}
                </span>
              ) : (
                <span className="text-base text-[#757575]">
                  {financial_impact.missing_reason || "Cost data not supplied"}
                </span>
              )}
              {financial_impact.is_available && (
                <span className="text-[10px] text-[#9E9E9E]">Net Annual Savings</span>
              )}
            </div>

            <div className="flex items-center justify-between pt-3 mt-3 border-t border-[#383838] text-[11px] text-[#9E9E9E]">
              <span>
                Baseline:{" "}
                {financial_impact.baseline_cost ? `$${financial_impact.baseline_cost}` : "—"}
              </span>
              <span>→</span>
              <span className="text-[#E0E0E0] font-semibold">
                Scenario:{" "}
                {financial_impact.scenario_cost ? `$${financial_impact.scenario_cost}` : "—"}
              </span>
            </div>
          </div>
        </div>

        {/* Assumptions & Target Scope Details */}
        <div className="p-3 bg-[#262626] rounded border border-[#383838] text-[11px]">
          <span className="text-[#9E9E9E] font-semibold uppercase block mb-1">
            Engine Assumptions & Targets:
          </span>
          <div className="flex flex-wrap gap-2">
            <span className="text-[#757575]">Targeted Activities:</span>
            <span className="text-[#E0E0E0] font-semibold">
              {scenario.target_activity_ids.length} records
            </span>
            {scenario.assumptions.map((assump, idx) => (
              <span key={idx} className="text-[#00ACC1]">
                • {assump}
              </span>
            ))}
          </div>
        </div>
      </div>
    </IsaCard>
  );
}
