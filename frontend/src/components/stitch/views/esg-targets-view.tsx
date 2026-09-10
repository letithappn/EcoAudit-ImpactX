"use client";

import React from "react";
import { RunSummaryResponse } from "@/lib/types";

interface EsgTargetsViewProps {
  summary: RunSummaryResponse | null;
  onOpenUpload?: () => void;
}

export function EsgTargetsView({ summary, onOpenUpload }: EsgTargetsViewProps) {
  return (
    <div className="flex flex-col w-full">
      <div className="px-space-xl py-space-xl flex flex-col gap-space-xl">
        {/* Title Block */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md">
          <div className="flex flex-col gap-space-2xs">
            <div className="flex items-center gap-space-xs text-on-surface-variant font-mono-data text-mono-data uppercase tracking-wider">
              <span className="inline-block w-2 h-2 rounded-full bg-on-tertiary-container" />
              <span>SBTi Corporate Net-Zero Standard • CSRD ESRS E1 Aligned</span>
            </div>
            <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight font-bold">
              Multi-Year ESG Targets, Removals &amp; SBTi Pathways
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant max-w-4xl">
              Science-based trajectory tracking across Scope 1, 2, and 3 with verifiable carbon credits,
              high-durability CDR removals, and Egypt FRA compliance filings.
            </p>
          </div>

          <button
            type="button"
            onClick={onOpenUpload}
            className="flex items-center gap-space-xs bg-secondary hover:bg-secondary/90 text-on-secondary px-space-md py-space-sm rounded-lg font-label-md text-label-md font-semibold shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">add_task</span>
            <span>Update Annual ESG Filing</span>
          </button>
        </div>

        {/* 4 Multi-Year Milestones */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-space-md">
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              FY2024 Baseline
            </span>
            <div className="mt-space-md flex items-baseline gap-1">
              <span className="font-metric-xl text-metric-xl font-bold text-on-surface">1.43M</span>
              <span className="font-mono-data text-xs text-on-surface-variant">tCO₂e</span>
            </div>
            <span className="text-[11px] font-mono-data text-on-tertiary-container font-semibold mt-2">
              Verified 100% Assurance
            </span>
          </div>

          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              2027 Interim Goal
            </span>
            <div className="mt-space-md flex items-baseline gap-1">
              <span className="font-metric-xl text-metric-xl font-bold text-secondary">1.08M</span>
              <span className="font-mono-data text-xs text-on-surface-variant">tCO₂e (-25%)</span>
            </div>
            <span className="text-[11px] font-mono-data text-secondary font-semibold mt-2">
              On Track: H₂ Retrofit Phase 1
            </span>
          </div>

          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              2030 SBTi Target
            </span>
            <div className="mt-space-md flex items-baseline gap-1">
              <span className="font-metric-xl text-metric-xl font-bold text-on-tertiary-container">0.72M</span>
              <span className="font-mono-data text-xs text-on-surface-variant">tCO₂e (-50%)</span>
            </div>
            <span className="text-[11px] font-mono-data text-on-tertiary-container font-semibold mt-2">
              SBTi Validated 1.5°C
            </span>
          </div>

          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              2035 Net Zero
            </span>
            <div className="mt-space-md flex items-baseline gap-1">
              <span className="font-metric-xl text-metric-xl font-bold text-on-surface">&lt;0.14M</span>
              <span className="font-mono-data text-xs text-on-surface-variant">Residual</span>
            </div>
            <span className="text-[11px] font-mono-data text-on-tertiary-container font-semibold mt-2">
              Neutralized by CDR Removals
            </span>
          </div>
        </div>

        {/* Permanent Removals & Offsets Ledger */}
        <div className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-md">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface font-bold">
                Permanent Carbon Dioxide Removals (CDR) &amp; Certified Credits
              </h2>
              <span className="font-body-sm text-body-sm text-on-surface-variant">
                High-durability atmospheric removals aligned with the Oxford Principles for Net Zero Carbon Offsetting.
              </span>
            </div>
            <span className="font-mono-data text-[11px] bg-tertiary-container/10 text-on-tertiary-container px-space-sm py-1 rounded font-bold">
              ISO 14064-2 Verified
            </span>
          </div>

          <div className="overflow-x-auto rounded-lg border border-outline-variant/30">
            <table className="w-full text-left font-body-md text-body-md border-collapse">
              <thead>
                <tr className="bg-surface-container-low/60 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider border-b border-outline-variant/30">
                  <th className="py-space-sm px-space-md">Project Name &amp; Methodology</th>
                  <th className="py-space-sm px-space-md">Registry / Serial</th>
                  <th className="py-space-sm px-space-md">Durability</th>
                  <th className="py-space-sm px-space-md">Volume Retired</th>
                  <th className="py-space-sm px-space-md">Unit Cost</th>
                  <th className="py-space-sm px-space-md">Assurance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-semibold text-on-surface">
                    Northern Delta Biochar &amp; Soil Carbon Enhancement
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs text-secondary font-semibold">
                    PURO-EARTH-2024-8192
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs">
                    &gt; 500 Years
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    18,500 tCO₂e
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs">
                    €145 / tonne
                  </td>
                  <td className="py-space-sm px-space-md">
                    <span className="px-space-xs py-[2px] bg-tertiary-container/10 text-on-tertiary-container rounded text-xs font-semibold">
                      Retired &amp; Audited
                    </span>
                  </td>
                </tr>

                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-semibold text-on-surface">
                    Red Sea Mangrove Coastal Restoration &amp; Blue Carbon
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs text-secondary font-semibold">
                    VERRA-VCS-2024-3401
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs">
                    &gt; 100 Years
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    24,000 tCO₂e
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs">
                    €38 / tonne
                  </td>
                  <td className="py-space-sm px-space-md">
                    <span className="px-space-xs py-[2px] bg-tertiary-container/10 text-on-tertiary-container rounded text-xs font-semibold">
                      Active Monitoring
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
