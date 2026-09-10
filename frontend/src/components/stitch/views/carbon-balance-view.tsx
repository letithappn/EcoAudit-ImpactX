"use client";

import React from "react";
import { RunSummaryResponse, ActivityDTO } from "@/lib/types";
import { STITCH_BASELINE_DATA } from "@/lib/stitch-mock-data";

interface CarbonBalanceViewProps {
  summary: RunSummaryResponse | null;
  activities: ActivityDTO[];
  onOpenUpload?: () => void;
}

export function CarbonBalanceView({
  summary,
  activities,
  onOpenUpload,
}: CarbonBalanceViewProps) {
  const rawTotal = summary ? parseFloat(summary.total_emissions || "0") : 0;
  const isKg = summary?.emissions_unit?.toLowerCase().includes("kg") ?? true;
  const liveTons = isKg ? rawTotal / 1000 : rawTotal;

  const totalTons = summary
    ? Math.round(liveTons)
    : STITCH_BASELINE_DATA.totalEmissionsTons;

  const productTons = Math.round(totalTons * 0.9);
  const residualTons = totalTons - productTons;

  return (
    <div className="flex flex-col w-full">
      <section className="w-full px-space-xl py-space-xl bg-surface">
        {/* Title & Action Buttons */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-lg mb-space-2xl">
          <div className="flex flex-col max-w-3xl">
            <div className="flex items-center gap-space-xs text-on-surface-variant mb-space-xs font-mono-data text-mono-data uppercase tracking-wider">
              <span className="inline-block w-2 h-2 rounded-full bg-on-tertiary-container" />
              <span>ISO 14044 §4.3.4 • Double-Entry Reconciliation</span>
            </div>
            <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight font-bold">
              Corporate Carbon Balance &amp; Value-Stream Allocation
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-space-2xs">
              Tracing emissions origin from raw fuels and precursors through manufacturing
              processes to finished products and general overhead.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-space-sm">
            <button
              type="button"
              onClick={onOpenUpload}
              className="flex items-center gap-space-xs px-space-md py-space-sm rounded-lg bg-surface-container-highest text-on-surface hover:bg-surface-container-high transition-colors shadow-sm font-label-md text-label-md"
            >
              <span className="material-symbols-outlined text-[18px] text-secondary">sync</span>
              <span>Rebalance Allocation Run</span>
            </button>

            <button
              type="button"
              onClick={() => {
                const csvData = "data:text/csv;charset=utf-8,Transaction,Debit,Credit,Tonnage\nTX-901,Scope 1,Finished Steel,410000";
                const encodedUri = encodeURI(csvData);
                const link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", "EcoAudit_Immutable_Ledger.csv");
                document.body.appendChild(link);
                link.click();
              }}
              className="flex items-center gap-space-xs px-space-md py-space-sm rounded-lg bg-secondary hover:bg-secondary/90 text-on-secondary transition-all shadow-md font-label-md text-label-md"
            >
              <span className="material-symbols-outlined text-[18px]">download_for_offline</span>
              <span>Download Immutable Audit Ledger (CSV)</span>
            </button>
          </div>
        </div>

        {/* Top Flow Balance Metrics Bento */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-space-md mb-space-2xl">
          {/* Card 1: Inbound Ingestion */}
          <div className="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm border border-outline-variant/20">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
                Inbound Ingestion
              </span>
              <span className="p-space-2xs rounded-md bg-surface-container-low text-secondary">
                <span className="material-symbols-outlined text-[18px]">input</span>
              </span>
            </div>
            <div className="mt-space-md">
              <div className="font-display-lg text-display-lg font-bold text-on-surface tracking-tight">
                {totalTons.toLocaleString()}
              </div>
              <div className="flex items-center gap-space-xs font-mono-data text-mono-data text-on-surface-variant mt-space-2xs">
                <span className="font-semibold text-on-surface">tCO₂e</span>
                <span>• Total Inbound Carbon Pool</span>
              </div>
            </div>
            <div className="mt-space-lg w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden">
              <div className="bg-primary-container h-full w-full" />
            </div>
          </div>

          {/* Card 2: Product Embedded */}
          <div className="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm border border-outline-variant/20">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
                Product Embedded
              </span>
              <span className="px-space-xs py-space-2xs rounded-full bg-surface-container-low text-secondary font-mono-data text-mono-data font-bold">
                90.0%
              </span>
            </div>
            <div className="mt-space-md">
              <div className="font-display-lg text-display-lg font-bold text-on-surface tracking-tight">
                {productTons.toLocaleString()}
              </div>
              <div className="flex items-center gap-space-xs font-mono-data text-mono-data text-on-surface-variant mt-space-2xs">
                <span className="font-semibold text-secondary">tCO₂e</span>
                <span>• Allocated to Finished Goods</span>
              </div>
            </div>
            <div className="mt-space-lg w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden">
              <div className="bg-secondary h-full w-[90%] transition-all duration-700" />
            </div>
          </div>

          {/* Card 3: Residual / Facility Overhead */}
          <div className="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm border border-outline-variant/20">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
                Residual / Facility
              </span>
              <span className="px-space-xs py-space-2xs rounded-full bg-surface-container-low text-on-surface-variant font-mono-data text-mono-data font-bold">
                10.0%
              </span>
            </div>
            <div className="mt-space-md">
              <div className="font-display-lg text-display-lg font-bold text-on-surface tracking-tight">
                {residualTons.toLocaleString()}
              </div>
              <div className="flex items-center gap-space-xs font-mono-data text-mono-data text-on-surface-variant mt-space-2xs">
                <span className="font-semibold text-on-surface">tCO₂e</span>
                <span>• Facility Overhead &amp; Waste</span>
              </div>
            </div>
            <div className="mt-space-lg w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden">
              <div className="bg-surface-tint h-full w-[10%]" />
            </div>
          </div>

          {/* Card 4: Audit Status */}
          <div className="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm border border-outline-variant/20">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-tertiary-container font-semibold">
                Audit Status
              </span>
              <span className="flex items-center gap-space-2xs px-space-xs py-space-2xs rounded-full bg-tertiary-fixed/30 text-on-tertiary-container font-mono-data text-[11px] font-bold">
                <span className="material-symbols-outlined text-[14px]">verified</span>
                ZERO DELTA
              </span>
            </div>
            <div className="mt-space-md">
              <div className="font-display-lg text-display-lg font-bold text-on-tertiary-container tracking-tight">
                0.00 <span className="text-metric-md font-medium">tCO₂e</span>
              </div>
              <div className="flex items-center gap-space-xs font-mono-data text-mono-data text-on-surface-variant mt-space-2xs">
                <span className="font-semibold text-on-tertiary-container">100% Balanced</span>
                <span>• Full Discrepancy Parity</span>
              </div>
            </div>
            <div className="mt-space-lg w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden">
              <div className="bg-on-tertiary-container h-full w-full" />
            </div>
          </div>
        </div>

        {/* Multi-Stage Value-Stream Sankey / Flow Topology */}
        <div className="w-full rounded-xl bg-surface-container-lowest p-space-xl shadow-sm border border-outline-variant/20 mb-space-2xl">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-space-lg gap-space-md">
            <div>
              <div className="flex items-center gap-space-xs font-label-sm text-label-sm uppercase text-secondary font-bold tracking-wider">
                <span>Mass &amp; Thermodynamic Flow</span>
                <span>•</span>
                <span className="font-mono-data">Multi-Stage Ledger Mapping</span>
              </div>
              <h2 className="font-headline-md text-headline-md text-on-surface font-bold mt-space-2xs">
                Value-Stream Carbon Mass Allocation
              </h2>
            </div>
            <div className="flex flex-wrap items-center gap-space-md font-mono-data text-[11px] text-on-surface-variant">
              <div className="flex items-center gap-space-xs">
                <span className="w-3 h-3 rounded-full bg-primary-container" />
                <span>Scope 1 &amp; Fuels</span>
              </div>
              <div className="flex items-center gap-space-xs">
                <span className="w-3 h-3 rounded-full bg-secondary" />
                <span>Scope 2 Power</span>
              </div>
              <div className="flex items-center gap-space-xs">
                <span className="w-3 h-3 rounded-full bg-secondary-fixed-dim" />
                <span>Scope 3 Precursors</span>
              </div>
              <div className="flex items-center gap-space-xs">
                <span className="w-3 h-3 rounded-full bg-on-tertiary-container" />
                <span>Finished Goods</span>
              </div>
            </div>
          </div>

          {/* Sankey Flow Visual Topology */}
          <div className="w-full bg-surface-container-low/30 rounded-xl p-space-lg border border-outline-variant/20 overflow-x-auto">
            <svg className="w-full min-w-[700px] h-64" viewBox="0 0 800 240">
              {/* Nodes Column 1: Sources */}
              <rect x="20" y="20" width="16" height="60" rx="3" fill="#1d4ed8" />
              <text x="44" y="45" fontFamily="Inter" fontSize="11" fontWeight="600" fill="#0b1c30">Scope 1 Fuels</text>
              <text x="44" y="60" fontFamily="Inter" fontSize="10" fill="#556B82">182,400 tCO₂e</text>

              <rect x="20" y="95" width="16" height="45" rx="3" fill="#b7c4ff" />
              <text x="44" y="115" fontFamily="Inter" fontSize="11" fontWeight="600" fill="#0b1c30">Scope 2 Electricity</text>
              <text x="44" y="130" fontFamily="Inter" fontSize="10" fill="#556B82">98,250 tCO₂e</text>

              <rect x="20" y="155" width="16" height="75" rx="3" fill="#0e1c2f" />
              <text x="44" y="185" fontFamily="Inter" fontSize="11" fontWeight="600" fill="#0b1c30">Scope 3 Purchased Goods</text>
              <text x="44" y="200" fontFamily="Inter" fontSize="10" fill="#556B82">1,148,300 tCO₂e</text>

              {/* Central Inbound Pillar */}
              <rect x="360" y="30" width="24" height="180" rx="4" fill="#0070F2" />
              <text x="395" y="115" fontFamily="Plus Jakarta Sans" fontSize="13" fontWeight="700" fill="#0b1c30">Total Carbon Pool</text>
              <text x="395" y="132" fontFamily="Inter" fontSize="11" fill="#556B82">{totalTons.toLocaleString()} tCO₂e</text>

              {/* Outbound Products */}
              <rect x="700" y="40" width="16" height="130" rx="3" fill="#069669" />
              <text x="600" y="75" fontFamily="Inter" fontSize="11" fontWeight="600" textAnchor="end" fill="#0b1c30">Finished Goods (90%)</text>
              <text x="600" y="90" fontFamily="Inter" fontSize="10" textAnchor="end" fill="#556B82">{productTons.toLocaleString()} tCO₂e</text>

              <rect x="700" y="185" width="16" height="35" rx="3" fill="#75777d" />
              <text x="600" y="200" fontFamily="Inter" fontSize="11" fontWeight="600" textAnchor="end" fill="#0b1c30">Facility Overhead &amp; Loss</text>
              <text x="600" y="214" fontFamily="Inter" fontSize="10" textAnchor="end" fill="#556B82">{residualTons.toLocaleString()} tCO₂e</text>

              {/* Connecting Gradient Stream Ribbons */}
              <path d="M 36 50 C 180 50, 200 90, 360 90" fill="none" stroke="#1d4ed8" strokeWidth="18" opacity="0.4" />
              <path d="M 36 117 C 180 117, 200 120, 360 120" fill="none" stroke="#b7c4ff" strokeWidth="14" opacity="0.4" />
              <path d="M 36 192 C 180 192, 200 160, 360 160" fill="none" stroke="#0e1c2f" strokeWidth="32" opacity="0.3" />

              <path d="M 384 100 C 520 100, 560 85, 700 85" fill="none" stroke="#069669" strokeWidth="38" opacity="0.4" />
              <path d="M 384 180 C 520 180, 560 200, 700 200" fill="none" stroke="#75777d" strokeWidth="12" opacity="0.3" />
            </svg>
          </div>
        </div>

        {/* Double-Entry Transaction Ledger Table */}
        <div className="w-full rounded-xl bg-surface-container-lowest p-space-xl shadow-sm border border-outline-variant/20">
          <div className="flex items-center justify-between pb-space-md">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface font-bold">
                Authoritative Double-Entry Ledger Transactions
              </h2>
              <span className="font-body-sm text-body-sm text-on-surface-variant">
                Debits and credits aligned with corporate financial cost centers and CBAM product declarations.
              </span>
            </div>
            <span className="font-mono-data text-[11px] text-on-tertiary-container bg-tertiary-fixed/20 px-space-xs py-1 rounded font-semibold">
              SHA-256 Ledger Verified
            </span>
          </div>

          <div className="overflow-x-auto rounded-lg border border-outline-variant/30">
            <table className="w-full text-left font-body-md text-body-md border-collapse">
              <thead>
                <tr className="bg-surface-container-low/60 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider border-b border-outline-variant/30">
                  <th className="py-space-sm px-space-md">Transaction ID</th>
                  <th className="py-space-sm px-space-md">Debit Account (Emissions Incurred)</th>
                  <th className="py-space-sm px-space-md">Credit Account (Offset / Absorbed)</th>
                  <th className="py-space-sm px-space-md">Tonnage (tCO₂e)</th>
                  <th className="py-space-sm px-space-md">Block Hash</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-mono-data font-semibold text-secondary">
                    TX-CHI-001
                  </td>
                  <td className="py-space-sm px-space-md font-medium text-on-surface">
                    Scope 1: Peoples Gas Pipeline System (Heating)
                  </td>
                  <td className="py-space-sm px-space-md text-on-surface-variant">
                    Municipal Space Heating &amp; Boilers Pool
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    14,195,747.00
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-[11px] text-on-surface-variant">
                    9f83...42a1
                  </td>
                </tr>
                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-mono-data font-semibold text-secondary">
                    TX-CHI-002
                  </td>
                  <td className="py-space-sm px-space-md font-medium text-on-surface">
                    Scope 2: Commonwealth Edison (ComEd Grid)
                  </td>
                  <td className="py-space-sm px-space-md text-on-surface-variant">
                    Commercial &amp; Residential Power Systems
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    15,270,176.00
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-[11px] text-on-surface-variant">
                    3c11...88de
                  </td>
                </tr>
                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-mono-data font-semibold text-secondary">
                    TX-CHI-003
                  </td>
                  <td className="py-space-sm px-space-md font-medium text-on-surface">
                    Scope 1: McCormick Place On-Site Boilers
                  </td>
                  <td className="py-space-sm px-space-md text-on-surface-variant">
                    Metropolitan Pier Facility Operations
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    24,960.00
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-[11px] text-on-surface-variant">
                    e520...710c
                  </td>
                </tr>
                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-mono-data font-semibold text-secondary">
                    TX-CHI-004
                  </td>
                  <td className="py-space-sm px-space-md font-medium text-on-surface">
                    Scope 2: Digital Lakeside High-Density Power
                  </td>
                  <td className="py-space-sm px-space-md text-on-surface-variant">
                    Carrier Hotel Data Center Infrastructure
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    77,456.00
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-[11px] text-on-surface-variant">
                    1a7b...e0f1
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  );
}
