"use client";

import React from "react";
import { RunSummaryResponse, ActivityDTO } from "@/lib/types";

interface Scope3SuppliersViewProps {
  summary: RunSummaryResponse | null;
  activities: ActivityDTO[];
  onOpenUpload?: () => void;
}

export function Scope3SuppliersView({
  summary,
  activities,
  onOpenUpload,
}: Scope3SuppliersViewProps) {
  const scope3Activities = activities.filter((a) => a.scope === "Scope 3");

  return (
    <div className="flex flex-col w-full">
      <div className="px-space-xl py-space-xl flex flex-col gap-space-xl">
        {/* Title Block */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md">
          <div className="flex flex-col gap-space-2xs">
            <div className="flex items-center gap-space-xs text-on-surface-variant font-mono-data text-mono-data uppercase tracking-wider">
              <span className="inline-block w-2 h-2 rounded-full bg-secondary" />
              <span>GHG Protocol Scope 3 Technical Guidance • Cat 1-15</span>
            </div>
            <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight font-bold">
              Scope 3 Value-Chain &amp; Supplier Decarbonization
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant max-w-4xl">
              Engagement platform for Tier-1 supply chain decarbonization, primary activity data collection,
              and hybrid spend-based carbon modeling.
            </p>
          </div>

          <button
            type="button"
            onClick={onOpenUpload}
            className="flex items-center gap-space-xs bg-secondary hover:bg-secondary/90 text-on-secondary px-space-md py-space-sm rounded-lg font-label-md text-label-md font-semibold shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">send</span>
            <span>Launch Supplier Campaign</span>
          </button>
        </div>

        {/* 4 Summary Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-space-md">
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              Total Scope 3 Pool
            </span>
            <div className="mt-space-md flex items-baseline gap-1">
              <span className="font-metric-xl text-metric-xl font-bold text-on-surface">1,148,300</span>
              <span className="font-mono-data text-xs text-on-surface-variant">tCO₂e</span>
            </div>
            <span className="text-[11px] font-mono-data text-secondary font-semibold mt-2">
              80.3% of Total Corporate Footprint
            </span>
          </div>

          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              Primary Data Ratio
            </span>
            <div className="mt-space-md flex items-baseline gap-1">
              <span className="font-metric-xl text-metric-xl font-bold text-on-tertiary-container">74.2%</span>
              <span className="font-mono-data text-xs text-on-surface-variant">Primary</span>
            </div>
            <span className="text-[11px] font-mono-data text-on-tertiary-container font-semibold mt-2">
              +18.4% YoY Supplier Response
            </span>
          </div>

          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              Active Tier-1 Suppliers
            </span>
            <div className="mt-space-md flex items-baseline gap-1">
              <span className="font-metric-xl text-metric-xl font-bold text-on-surface">184</span>
              <span className="font-mono-data text-xs text-on-surface-variant">Vendors</span>
            </div>
            <span className="text-[11px] font-mono-data text-on-surface-variant mt-2">
              142 Completed CDP/SBTi Audit
            </span>
          </div>

          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <span className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
              Target 2030 Reduction
            </span>
            <div className="mt-space-md flex items-baseline gap-1">
              <span className="font-metric-xl text-metric-xl font-bold text-secondary">-42.0%</span>
              <span className="font-mono-data text-xs text-on-surface-variant">SBTi</span>
            </div>
            <span className="text-[11px] font-mono-data text-on-tertiary-container font-semibold mt-2">
              Aligned with 1.5°C Paris Trajectory
            </span>
          </div>
        </div>

        {/* Supplier Scorecard Table */}
        <div className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-md">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface font-bold">
                Tier-1 Strategic Suppliers Carbon Assurance
              </h2>
              <span className="font-body-sm text-body-sm text-on-surface-variant">
                Ranked by spend volume, emission intensity, and CBAM primary certificate status.
              </span>
            </div>
            <button
              type="button"
              onClick={onOpenUpload}
              className="text-secondary font-label-sm text-label-sm font-semibold hover:underline flex items-center gap-1"
            >
              <span>Import Vendor Invoices</span>
              <span className="material-symbols-outlined text-[16px]">upload_file</span>
            </button>
          </div>

          <div className="overflow-x-auto rounded-lg border border-outline-variant/30">
            <table className="w-full text-left font-body-md text-body-md border-collapse">
              <thead>
                <tr className="bg-surface-container-low/60 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider border-b border-outline-variant/30">
                  <th className="py-space-sm px-space-md">Supplier / Vendor</th>
                  <th className="py-space-sm px-space-md">Category</th>
                  <th className="py-space-sm px-space-md">Annual Spend</th>
                  <th className="py-space-sm px-space-md">Reported Tonnage</th>
                  <th className="py-space-sm px-space-md">Data Quality</th>
                  <th className="py-space-sm px-space-md">SBTi Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-semibold text-on-surface">
                    Egypt Smelting &amp; Refining Co.
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs">
                    Cat 3.1 Purchased Metals
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data">$184M</td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    382,410 tCO₂e
                  </td>
                  <td className="py-space-sm px-space-md">
                    <span className="px-space-xs py-[2px] bg-tertiary-container/10 text-on-tertiary-container rounded text-xs font-semibold">
                      94% Primary CEMS
                    </span>
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs text-on-tertiary-container font-semibold">
                    Target Set 1.5°C
                  </td>
                </tr>

                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-semibold text-on-surface">
                    Mediterranean Bulk Cargo Lines
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs">
                    Cat 3.4 Upstream Logistics
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data">$62M</td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    154,000 tCO₂e
                  </td>
                  <td className="py-space-sm px-space-md">
                    <span className="px-space-xs py-[2px] bg-tertiary-container/10 text-on-tertiary-container rounded text-xs font-semibold">
                      88% Fuel Telemetry
                    </span>
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs text-secondary font-semibold">
                    Committed 2025
                  </td>
                </tr>

                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-semibold text-on-surface">
                    Suez Industrial Polymer Solutions
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs">
                    Cat 3.1 Specialty Polymers
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data">$48M</td>
                  <td className="py-space-sm px-space-md font-mono-data font-semibold">
                    98,200 tCO₂e
                  </td>
                  <td className="py-space-sm px-space-md">
                    <span className="px-space-xs py-[2px] bg-surface-container-high text-on-surface rounded text-xs font-semibold">
                      76% Hybrid
                    </span>
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-xs text-on-surface-variant">
                    Under Review
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
