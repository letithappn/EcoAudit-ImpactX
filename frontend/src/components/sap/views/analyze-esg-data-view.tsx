"use client";

import React, { useState } from "react";
import { Search, X, ChevronDown, ArrowUp, ArrowDown } from "lucide-react";
import { RunSummaryResponse } from "@/lib/types";

interface EsgTile {
  title: string;
  unit: string;
  target: string;
  actual: string;
  isOverTarget: boolean;
  isGoodWhenHigh?: boolean;
  historical: { year: number; actual: number; target: number }[];
}

const DEFAULT_TILES: EsgTile[] = [
  {
    title: "Gross GHG Emissions – Scope 1",
    unit: "Ton",
    target: "294.42K",
    actual: "330.02K",
    isOverTarget: true,
    historical: [
      { year: 2021, actual: 40, target: 290 },
      { year: 2022, actual: 350, target: 290 },
      { year: 2023, actual: 310, target: 290 },
      { year: 2024, actual: 340, target: 290 },
      { year: 2025, actual: 330, target: 290 },
    ],
  },
  {
    title: "Gross GHG Emissions – Scope 2, Lo...",
    unit: "Ton",
    target: "66.18K",
    actual: "87.34K",
    isOverTarget: true,
    historical: [
      { year: 2021, actual: 20, target: 66 },
      { year: 2022, actual: 95, target: 66 },
      { year: 2023, actual: 70, target: 66 },
      { year: 2024, actual: 110, target: 66 },
      { year: 2025, actual: 87, target: 66 },
    ],
  },
  {
    title: "Gross GHG Emissions – Scope 3",
    unit: "Ton",
    target: "1.56M",
    actual: "1.76M",
    isOverTarget: true,
    historical: [
      { year: 2021, actual: 200, target: 1560 },
      { year: 2022, actual: 1750, target: 1560 },
      { year: 2023, actual: 1600, target: 1560 },
      { year: 2024, actual: 1800, target: 1560 },
      { year: 2025, actual: 1760, target: 1560 },
    ],
  },
  {
    title: "Total Gross GHG Emissions – Locati...",
    unit: "Ton",
    target: "1.92M",
    actual: "2.17M",
    isOverTarget: true,
    historical: [
      { year: 2021, actual: 300, target: 1920 },
      { year: 2022, actual: 2200, target: 1920 },
      { year: 2023, actual: 2000, target: 1920 },
      { year: 2024, actual: 2250, target: 1920 },
      { year: 2025, actual: 2170, target: 1920 },
    ],
  },
  {
    title: "Carbon Credits",
    unit: "Ton",
    target: "29.34",
    actual: "30.00",
    isOverTarget: false,
    isGoodWhenHigh: true,
    historical: [
      { year: 2021, actual: 0, target: 29 },
      { year: 2022, actual: 30, target: 29 },
      { year: 2023, actual: 30, target: 29 },
      { year: 2024, actual: 30, target: 29 },
      { year: 2025, actual: 30, target: 29 },
    ],
  },
  {
    title: "Emissions to Air",
    unit: "Ton",
    target: "1.92M",
    actual: "1.64M",
    isOverTarget: false,
    historical: [
      { year: 2021, actual: 200, target: 1920 },
      { year: 2022, actual: 1800, target: 1920 },
      { year: 2023, actual: 1700, target: 1920 },
      { year: 2024, actual: 1750, target: 1920 },
      { year: 2025, actual: 1640, target: 1920 },
    ],
  },
  {
    title: "Emissions to Water",
    unit: "Ton",
    target: "431.42K",
    actual: "444.97K",
    isOverTarget: true,
    historical: [
      { year: 2021, actual: 80, target: 431 },
      { year: 2022, actual: 430, target: 431 },
      { year: 2023, actual: 420, target: 431 },
      { year: 2024, actual: 450, target: 431 },
      { year: 2025, actual: 444, target: 431 },
    ],
  },
  {
    title: "Emissions to Soil",
    unit: "Ton",
    target: "72.89K",
    actual: "85.55K",
    isOverTarget: true,
    historical: [
      { year: 2021, actual: 10, target: 72 },
      { year: 2022, actual: 80, target: 72 },
      { year: 2023, actual: 75, target: 72 },
      { year: 2024, actual: 88, target: 72 },
      { year: 2025, actual: 85, target: 72 },
    ],
  },
  {
    title: "Percentage of Scope 1 Emissions U...",
    unit: "%",
    target: "30.00",
    actual: "27.93%",
    isOverTarget: true,
    historical: [
      { year: 2021, actual: 5, target: 30 },
      { year: 2022, actual: 25, target: 30 },
      { year: 2023, actual: 26, target: 30 },
      { year: 2024, actual: 28, target: 30 },
      { year: 2025, actual: 27.9, target: 30 },
    ],
  },
  {
    title: "GHG Emission Intensity, Location-B...",
    unit: "tM USD",
    target: "447.79",
    actual: "4.78K",
    isOverTarget: true,
    historical: [
      { year: 2021, actual: 100, target: 447 },
      { year: 2022, actual: 520, target: 447 },
      { year: 2023, actual: 480, target: 447 },
      { year: 2024, actual: 500, target: 447 },
      { year: 2025, actual: 478, target: 447 },
    ],
  },
];

interface AnalyzeEsgDataViewProps {
  summary?: RunSummaryResponse | null;
}

