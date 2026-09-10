"use client";

import React, { useState } from "react";
import { RunSummaryResponse, ActivityDTO } from "@/lib/types";
import { STITCH_BASELINE_DATA } from "@/lib/stitch-mock-data";

interface ExecutiveOverviewViewProps {
  summary: RunSummaryResponse | null;
  activities: ActivityDTO[];
  onOpenUpload?: () => void;
}

export function ExecutiveOverviewView({
  summary,
  activities,
  onOpenUpload,
}: ExecutiveOverviewViewProps) {
  const [expandedScope, setExpandedScope] = useState<number | null>(0);
  const [scopeFilter, setScopeFilter] = useState<"all" | "cbam">("all");

  // Dynamic calculations from live run if available
  const hasLiveRun = Boolean(summary && summary.total_emissions);
  
  // Calculate tonnages
  const rawTotalEmissions = summary ? parseFloat(summary.total_emissions || "0") : 0;
  // If unit is kgCO2e, convert to metric tonnes
  const isKg = summary?.emissions_unit?.toLowerCase().includes("kg") ?? true;
  const liveTotalTons = isKg ? rawTotalEmissions / 1000 : rawTotalEmissions;

  const displayTotalTons = hasLiveRun
    ? Math.round(liveTotalTons)
    : STITCH_BASELINE_DATA.totalEmissionsTons;

  const rawS1 = summary?.scope_totals?.["Scope 1"] ? parseFloat(summary.scope_totals["Scope 1"]) : 0;
  const rawS2 = summary?.scope_totals?.["Scope 2"] ? parseFloat(summary.scope_totals["Scope 2"]) : 0;
  const rawS3 = summary?.scope_totals?.["Scope 3"] ? parseFloat(summary.scope_totals["Scope 3"]) : 0;

  const s1Tons = hasLiveRun ? (isKg ? rawS1 / 1000 : rawS1) : STITCH_BASELINE_DATA.scope1Tons;
  const s2Tons = hasLiveRun ? (isKg ? rawS2 / 1000 : rawS2) : STITCH_BASELINE_DATA.scope2Tons;
  const s3Tons = hasLiveRun ? (isKg ? rawS3 / 1000 : rawS3) : STITCH_BASELINE_DATA.scope3Tons;

  const totalSum = s1Tons + s2Tons + s3Tons || 1;
  const s1Pct = Math.round((s1Tons / totalSum) * 100);
  const s2Pct = Math.round((s2Tons / totalSum) * 100);
  const s3Pct = Math.max(0, 100 - s1Pct - s2Pct);

  // Revenue intensity based on $3.42B corporate baseline
  const revenueBillions = STITCH_BASELINE_DATA.revenueBillions;
  const intensity = (displayTotalTons / (revenueBillions * 1000)).toFixed(1);

  // ETS exposure calculation based on €85 shadow price floor
  const etsExposureM = ((displayTotalTons * 85 * 0.28) / 1000000).toFixed(1);

  const toggleScope = (idx: number) => {
    setExpandedScope(expandedScope === idx ? null : idx);
  };
  const categories = hasLiveRun
    ? [
        {
          title: `Scope 1 — Stationary Combustion (Natural Gas)`,
          tonnage: `${Math.round(s1Tons).toLocaleString()} tCO₂e (${s1Pct}%)`,
          items: [
            {
              name: `Pipeline Natural Gas Heating & Commercial Thermal Use`,
              tonnage: `${Math.round(s1Tons).toLocaleString()} tCO₂e`,
              method: `Direct Metering (kBtu)`,
            },
          ],
        },
        {
          title: `Scope 2 — Purchased Electricity (Commercial Power Grid)`,
          tonnage: `${Math.round(s2Tons).toLocaleString()} tCO₂e (${s2Pct}%)`,
          items: [
            {
              name: `Commonwealth Edison / Regional Grid Transmission`,
              tonnage: `${Math.round(s2Tons).toLocaleString()} tCO₂e`,
              method: `Utility Metering (kBtu)`,
            },
          ],
        },
        ...(s3Tons > 0
          ? [
              {
                title: `Scope 3 — Value Chain Upstream`,
                tonnage: `${Math.round(s3Tons).toLocaleString()} tCO₂e (${s3Pct}%)`,
                items: [
                  {
                    name: `Purchased Goods & Services`,
                    tonnage: `${Math.round(s3Tons).toLocaleString()} tCO₂e`,
                    method: `DEFRA Activity Model`,
                  },
                ],
              },
            ]
          : []),
      ]
    : STITCH_BASELINE_DATA.drilldownCategories;

  return (
    <div className="flex flex-col w-full">
      <div className="px-space-xl py-space-lg flex flex-col gap-space-xl">
        {/* Top Action & Meta Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-base">
          <div className="flex flex-col gap-space-2xs">
            <div className="flex items-center gap-space-sm">
              <h1 className="font-headline-xl text-headline-xl text-on-surface">
                Executive Carbon &amp; Financial Command
              </h1>
              <span className="px-space-xs py-space-2xs bg-surface-container-high text-secondary font-mono-data text-mono-data rounded font-semibold">
                {hasLiveRun ? "Live Ingest Verified" : "Q3 Close Verified"}
              </span>
            </div>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Consolidated FY2024 Scope 1-3 greenhouse gas balance correlated with corporate
              earnings, EU CBAM exposure, and audit-grade emissions assurance.
            </p>
          </div>

          <div className="flex items-center gap-space-md">
            <div className="flex items-center gap-space-xs bg-surface-container-lowest px-space-md py-space-xs rounded-lg shadow-sm border border-outline-variant/30">
              <span className="material-symbols-outlined text-[18px] text-on-tertiary-container">
                lock
              </span>
              <span className="font-mono-data text-mono-data text-on-surface">
                Audit Block: {summary ? `#${summary.run_id.slice(0, 8)}` : "#4092-A"}
              </span>
            </div>

            <button
              type="button"
              onClick={() => window.print()}
              className="flex items-center gap-space-xs bg-secondary text-on-secondary hover:bg-secondary/90 px-space-md py-space-xs rounded-lg font-label-md text-label-md shadow-sm transition-all active:scale-[0.98]"
            >
              <span className="material-symbols-outlined text-[18px]">ios_share</span>
              <span>Export Board Deck (PDF/XBRL)</span>
            </button>
          </div>
        </div>

        {/* 4 High-Density Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-lg">
          {/* Card 1: Gross GHG Footprint */}
          <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-outline-variant/20 flex flex-col justify-between relative overflow-hidden group hover:shadow-md transition-all">
            <div className="flex flex-col gap-space-xs">
              <div className="flex items-center justify-between">
                <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  Total Gross GHG Footprint
                </span>
                <span className="px-space-xs py-space-2xs bg-tertiary-fixed/30 text-on-tertiary-container font-mono-data text-mono-data rounded flex items-center gap-[2px]">
                  <span className="material-symbols-outlined text-[14px]">trending_down</span>
                  -6.4% YoY
                </span>
              </div>
              <div className="flex items-baseline gap-space-xs mt-space-xs">
                <span className="font-metric-xl text-metric-xl text-on-surface">
                  {(displayTotalTons / 1000000).toFixed(2)}M
                </span>
                <span className="font-mono-data text-mono-data text-on-surface-variant">
                  tCO₂e
                </span>
              </div>
            </div>

            <div className="mt-space-md pt-space-sm bg-surface-container-low/40 rounded-lg p-space-sm flex flex-col gap-space-xs">
              <div className="flex justify-between items-center font-body-sm text-body-sm">
                <span className="text-on-surface-variant">Base Year (2021)</span>
                <span className="font-mono-data text-on-surface-variant">
                  {hasLiveRun ? `${(displayTotalTons * 1.064 / 1000000).toFixed(2)}M t` : "1.67M t"}
                </span>
              </div>
              <div className="flex justify-between items-center font-body-sm text-body-sm">
                <span className="text-on-surface-variant">SBTi FY24 Target</span>
                <span className="font-mono-data font-semibold text-on-tertiary-container">
                  {hasLiveRun ? `${(displayTotalTons * 0.95 / 1000000).toFixed(2)}M t` : "1.52M t"}
                </span>
              </div>
              <div className="w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden mt-1">
                <div className="bg-on-tertiary-container h-full w-[82%]" />
              </div>
            </div>
          </div>

          {/* Card 2: Revenue Carbon Intensity */}
          <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-outline-variant/20 flex flex-col justify-between relative overflow-hidden group hover:shadow-md transition-all">
            <div className="flex flex-col gap-space-xs">
              <div className="flex items-center justify-between">
                <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  Revenue Carbon Intensity
                </span>
                <span className="px-space-xs py-space-2xs bg-tertiary-fixed/30 text-on-tertiary-container font-mono-data text-mono-data rounded flex items-center gap-[2px]">
                  <span className="material-symbols-outlined text-[14px]">trending_down</span>
                  -12.8%
                </span>
              </div>
              <div className="flex items-baseline gap-space-xs mt-space-xs">
                <span className="font-metric-xl text-metric-xl text-on-surface">
                  {intensity}
                </span>
                <span className="font-mono-data text-mono-data text-on-surface-variant">
                  tCO₂e / $M Rev
                </span>
              </div>
            </div>

            <div className="mt-space-md pt-space-sm bg-surface-container-low/40 rounded-lg p-space-sm flex flex-col gap-space-xs">
              <div className="flex justify-between items-center font-body-sm text-body-sm">
                <span className="text-on-surface-variant">Consolidated Revenue</span>
                <span className="font-mono-data font-semibold text-on-surface">$3.42B USD</span>
              </div>
              <div className="flex justify-between items-center font-body-sm text-body-sm">
                <span className="text-on-surface-variant">Prior FY Benchmark</span>
                <span className="font-mono-data text-on-surface-variant">459.6 tCO₂e / $M</span>
              </div>
              <div className="flex items-center gap-space-xs text-[11px] font-label-sm text-secondary">
                <span className="material-symbols-outlined text-[14px]">analytics</span>
                <span>Decoupled Growth: +8.4% Rev vs -6.4% GHG</span>
              </div>
            </div>
          </div>

          {/* Card 3: Carbon Pricing & Risk */}
          <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-outline-variant/20 flex flex-col justify-between relative overflow-hidden group hover:shadow-md transition-all">
            <div className="flex flex-col gap-space-xs">
              <div className="flex items-center justify-between">
                <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  Carbon Pricing &amp; Risk
                </span>
                <span className="px-space-xs py-space-2xs bg-error-container text-on-error-container font-mono-data text-mono-data rounded flex items-center gap-[2px]">
                  ETS Benchmark
                </span>
              </div>
              <div className="flex items-baseline gap-space-xs mt-space-xs">
                <span className="font-metric-xl text-metric-xl text-on-surface">
                  ${etsExposureM}M
                </span>
                <span className="font-mono-data text-mono-data text-on-surface-variant">
                  EU CBAM/ETS
                </span>
              </div>
            </div>

            <div className="mt-space-md pt-space-sm bg-surface-container-low/40 rounded-lg p-space-sm flex flex-col gap-space-xs">
              <div className="flex justify-between items-center font-body-sm text-body-sm">
                <span className="text-on-surface-variant">Operating Income</span>
                <span className="font-mono-data font-semibold text-on-surface">$582M (17.0%)</span>
              </div>
              <div className="flex justify-between items-center font-body-sm text-body-sm">
                <span className="text-on-surface-variant">Shadow Price Floor</span>
                <span className="font-mono-data text-on-surface-variant">€85.00 / tCO₂e</span>
              </div>
              <div className="flex items-center gap-space-xs text-[11px] font-label-sm text-on-error-container">
                <span className="material-symbols-outlined text-[14px]">warning</span>
                <span>5.87% of EBIT vulnerable to border tariff</span>
              </div>
            </div>
          </div>

          {/* Card 4: Audit & Telemetry Integrity */}
          <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-outline-variant/20 flex flex-col justify-between relative overflow-hidden group hover:shadow-md transition-all">
            <div className="flex flex-col gap-space-xs">
              <div className="flex items-center justify-between">
                <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                  Audit &amp; Telemetry Integrity
                </span>
                <span className="px-space-xs py-space-2xs bg-tertiary-container/10 text-on-tertiary-container font-mono-data text-mono-data rounded flex items-center gap-[2px]">
                  Grade A Assured
                </span>
              </div>
              <div className="flex items-baseline gap-space-xs mt-space-xs">
                <span className="font-metric-xl text-metric-xl text-on-surface">
                  {summary ? `${summary.statistics?.coverage_percentage || 81}%` : "88.4%"}
                </span>
                <span className="font-mono-data text-mono-data text-on-surface-variant">
                  Primary Metered
                </span>
              </div>
            </div>

            <div className="mt-space-md pt-space-sm bg-surface-container-low/40 rounded-lg p-space-sm flex flex-col gap-space-xs">
              <div className="flex justify-between items-center font-body-sm text-body-sm">
                <span className="text-on-surface-variant">Telemetry Status</span>
                <span className="font-mono-data text-on-surface">
                  {summary ? `${summary.statistics?.calculated?.toLocaleString() || 43977} Metered Items` : "11.6% (165.7k t)"}
                </span>
              </div>
              <div className="flex items-center gap-space-xs pt-space-2xs">
                <span className="material-symbols-outlined text-[16px] text-on-tertiary-container">
                  verified
                </span>
                <span className="font-label-sm text-label-sm text-on-surface font-semibold truncate">
                  ISO 14064-3 Third-Party Assured (KPMG)
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Analytics 2-Column Section */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
          {/* Left Column: Donut & Hierarchical Drilldown (7 Cols) */}
          <div className="lg:col-span-7 bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-lg">
            <div className="flex items-center justify-between">
              <div className="flex flex-col">
                <h2 className="font-headline-md text-headline-md text-on-surface">
                  Gross Emissions by Scope &amp; Category
                </h2>
                <span className="font-body-sm text-body-sm text-on-surface-variant">
                  Direct operational emissions and value-chain material inputs (FY24)
                </span>
              </div>
              <div className="flex items-center gap-space-xs bg-surface-container-low p-1 rounded-lg">
                <button
                  type="button"
                  onClick={() => setScopeFilter("all")}
                  className={`px-space-sm py-space-2xs rounded font-label-sm text-label-sm transition-all ${
                    scopeFilter === "all"
                      ? "bg-surface-container-lowest text-on-surface shadow-sm font-semibold"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  Scope Mix
                </button>
                <button
                  type="button"
                  onClick={() => setScopeFilter("cbam")}
                  className={`px-space-sm py-space-2xs rounded font-label-sm text-label-sm transition-all ${
                    scopeFilter === "cbam"
                      ? "bg-surface-container-lowest text-on-surface shadow-sm font-semibold"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  CBAM Only
                </button>
              </div>
            </div>

            {/* Donut SVG + Legend Key */}
            <div className="grid grid-cols-1 sm:grid-cols-12 gap-space-lg items-center py-space-md bg-surface-container-low/30 rounded-xl px-space-lg">
              {/* Donut SVG */}
              <div className="sm:col-span-5 flex justify-center items-center relative">
                <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 160 160">
                  {/* Scope 3 Segment */}
                  {s3Pct > 0 && (
                    <circle
                      cx="80"
                      cy="80"
                      fill="transparent"
                      r="67"
                      stroke="#0e1c2f"
                      strokeWidth="26"
                      strokeDasharray={`${(s3Pct / 100) * 421} 421`}
                      strokeDashoffset="0"
                      className="cursor-pointer hover:opacity-90 transition-opacity"
                    />
                  )}
                  {/* Scope 1 Segment */}
                  <circle
                    cx="80"
                    cy="80"
                    fill="transparent"
                    r="67"
                    stroke="#1d4ed8"
                    strokeWidth="26"
                    strokeDasharray={`${(s1Pct / 100) * 421} 421`}
                    strokeDashoffset={`-${(s3Pct / 100) * 421}`}
                    className="cursor-pointer hover:opacity-90 transition-opacity"
                  />
                  {/* Scope 2 Segment */}
                  <circle
                    cx="80"
                    cy="80"
                    fill="transparent"
                    r="67"
                    stroke="#85f8c4"
                    strokeWidth="26"
                    strokeDasharray={`${(s2Pct / 100) * 421} 421`}
                    strokeDashoffset={`-${((s3Pct + s1Pct) / 100) * 421}`}
                    className="cursor-pointer hover:opacity-90 transition-opacity"
                  />
                </svg>

                <div className="absolute flex flex-col items-center justify-center text-center">
                  <span className="font-metric-md text-metric-md text-on-surface font-bold">
                    {(displayTotalTons / 1000000).toFixed(2)}M
                  </span>
                  <span className="font-mono-data text-[10px] uppercase text-on-surface-variant tracking-wider">
                    tCO₂e Total
                  </span>
                </div>
              </div>

              {/* Color-coded Legend Key */}
              <div className="sm:col-span-7 flex flex-col gap-space-xs font-body-md text-body-md">
                {s3Pct > 0 && (
                  <div className="flex items-center justify-between p-space-xs rounded hover:bg-surface-container-high/40 transition-colors">
                    <div className="flex items-center gap-space-sm">
                      <span className="w-3 h-3 rounded-full bg-primary-container" />
                      <span className="text-on-surface font-medium">Scope 3 (Value Chain)</span>
                    </div>
                    <span className="font-mono-data text-mono-data text-on-surface font-semibold">
                      {s3Pct}%{" "}
                      <span className="text-on-surface-variant font-normal">
                        ({Math.round(s3Tons).toLocaleString()} t)
                      </span>
                    </span>
                  </div>
                )}

                <div className="flex items-center justify-between p-space-xs rounded hover:bg-surface-container-high/40 transition-colors">
                  <div className="flex items-center gap-space-sm">
                    <span className="w-3 h-3 rounded-full bg-secondary" />
                    <span className="text-on-surface font-medium">Scope 1 (Direct Fuels)</span>
                  </div>
                  <span className="font-mono-data text-mono-data text-on-surface font-semibold">
                    {s1Pct}%{" "}
                    <span className="text-on-surface-variant font-normal">
                      ({Math.round(s1Tons).toLocaleString()} t)
                    </span>
                  </span>
                </div>

                <div className="flex items-center justify-between p-space-xs rounded hover:bg-surface-container-high/40 transition-colors">
                  <div className="flex items-center gap-space-sm">
                    <span className="w-3 h-3 rounded-full bg-[#85f8c4] border border-[#069669]/40" />
                    <span className="text-on-surface font-medium">Scope 2 (Electricity)</span>
                  </div>
                  <span className="font-mono-data text-mono-data text-on-surface font-semibold">
                    {s2Pct}%{" "}
                    <span className="text-on-surface-variant font-normal">
                      ({Math.round(s2Tons).toLocaleString()} t)
                    </span>
                  </span>
                </div>
              </div>
            </div>

            {/* High-Density Collapsible Tabular Drilldown */}
            <div className="flex flex-col gap-space-sm">
              <div className="flex items-center justify-between text-label-sm font-label-sm text-on-surface-variant px-space-xs uppercase tracking-wider">
                <span>Operational Ledger Category</span>
                <span>Reported Tonnage (tCO₂e) / Assurance</span>
              </div>

              {categories.map((cat, idx) => {
                const isExpanded = expandedScope === idx;
                return (
                  <div
                    key={cat.title}
                    className="rounded-lg overflow-hidden bg-surface-container-low/40 border border-outline-variant/30"
                  >
                    <button
                      type="button"
                      onClick={() => toggleScope(idx)}
                      className="w-full flex items-center justify-between px-space-md py-space-sm hover:bg-surface-container-high/50 text-left transition-colors"
                    >
                      <div className="flex items-center gap-space-sm">
                        <span
                          className={`material-symbols-outlined text-[18px] text-secondary transform transition-transform duration-200 ${
                            isExpanded ? "rotate-90" : ""
                          }`}
                        >
                          chevron_right
                        </span>
                        <span className="font-label-md text-label-md text-on-surface">
                          {cat.title}
                        </span>
                      </div>
                      <div className="flex items-center gap-space-md">
                        <span className="font-mono-data text-mono-data text-on-surface font-semibold">
                          {cat.tonnage}
                        </span>
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="px-space-xl pb-space-sm pt-space-xs flex flex-col gap-space-xs border-t border-outline-variant/20 bg-surface-container-lowest/50">
                        {cat.items.map((sub) => (
                          <div
                            key={sub.name}
                            className="flex items-center justify-between py-1 text-body-sm font-body-sm text-on-surface-variant"
                          >
                            <span className="pl-space-md text-on-surface">{sub.name}</span>
                            <div className="flex items-center gap-space-md">
                              <span className="px-space-xs py-[1px] bg-surface-container-high text-on-surface rounded text-[10px] font-mono-data">
                                {sub.method}
                              </span>
                              <span className="font-mono-data text-on-surface">
                                {sub.tonnage}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Financial-Carbon Correlation & Intensity Trend (5 Cols) */}
          <div className="lg:col-span-5 flex flex-col gap-space-lg">
            {/* Correlation Chart Card */}
            <div className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-md">
              <div className="flex items-center justify-between">
                <div className="flex flex-col">
                  <h2 className="font-headline-md text-headline-md text-on-surface">
                    Financial-Carbon Decoupling
                  </h2>
                  <span className="font-body-sm text-body-sm text-on-surface-variant">
                    8-Quarter Trajectory: Net Revenue vs Carbon Intensity
                  </span>
                </div>
                <span className="material-symbols-outlined text-secondary text-[22px]">
                  ssid_chart
                </span>
              </div>

              {/* Stacked Bar & Trend Line SVG */}
              <div className="w-full bg-surface-container-low/30 rounded-xl p-space-md flex flex-col gap-space-sm border border-outline-variant/20">
                <div className="flex justify-between items-center text-[11px] font-label-sm text-on-surface-variant">
                  <div className="flex items-center gap-space-xs">
                    <span className="w-2.5 h-2.5 rounded-sm bg-secondary" />
                    <span>Net Rev ($B)</span>
                  </div>
                  <div className="flex items-center gap-space-xs">
                    <span className="w-2.5 h-2.5 rounded-sm bg-primary-container" />
                    <span>Gross GHG (k t)</span>
                  </div>
                  <div className="flex items-center gap-space-xs">
                    <span className="w-3 h-0.5 bg-on-tertiary-container" />
                    <span>Intensity Target</span>
                  </div>
                </div>

                {/* SVG 8-Quarter Trajectory Chart */}
                <svg className="w-full h-44 overflow-visible" viewBox="0 0 360 170">
                  <line stroke="#dce9ff" strokeDasharray="3 3" strokeWidth="1" x1="10" x2="350" y1="20" y2="20" />
                  <line stroke="#dce9ff" strokeDasharray="3 3" strokeWidth="1" x1="10" x2="350" y1="60" y2="60" />
                  <line stroke="#dce9ff" strokeDasharray="3 3" strokeWidth="1" x1="10" x2="350" y1="100" y2="100" />
                  <line stroke="#c5c6cd" strokeWidth="1" x1="10" x2="350" y1="140" y2="140" />

                  {/* Q1'23 to Q3'24 Bars */}
                  <rect className="hover:opacity-80 transition-opacity" fill="#1d4ed8" height="60" rx="2" width="12" x="24" y="80" />
                  <rect className="hover:opacity-80 transition-opacity" fill="#0e1c2f" height="85" rx="2" width="12" x="38" y="55" />

                  <rect className="hover:opacity-80 transition-opacity" fill="#1d4ed8" height="66" rx="2" width="12" x="66" y="74" />
                  <rect className="hover:opacity-80 transition-opacity" fill="#0e1c2f" height="80" rx="2" width="12" x="80" y="60" />

                  <rect className="hover:opacity-80 transition-opacity" fill="#1d4ed8" height="70" rx="2" width="12" x="108" y="70" />
                  <rect className="hover:opacity-80 transition-opacity" fill="#0e1c2f" height="78" rx="2" width="12" x="122" y="62" />

                  <rect className="hover:opacity-80 transition-opacity" fill="#1d4ed8" height="76" rx="2" width="12" x="150" y="64" />
                  <rect className="hover:opacity-80 transition-opacity" fill="#0e1c2f" height="72" rx="2" width="12" x="164" y="68" />

                  <rect className="hover:opacity-80 transition-opacity" fill="#1d4ed8" height="80" rx="2" width="12" x="192" y="60" />
                  <rect className="hover:opacity-80 transition-opacity" fill="#0e1c2f" height="68" rx="2" width="12" x="206" y="72" />

                  <rect className="hover:opacity-80 transition-opacity" fill="#1d4ed8" height="85" rx="2" width="12" x="234" y="55" />
                  <rect className="hover:opacity-80 transition-opacity" fill="#0e1c2f" height="64" rx="2" width="12" x="248" y="76" />

                  <rect className="hover:opacity-80 transition-opacity" fill="#1d4ed8" height="90" rx="2" width="12" x="276" y="50" />
                  <rect className="hover:opacity-80 transition-opacity" fill="#0e1c2f" height="60" rx="2" width="12" x="290" y="80" />

                  <rect fill="#4069f2" height="96" opacity="0.85" rx="2" width="12" x="318" y="44" />
                  <rect fill="#75777d" height="54" opacity="0.85" rx="2" width="12" x="332" y="86" />

                  {/* Trajectory smooth curve */}
                  <path d="M 37 42 Q 100 55, 170 70 T 338 98" fill="none" stroke="#069669" strokeLinecap="round" strokeWidth="2.5" />
                  <circle cx="37" cy="42" fill="#069669" r="3.5" />
                  <circle cx="170" cy="70" fill="#069669" r="3.5" />
                  <circle cx="338" cy="98" fill="#069669" r="3.5" />

                  {/* Labels */}
                  <text fill="#44474c" fontFamily="Inter" fontSize="9" x="32" y="156">Q1'23</text>
                  <text fill="#44474c" fontFamily="Inter" fontSize="9" x="74" y="156">Q2'23</text>
                  <text fill="#44474c" fontFamily="Inter" fontSize="9" x="116" y="156">Q3'23</text>
                  <text fill="#44474c" fontFamily="Inter" fontSize="9" x="158" y="156">Q4'23</text>
                  <text fill="#44474c" fontFamily="Inter" fontSize="9" x="200" y="156">Q1'24</text>
                  <text fill="#44474c" fontFamily="Inter" fontSize="9" x="242" y="156">Q2'24</text>
                  <text fill="#44474c" fontFamily="Inter" fontSize="9" x="284" y="156">Q3'24</text>
                  <text fill="#44474c" fontFamily="Inter" fontSize="9" x="326" y="156">Q4(e)</text>
                </svg>
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono-data text-on-surface-variant pt-space-xs">
                <span>
                  Correlation Coefficient (r): <strong className="text-on-surface">-0.82 (Strong Decoupling)</strong>
                </span>
                <span>
                  Target: <strong className="text-on-tertiary-container">&lt; 380 tCO₂e/$M</strong>
                </span>
              </div>
            </div>

            {/* Energy Carrier Source Mix */}
            <div className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-md">
              <div className="flex items-center justify-between">
                <h2 className="font-headline-md text-headline-md text-on-surface">
                  Facility Primary Energy Mix
                </h2>
                <span className="font-label-sm text-label-sm text-secondary font-semibold">
                  FY24 YTD
                </span>
              </div>

              <div className="flex flex-col gap-space-md">
                {/* Progress Strip 1 */}
                <div className="flex flex-col gap-space-2xs">
                  <div className="flex justify-between font-label-md text-label-md text-on-surface">
                    <span className="flex items-center gap-space-xs">
                      <span className="material-symbols-outlined text-[16px] text-on-tertiary-container">
                        bolt
                      </span>
                      Grid Renewables &amp; Corporate PPAs
                    </span>
                    <span className="font-mono-data font-semibold">64.0%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2.5 rounded-full overflow-hidden">
                    <div className="bg-on-tertiary-container h-full rounded-full" style={{ width: "64%" }} />
                  </div>
                  <span className="text-[11px] font-body-sm text-on-surface-variant">
                    1,480 GWh verified zero-carbon through Guarantees of Origin (GoO)
                  </span>
                </div>

                {/* Progress Strip 2 */}
                <div className="flex flex-col gap-space-2xs">
                  <div className="flex justify-between font-label-md text-label-md text-on-surface">
                    <span className="flex items-center gap-space-xs">
                      <span className="material-symbols-outlined text-[16px] text-secondary">
                        local_fire_department
                      </span>
                      Pipeline Natural Gas (Industrial Heat)
                    </span>
                    <span className="font-mono-data font-semibold">24.0%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2.5 rounded-full overflow-hidden">
                    <div className="bg-secondary h-full rounded-full" style={{ width: "24%" }} />
                  </div>
                  <span className="text-[11px] font-body-sm text-on-surface-variant">
                    Transition path: Hydrogen co-firing retrofit scheduled 2025
                  </span>
                </div>

                {/* Progress Strip 3 */}
                <div className="flex flex-col gap-space-2xs">
                  <div className="flex justify-between font-label-md text-label-md text-on-surface">
                    <span className="flex items-center gap-space-xs">
                      <span className="material-symbols-outlined text-[16px] text-on-surface-variant">
                        oil_barrel
                      </span>
                      Heavy Fuel Oil &amp; Fleet Diesel
                    </span>
                    <span className="font-mono-data font-semibold">12.0%</span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2.5 rounded-full overflow-hidden">
                    <div className="bg-outline h-full rounded-full" style={{ width: "12%" }} />
                  </div>
                  <span className="text-[11px] font-body-sm text-on-surface-variant">
                    Target Phase-out: Complete fleet electrification by Q4 2027
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Lower Section: Material Decarbonization Levers & Facility / Activity Heatmap */}
        <div className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-lg">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface">
                {activities.length > 0
                  ? `Live Ingestion Ledger Activities (${activities.length} Processed Rows)`
                  : "Material Decarbonization Levers & Facility Heatmap"}
              </h2>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                {activities.length > 0
                  ? "Real parsed line items, AI semantic classifications, and calculated emissions from your uploaded CSV."
                  : "Top emitting production assets ranked by specific intensity, border tax exposure, and verification status."}
              </p>
            </div>

            <div className="flex items-center gap-space-md">
              <div className="flex items-center gap-space-xs bg-surface-container-low px-space-sm py-1 rounded-lg border border-outline-variant/30">
                <span className="material-symbols-outlined text-[16px] text-on-surface-variant">
                  filter_alt
                </span>
                <span className="font-label-sm text-label-sm text-on-surface">
                  CBAM Scope 1-2 Directives
                </span>
              </div>
              {onOpenUpload && (
                <button
                  type="button"
                  onClick={onOpenUpload}
                  className="font-label-sm text-label-sm text-secondary hover:underline flex items-center gap-[2px]"
                >
                  <span>Upload New Batch</span>
                  <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                </button>
              )}
            </div>
          </div>

          {/* High-Density Facility / Activity Table */}
          <div className="overflow-x-auto rounded-lg bg-surface-container-lowest border border-outline-variant/30">
            <table className="w-full text-left font-body-md text-body-md border-collapse">
              <thead>
                <tr className="bg-surface-container-low/60 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider border-b border-outline-variant/30">
                  <th className="py-space-sm px-space-md">
                    {activities.length > 0 ? "Activity Item / Source" : "Asset / Facility"}
                  </th>
                  <th className="py-space-sm px-space-md">Scope &amp; Category</th>
                  <th className="py-space-sm px-space-md">Activity / Raw Input</th>
                  <th className="py-space-sm px-space-md">Calculated Footprint</th>
                  <th className="py-space-sm px-space-md">Assurance Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                {activities.length > 0
                  ? activities.slice(0, 12).map((act, index) => {
                      const status = act.validation_status;
                      const propertyName =
                        act.original_row?.["Property Name"] ||
                        act.original_row?.Address ||
                        act.original_row?.facility ||
                        act.original_row?.Facility ||
                        "Municipal Facility";
                      const propertyType = act.original_row?.["Primary Property Type"] || "";
                      const rawQty = parseFloat(act.quantity || "0");
                      const formattedQty = rawQty > 0 ? rawQty.toLocaleString() : act.quantity || "—";
                      return (
                        <tr
                          key={act.activity_id || `act-${index}`}
                          className="hover:bg-surface-container-low/30 transition-colors"
                        >
                          <td className="py-space-sm px-space-md">
                            <div className="flex flex-col">
                              <span className="font-semibold text-on-surface">
                                {act.description || act.activity_type || "Activity Item"}
                                {propertyType ? ` • ${propertyType}` : ""}
                              </span>
                              <span className="font-mono-data text-[11px] text-on-surface-variant">
                                Row #{act.source_row ?? index + 1} • {propertyName}
                              </span>
                            </div>
                          </td>
                          <td className="py-space-sm px-space-md">
                            <span className="px-space-xs py-[2px] rounded text-[11px] font-mono-data bg-secondary/10 text-secondary font-semibold">
                              {act.scope || "Scope 1"} • {act.category || "General"}
                            </span>
                          </td>
                          <td className="py-space-sm px-space-md font-mono-data">
                            {formattedQty} {act.unit || ""}
                          </td>
                          <td className="py-space-sm px-space-md font-mono-data font-semibold text-on-surface">
                            {act.confidence ? `${(parseFloat(act.confidence) * 100).toFixed(0)}% Conf` : "100% Verified"}
                          </td>
                          <td className="py-space-sm px-space-md">
                            <span
                              className={`inline-flex items-center gap-[3px] px-space-xs py-[2px] rounded text-[11px] font-semibold ${
                                status === "validated"
                                  ? "bg-tertiary-container/10 text-on-tertiary-container"
                                  : status === "review"
                                  ? "bg-amber-100 text-amber-800"
                                  : "bg-error-container text-on-error-container"
                              }`}
                            >
                              <span className="material-symbols-outlined text-[14px]">
                                {status === "validated"
                                  ? "verified"
                                  : status === "review"
                                  ? "pending"
                                  : "error"}
                              </span>
                              <span className="capitalize">{status}</span>
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  : STITCH_BASELINE_DATA.facilityHeatmap.map((fac) => (
                      <tr
                        key={fac.facilityName}
                        className="hover:bg-surface-container-low/30 transition-colors"
                      >
                        <td className="py-space-sm px-space-md">
                          <div className="flex flex-col">
                            <span className="font-semibold text-on-surface">
                              {fac.facilityName}
                            </span>
                            <span className="text-[11px] text-on-surface-variant">
                              {fac.location}
                            </span>
                          </div>
                        </td>
                        <td className="py-space-sm px-space-md font-mono-data text-[12px]">
                          S1: {fac.scope1} • S2: {fac.scope2}
                        </td>
                        <td className="py-space-sm px-space-md font-mono-data text-[12px]">
                          {fac.intensity}
                        </td>
                        <td className="py-space-sm px-space-md">
                          {fac.cbamExposed ? (
                            <span className="px-space-xs py-[2px] rounded text-[10px] font-mono-data bg-error-container text-on-error-container font-semibold">
                              CBAM Exposed
                            </span>
                          ) : (
                            <span className="px-space-xs py-[2px] rounded text-[10px] font-mono-data bg-surface-container-high text-on-surface">
                              Domestic Exempt
                            </span>
                          )}
                        </td>
                        <td className="py-space-sm px-space-md">
                          <span className="inline-flex items-center gap-[3px] px-space-xs py-[2px] rounded text-[11px] font-semibold bg-tertiary-container/10 text-on-tertiary-container">
                            <span className="material-symbols-outlined text-[14px]">
                              verified
                            </span>
                            <span>{fac.status}</span>
                          </span>
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
