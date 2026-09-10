"use client";

import React from "react";
import { ContributionDTO } from "@/lib/types";
import { Layers, Zap, Truck, Factory } from "lucide-react";

interface ScopeBreakdownProps {
  scopeTotals: Record<string, string>;
  contributions: ContributionDTO[];
  emissionsUnit: string;
}

export function ScopeBreakdown({
  scopeTotals,
  contributions,
  emissionsUnit,
}: ScopeBreakdownProps) {
  // Scope 1: Direct emissions
  const scope1 = scopeTotals["Scope 1"] || "0";
  // Scope 2: Indirect electricity / steam
  const scope2 = scopeTotals["Scope 2"] || "0";
  // Scope 3: Value chain
  const scope3 = scopeTotals["Scope 3"] || "0";

  // Map contributions
  const contribMap = new Map<string, string>();
  contributions.forEach((c) => {
    contribMap.set(c.label, c.percentage);
  });

  const scope1Pct = contribMap.get("Scope 1") || "0";
  const scope2Pct = contribMap.get("Scope 2") || "0";
  const scope3Pct = contribMap.get("Scope 3") || "0";

  return (
    <div className="flex flex-col gap-4 font-mono text-xs">
      {/* Proportion Bar */}
      <div className="w-full h-4 bg-[#2B2B2B] rounded overflow-hidden border border-[#4A4A4A] flex">
        <div
          title={`Scope 1: ${scope1Pct}%`}
          className="h-full bg-[#EF5350] transition-all"
          style={{ width: `${Math.min(100, Math.max(0, parseFloat(scope1Pct)))}%` }}
        />
        <div
          title={`Scope 2: ${scope2Pct}%`}
          className="h-full bg-[#FFA726] transition-all"
          style={{ width: `${Math.min(100, Math.max(0, parseFloat(scope2Pct)))}%` }}
        />
        <div
          title={`Scope 3: ${scope3Pct}%`}
          className="h-full bg-[#42A5F5] transition-all"
          style={{ width: `${Math.min(100, Math.max(0, parseFloat(scope3Pct)))}%` }}
        />
      </div>

      {/* Scope Details Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Scope 1 Card */}
        <div className="p-3.5 rounded bg-[#2E2E2E] border border-[#4A4A4A] border-t-2 border-t-[#EF5350] flex flex-col">
          <div className="flex items-center justify-between text-[#9E9E9E] mb-1">
            <div className="flex items-center gap-1.5">
              <Factory className="w-3.5 h-3.5 text-[#EF5350]" />
              <span className="font-bold text-[#E0E0E0]">Scope 1</span>
            </div>
            <span className="text-xs font-semibold text-[#EF5350]">{scope1Pct}%</span>
          </div>
          <span className="text-[10px] text-[#757575]">Direct Fuel & Stationary Combustion</span>
          <div className="mt-2 text-base font-bold text-[#FFFFFF]">
            {scope1} <span className="text-[10px] font-normal text-[#9E9E9E]">{emissionsUnit}</span>
          </div>
        </div>

        {/* Scope 2 Card */}
        <div className="p-3.5 rounded bg-[#2E2E2E] border border-[#4A4A4A] border-t-2 border-t-[#FFA726] flex flex-col">
          <div className="flex items-center justify-between text-[#9E9E9E] mb-1">
            <div className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-[#FFA726]" />
              <span className="font-bold text-[#E0E0E0]">Scope 2</span>
            </div>
            <span className="text-xs font-semibold text-[#FFA726]">{scope2Pct}%</span>
          </div>
          <span className="text-[10px] text-[#757575]">Purchased Grid Electricity & Heating</span>
          <div className="mt-2 text-base font-bold text-[#FFFFFF]">
            {scope2} <span className="text-[10px] font-normal text-[#9E9E9E]">{emissionsUnit}</span>
          </div>
        </div>

        {/* Scope 3 Card */}
        <div className="p-3.5 rounded bg-[#2E2E2E] border border-[#4A4A4A] border-t-2 border-t-[#42A5F5] flex flex-col">
          <div className="flex items-center justify-between text-[#9E9E9E] mb-1">
            <div className="flex items-center gap-1.5">
              <Truck className="w-3.5 h-3.5 text-[#42A5F5]" />
              <span className="font-bold text-[#E0E0E0]">Scope 3</span>
            </div>
            <span className="text-xs font-semibold text-[#42A5F5]">{scope3Pct}%</span>
          </div>
          <span className="text-[10px] text-[#757575]">Upstream Logistics, Waste & Supply Chain</span>
          <div className="mt-2 text-base font-bold text-[#FFFFFF]">
            {scope3} <span className="text-[10px] font-normal text-[#9E9E9E]">{emissionsUnit}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
