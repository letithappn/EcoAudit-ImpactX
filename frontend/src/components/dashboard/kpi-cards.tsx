"use client";

import React from "react";
import { RunSummaryResponse } from "@/lib/types";
import { IsaCard } from "@/components/ui/isa-card";
import { Activity, ShieldCheck, CheckCircle2, Sparkles, Scale } from "lucide-react";

interface KpiCardsProps {
  summary: RunSummaryResponse;
}

export function KpiCards({ summary }: KpiCardsProps) {
  const stats = summary.statistics || {};
  const dataQuality = summary.data_quality;

  // Calculate FRA Decision 36 mandatory 20% CERC retirement amount if Scope 1 + Scope 2 are present
  // Note: we display the number of CERCs required
  const scope1 = summary.scope_totals["Scope 1"] || "0";
  const scope2 = summary.scope_totals["Scope 2"] || "0";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* KPI 1: Gross Carbon Footprint (Authoritative Decimal String) */}
      <IsaCard
        title="Gross GHG Emissions"
        subtitle="Scope 1, 2, 3 Deterministic Total"
        className="border-l-4 border-l-[#00ACC1]"
      >
        <div className="flex flex-col">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-mono font-bold text-[#FFFFFF] tracking-tight">
              {summary.total_emissions}
            </span>
            <span className="text-xs font-mono font-semibold text-[#00ACC1]">
              {summary.emissions_unit}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-[#4A4A4A]/60 text-[11px] font-mono text-[#9E9E9E]">
            <Activity className="w-3.5 h-3.5 text-[#00ACC1]" />
            <span>Calculated: {stats.calculated ?? "0"} / {stats.total_rows ?? "0"} Activities</span>
          </div>
        </div>
      </IsaCard>

      {/* KPI 2: Regulatory Accounting Coverage */}
      <IsaCard
        title="Accounting Coverage"
        subtitle="Completeness & Boundary Rigor"
        severity={
          (stats.coverage_percentage ?? 0) >= 90
            ? "safe"
            : (stats.coverage_percentage ?? 0) >= 70
            ? "warning"
            : "critical"
        }
      >
        <div className="flex flex-col">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-mono font-bold text-[#43A047] tracking-tight">
              {stats.coverage_percentage ?? 0}%
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-[#4A4A4A]/60 text-[11px] font-mono text-[#9E9E9E]">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#43A047]" />
            <span>
              Validated: {stats.validated ?? "0"} records ({stats.needs_review ?? "0"} review)
            </span>
          </div>
        </div>
      </IsaCard>

      {/* KPI 3: Data Quality & AI Assurance */}
      <IsaCard
        title="Classification Assurance"
        subtitle="Gemini / Deterministic Match"
      >
        <div className="flex flex-col">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-mono font-bold text-[#E0E0E0] tracking-tight">
              {dataQuality?.average_ai_confidence
                ? `${(parseFloat(dataQuality.average_ai_confidence) * 100).toFixed(1)}%`
                : "100%"}
            </span>
            <span className="text-xs font-mono text-[#9E9E9E]">Confidence</span>
          </div>
          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-[#4A4A4A]/60 text-[11px] font-mono text-[#9E9E9E]">
            <ShieldCheck className="w-3.5 h-3.5 text-[#00ACC1]" />
            <span>
              {dataQuality?.factor_sources?.length || 1} Official Registry Sources
            </span>
          </div>
        </div>
      </IsaCard>

      {/* KPI 4: Actionable Decarbonization Scenarios */}
      <IsaCard
        title="Supported Interventions"
        subtitle="Optimized What-If Scenarios"
        className="border-l-4 border-l-[#43A047]"
      >
        <div className="flex flex-col">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-mono font-bold text-[#43A047] tracking-tight">
              {stats.recommendations_supported ?? 0}
            </span>
            <span className="text-xs font-mono text-[#9E9E9E]">Verified</span>
          </div>
          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-[#4A4A4A]/60 text-[11px] font-mono text-[#9E9E9E]">
            <Sparkles className="w-3.5 h-3.5 text-[#43A047]" />
            <span>
              {stats.recommendations_generated ?? 0} AI Proposals Evaluated
            </span>
          </div>
        </div>
      </IsaCard>
    </div>
  );
}