export function AnalyzeEsgDataView({ summary }: AnalyzeEsgDataViewProps) {
  const [periodChips, setPeriodChips] = useState(["2022", "2023", "2024", "2025"]);
  const [structureChip, setStructureChip] = useState("=Business Location");

  const removePeriod = (p: string) => {
    setPeriodChips((prev) => prev.filter((item) => item !== p));
  };

  return (
    <div className="flex flex-col gap-5 max-w-7xl mx-auto w-full p-6 select-none">
      {/* 1. Header Toolbar with Filter Bar matching Image 3 */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-1 text-sm font-semibold text-[#0070F2] cursor-pointer">
            <span>Global</span>
            <ChevronDown className="w-4 h-4 text-[#0070F2]" />
          </div>
          <button
            type="button"
            className="px-3 py-1 bg-white border border-[#CBD5E1] rounded text-xs font-semibold text-[#0070F2] hover:bg-[#F8FAFC]"
          >
            Manage Tiles
          </button>
        </div>

        {/* Filter Bar Controls */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 text-xs items-end">
          {/* Search */}
          <div className="md:col-span-2">
            <input
              type="text"
              placeholder="Search"
              className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
            />
          </div>

          {/* Period Multi-Chips */}
          <div className="md:col-span-3">
            <label className="block text-[#556B82] font-semibold mb-1 text-[11px]">Period:*</label>
            <div className="flex flex-wrap gap-1 p-1 bg-white border border-[#CBD5E1] rounded min-h-[32px] items-center">
              {periodChips.map((p) => (
                <span
                  key={p}
                  className="inline-flex items-center gap-1 bg-[#F1F5F9] text-[#1C2B36] px-2 py-0.5 rounded text-[11px]"
                >
                  <span>{p}</span>
                  <X
                    className="w-3 h-3 text-[#556B82] hover:text-[#DC2626] cursor-pointer"
                    onClick={() => removePeriod(p)}
                  />
                </span>
              ))}
            </div>
          </div>

          {/* Reporting Structure */}
          <div className="md:col-span-3">
            <label className="block text-[#556B82] font-semibold mb-1 text-[11px]">Reporting Structure:*</label>
            <div className="flex items-center justify-between px-2.5 py-1.5 bg-white border border-[#CBD5E1] rounded text-xs">
              <span className="text-[#1C2B36] truncate">{structureChip}</span>
              <X
                className="w-3 h-3 text-[#556B82] hover:text-[#DC2626] cursor-pointer"
                onClick={() => setStructureChip("")}
              />
            </div>
          </div>

          {/* Group Name */}
          <div className="md:col-span-2">
            <label className="block text-[#556B82] font-semibold mb-1 text-[11px]">Group Name:</label>
            <select className="w-full bg-white border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1C2B36]">
              <option value="">All Groups</option>
              <option value="manufacturing">Manufacturing</option>
              <option value="logistics">Logistics</option>
            </select>
          </div>

          {/* Go & Clear Buttons */}
          <div className="md:col-span-2 flex items-center gap-2">
            <button
              type="button"
              className="px-4 py-1.5 bg-[#0070F2] hover:bg-[#0057D2] text-white rounded font-semibold text-xs transition-colors shadow-sm"
            >
              Go
            </button>
            <button
              type="button"
              className="px-3 py-1.5 text-[#0070F2] hover:underline font-semibold text-xs"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* 2. Environmental Header */}
      <div className="pt-2">
        <h3 className="text-sm font-bold text-[#1C2B36]">Environmental</h3>
      </div>

      {/* 3. 10 ESG KPI Tiles in Grid matching Image 3 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {DEFAULT_TILES.map((tile, idx) => {
          const isRed = tile.isOverTarget && !tile.isGoodWhenHigh;
          const textColor = isRed ? "text-[#DC2626]" : "text-[#16A34A]";
          const ArrowIcon = isRed ? ArrowUp : ArrowDown;

          return (
            <div
              key={idx}
              className="bg-white rounded-xl border border-[#E2E8F0] shadow-xs p-4 flex flex-col justify-between hover:shadow-md transition-shadow cursor-pointer"
            >
              <div>
                <h4 className="text-xs font-semibold text-[#1C2B36] line-clamp-1" title={tile.title}>
                  {tile.title}
                </h4>

                <div className="flex items-baseline justify-between mt-2 text-[11px] text-[#556B82]">
                  <span>{tile.unit}</span>
                  <span>Target {tile.target}</span>
                </div>

                {/* Big Number Display with Up/Down arrow */}
                <div className="flex items-center gap-1 mt-1">
                  <span className={`text-2xl font-bold tracking-tight ${textColor}`}>
                    {tile.actual}
                  </span>
                  <ArrowIcon className={`w-4 h-4 ${textColor}`} />
                </div>
              </div>

              {/* Year Stamp */}
              <div className="text-[10px] text-[#899AA8] mt-2 font-medium">2025</div>

              {/* Mini Column Bar Chart matching Image 3 */}
              <div className="mt-2 pt-2 border-t border-[#F1F5F9]">
                <div className="h-16 w-full flex items-end justify-between gap-1.5 px-1 relative">
                  {/* Black Horizontal Target Line */}
                  <div
                    className="absolute left-0 right-0 border-t-2 border-[#1C2B36] z-10"
                    style={{ top: "35%" }}
                  />

                  {tile.historical.map((bar) => {
                    const heightPct = Math.min(95, Math.max(15, (bar.actual / (bar.target * 1.3)) * 100));
                    return (
                      <div key={bar.year} className="flex-1 flex flex-col items-center h-full justify-end">
                        <div
                          className="w-full bg-[#0070F2] rounded-t-xs transition-all hover:bg-[#0057D2]"
                          style={{ height: `${heightPct}%` }}
                        />
                        <span className="text-[8px] text-[#899AA8] mt-1">{bar.year}</span>
                      </div>
                    );
                  })}
                </div>

                {/* Legend */}
                <div className="flex items-center gap-2 justify-center text-[9px] text-[#556B82] mt-2">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-[#0070F2] inline-block" /> Actual
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2.5 h-[2px] bg-[#1C2B36] inline-block" /> Target
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
