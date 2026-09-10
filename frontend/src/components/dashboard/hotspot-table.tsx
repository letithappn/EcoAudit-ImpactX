"use client";

import React from "react";
import { HotspotDTO } from "@/lib/types";
import { IsaBadge } from "@/components/ui/isa-badge";
import { Flame, AlertTriangle, ArrowUpRight } from "lucide-react";

interface HotspotTableProps {
  hotspots: HotspotDTO[];
  emissionsUnit: string;
}

export function HotspotTable({ hotspots, emissionsUnit }: HotspotTableProps) {
  if (!hotspots || hotspots.length === 0) {
    return (
      <div className="p-8 text-center text-xs font-mono text-[#757575] bg-[#2F2F2F] rounded border border-[#4A4A4A]">
        No critical emission hotspots detected above baseline thresholds.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left font-mono text-xs border-collapse">
        <thead>
          <tr className="border-b border-[#4A4A4A] text-[#9E9E9E] bg-[#2B2B2B]">
            <th className="py-2.5 px-3 uppercase font-semibold">Rank</th>
            <th className="py-2.5 px-3 uppercase font-semibold">Hotspot Source / Dimension</th>
            <th className="py-2.5 px-3 uppercase font-semibold">Scope & Category</th>
            <th className="py-2.5 px-3 uppercase font-semibold text-right">Emissions</th>
            <th className="py-2.5 px-3 uppercase font-semibold text-right">Share of Total</th>
            <th className="py-2.5 px-3 uppercase font-semibold text-center">Severity</th>
            <th className="py-2.5 px-3 uppercase font-semibold text-center">Actionability</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#383838]">
          {hotspots.map((item) => (
            <tr
              key={`${item.rank}-${item.label}`}
              className="hover:bg-[#383838]/60 transition-colors"
            >
              <td className="py-3 px-3 text-[#757575] font-bold">
                #{item.rank}
              </td>
              <td className="py-3 px-3">
                <div className="flex items-center gap-2">
                  <Flame className="w-3.5 h-3.5 text-[#F57C00] flex-shrink-0" />
                  <span className="font-semibold text-[#E0E0E0]">{item.label}</span>
                </div>
                <span className="text-[10px] text-[#757575] mt-0.5 block">
                  {item.dimension} • {item.contributing_activities} Contributing Activities
                </span>
              </td>
              <td className="py-3 px-3 text-[#9E9E9E]">
                <div>{item.parent_scope || "Cross-Scope"}</div>
                <div className="text-[10px] text-[#757575]">
                  {item.parent_category || "Aggregated"}
                </div>
              </td>
              <td className="py-3 px-3 text-right font-bold text-[#FFFFFF]">
                {item.emissions} {emissionsUnit}
              </td>
              <td className="py-3 px-3 text-right">
                <div className="flex items-center justify-end gap-2">
                  <div className="w-16 h-1.5 bg-[#2B2B2B] rounded overflow-hidden border border-[#4A4A4A]">
                    <div
                      className="h-full bg-[#F57C00]"
                      style={{ width: `${Math.min(100, parseFloat(item.percentage_of_total))}%` }}
                    />
                  </div>
                  <span className="font-semibold text-[#F57C00]">
                    {item.percentage_of_total}%
                  </span>
                </div>
                {item.percentage_of_scope && (
                  <span className="text-[10px] text-[#757575] block text-right">
                    {item.percentage_of_scope}% of scope
                  </span>
                )}
              </td>
              <td className="py-3 px-3 text-center">
                <IsaBadge severity={item.severity} size="sm">
                  {item.severity}
                </IsaBadge>
              </td>
              <td className="py-3 px-3 text-center">
                <span
                  className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide border ${
                    item.actionability.toLowerCase() === "high"
                      ? "bg-[#1B3A24] text-[#43A047] border-[#43A047]/40"
                      : item.actionability.toLowerCase() === "medium"
                      ? "bg-[#0A3840] text-[#00ACC1] border-[#00ACC1]/40"
                      : "bg-[#2B2B2B] text-[#9E9E9E] border-[#4A4A4A]"
                  }`}
                >
                  {item.actionability}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
