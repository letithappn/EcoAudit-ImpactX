"use client";

import React, { useState } from "react";
import {
  Filter,
  ChevronRight,
  ChevronDown,
  X,
  PieChart as PieIcon,
  TrendingDown,
  TrendingUp,
  BarChart2,
} from "lucide-react";
import { RunSummaryResponse } from "@/lib/types";

interface SacStoriesViewProps {
  summary?: RunSummaryResponse | null;
}

export function SacStoriesView({ summary }: SacStoriesViewProps) {
  const [filterOpen, setFilterOpen] = useState(true);

  // Authoritative total or fallback to SAP template values
  const totalEmissionsVal = summary ? summary.total_emissions : "159";
  const unit = summary ? summary.emissions_unit : "tCO2e";

  return (
    <div className="flex-1 flex flex-col bg-white min-h-[850px] select-none text-xs">
      {/* 1. SAP Analytics Cloud Story Navigation Bar matching Image 5 */}
      <div className="bg-[#1C2B36] text-white px-4 py-2 flex items-center justify-between border-b border-[#334155]">
        <div className="flex items-center gap-3">
          <span className="font-mono text-sm">≡</span>
          <div className="flex items-center gap-1.5 font-bold">
            <span className="text-[#60A5FA]">‹ SAP</span>
            <span className="text-gray-300">Stories</span>
            <span className="text-gray-500">|</span>
            <span className="text-xs font-normal text-white bg-[#334155] px-2 py-0.5 rounded flex items-center gap-2">
              <span>SAP_GRL_DSP_GreenHouseG...</span>
              <X className="w-3 h-3 text-gray-400 hover:text-white cursor-pointer" />
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-gray-300 text-[11px]">
          <span className="bg-[#0070F2] text-white px-2 py-0.5 rounded font-bold">1</span>
          <span>1 / 4 ›</span>
        </div>
      </div>

      {/* 2. Story Submenu Bar */}
      <div className="bg-[#F8FAFC] border-b border-[#E2E8F0] px-4 py-1.5 flex items-center justify-between text-[#556B82] text-[11px]">
        <div className="flex items-center gap-4">
          <span className="hover:text-[#1C2B36] cursor-pointer">File ▾</span>
          <span className="hover:text-[#1C2B36] cursor-pointer">Edit ▾</span>
          <span className="hover:text-[#1C2B36] cursor-pointer">Tools ▾</span>
          <span className="hover:text-[#1C2B36] cursor-pointer">Display ▾</span>
          <div className="h-3.5 w-[1px] bg-[#CBD5E1]" />
          <button
            type="button"
            onClick={() => setFilterOpen(!filterOpen)}
            className={`flex items-center gap-1 px-2 py-0.5 rounded font-semibold ${
              filterOpen ? "bg-[#0070F2] text-white" : "hover:bg-[#E2E8F0] text-[#1C2B36]"
            }`}
          >
            <Filter className="w-3 h-3" />
            <span>Filters</span>
          </button>
          <span className="font-semibold text-[#1C2B36]">GHG Emissions Overview ▾</span>
        </div>
      </div>

      {/* 3. Main SAC Layout: Collapsible Left Filter Sidebar + Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Filter Sidebar matching Image 5 */}
        {filterOpen && (
          <aside className="w-64 bg-[#FAFBFC] border-r border-[#E2E8F0] p-3.5 flex flex-col gap-4 overflow-y-auto text-[11px] text-[#556B82]">
            <div className="flex items-center justify-between font-bold text-[#1C2B36]">
              <span>Filters</span>
              <X className="w-3.5 h-3.5 cursor-pointer text-[#899AA8]" onClick={() => setFilterOpen(false)} />
            </div>

            {/* Applied to All Pages */}
            <div className="flex flex-col gap-2">
              <div className="font-bold text-[#1C2B36] flex items-center justify-between">
                <span>Applied to All Pages (11) ⓘ</span>
                <ChevronDown className="w-3.5 h-3.5 text-[#899AA8]" />
              </div>

              <div className="p-2 bg-white rounded border border-[#E2E8F0] flex flex-col gap-1">
                <span className="text-[10px] text-[#899AA8]">Currency Role / Currency</span>
                <span className="text-[#0070F2] font-semibold">USD (Group Currency)</span>
              </div>

              <div className="p-2 bg-white rounded border border-[#E2E8F0] flex flex-col gap-1">
                <span className="text-[10px] text-[#899AA8]">Unit of Carbon</span>
                <span className="text-[#0070F2] font-semibold">Ton</span>
              </div>

              <div className="p-2 bg-white rounded border border-[#E2E8F0] flex flex-col gap-1">
                <span className="text-[10px] text-[#899AA8]">End Period - Fiscal Year</span>
                <span className="text-[#0070F2] font-semibold">2024</span>
              </div>

              <div className="p-2 bg-white rounded border border-[#E2E8F0] flex flex-col gap-1">
                <span className="text-[10px] text-[#899AA8]">Profit Center</span>
                <span className="text-[#0070F2] font-semibold">(All)</span>
              </div>

              <div className="p-2 bg-white rounded border border-[#E2E8F0] flex flex-col gap-1">
                <span className="text-[10px] text-[#899AA8]">Segment</span>
                <span className="text-[#0070F2] font-semibold">(All)</span>
              </div>
            </div>

            {/* Applied to This Page */}
            <div className="flex flex-col gap-2 pt-2 border-t border-[#E2E8F0]">
              <div className="font-bold text-[#1C2B36] flex items-center justify-between">
                <span>Applied to This Page (2) ⓘ</span>
                <ChevronDown className="w-3.5 h-3.5 text-[#899AA8]" />
              </div>
              <div className="p-2 bg-white rounded border border-[#E2E8F0] flex flex-col gap-1">
                <span className="text-[10px] text-[#899AA8]">GHG Category</span>
                <span className="text-[#0070F2] font-semibold">(All)</span>
              </div>
            </div>
          </aside>
        )}

        {/* Main Analytics Canvas matching Image 5 */}
        <div className="flex-1 p-5 overflow-y-auto flex flex-col gap-5 bg-white">
          {/* Top Row: Combined GHG & Finance KPIs + Finance KPIs */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            {/* Combined GHG & Finance KPIs (7 cols) */}
            <div className="lg:col-span-7 bg-white rounded-xl border border-[#E2E8F0] shadow-xs p-4 flex flex-col justify-between">
              <h4 className="font-bold text-[#1C2B36] text-xs mb-3">Combined GHG and Finance KPIs</h4>
              <div className="grid grid-cols-4 gap-2 text-center">
                <div className="p-2 bg-[#F8FAFC] rounded">
                  <span className="text-[10px] text-[#556B82] block">GHG Emissions</span>
                  <span className="text-[9px] text-[#899AA8]">in {unit}</span>
                  <span className="text-xl font-bold text-[#1C2B36] block mt-1">{totalEmissionsVal}</span>
                  <span className="text-[10px] text-[#16A34A] font-semibold">-30% Δ Prev</span>
                </div>

                <div className="p-2 bg-[#F8FAFC] rounded">
                  <span className="text-[10px] text-[#556B82] block">GHG Int. / Op. Inc.</span>
                  <span className="text-[9px] text-[#899AA8]">in tCO2e/USD</span>
                  <span className="text-xl font-bold text-[#1C2B36] block mt-1">+12</span>
                  <span className="text-[10px] text-[#16A34A] font-semibold">-10% Δ Prev</span>
                </div>

                <div className="p-2 bg-[#F8FAFC] rounded">
                  <span className="text-[10px] text-[#556B82] block">GHG Int. / Margin</span>
                  <span className="text-[9px] text-[#899AA8]">in tCO2e/USD</span>
                  <span className="text-xl font-bold text-[#1C2B36] block mt-1">+15</span>
                  <span className="text-[10px] text-[#DC2626] font-semibold">+3% Δ Prev</span>
                </div>

                <div className="p-2 bg-[#F8FAFC] rounded">
                  <span className="text-[10px] text-[#556B82] block">GHG Int. / Revenue</span>
                  <span className="text-[9px] text-[#899AA8]">in tCO2e/USD</span>
                  <span className="text-xl font-bold text-[#1C2B36] block mt-1">+14</span>
                  <span className="text-[10px] text-[#DC2626] font-semibold">+4% Δ Prev</span>
                </div>
              </div>
            </div>

            {/* Finance KPIs (5 cols) */}
            <div className="lg:col-span-5 bg-white rounded-xl border border-[#E2E8F0] shadow-xs p-4 flex flex-col justify-between">
              <h4 className="font-bold text-[#1C2B36] text-xs mb-3">Finance KPIs</h4>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-2 bg-[#F8FAFC] rounded">
                  <span className="text-[10px] text-[#556B82] block">Operating Income</span>
                  <span className="text-[9px] text-[#899AA8]">in m USD</span>
                  <span className="text-xl font-bold text-[#1C2B36] block mt-1">-152</span>
                  <span className="text-[10px] text-[#16A34A] font-semibold">+4% Δ Prev</span>
                </div>

                <div className="p-2 bg-[#F8FAFC] rounded">
                  <span className="text-[10px] text-[#556B82] block">Gross Margin</span>
                  <span className="text-[9px] text-[#899AA8]">in k USD</span>
                  <span className="text-xl font-bold text-[#1C2B36] block mt-1">-3,278</span>
                  <span className="text-[10px] text-[#16A34A] font-semibold">+21% Δ Prev</span>
                </div>

                <div className="p-2 bg-[#F8FAFC] rounded">
                  <span className="text-[10px] text-[#556B82] block">Net Revenue</span>
                  <span className="text-[9px] text-[#899AA8]">in k USD</span>
                  <span className="text-xl font-bold text-[#1C2B36] block mt-1">177</span>
                  <span className="text-[10px] text-[#DC2626] font-semibold">-75% Δ Prev</span>
                </div>
              </div>
            </div>
          </div>

          {/* Middle Row: KPIs Related to All GHG Scopes & Scope 1/2 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* All GHG Scopes Donut Charts */}
            <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-xs p-4">
              <h4 className="font-bold text-[#1C2B36] text-xs mb-3">KPIs Related to All GHG Scopes</h4>
              <div className="grid grid-cols-2 gap-4 items-center">
                {/* Donut 1: Data Quality */}
                <div className="flex flex-col items-center text-center">
                  <span className="text-[11px] font-semibold text-[#556B82] mb-2">Data Quality Characteristic</span>
                  <div className="w-28 h-28 relative flex items-center justify-center">
                    <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                      {/* Secondary Proxy 76% (Blue) */}
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#0070F2" strokeWidth="6" strokeDasharray="76 100" strokeDashoffset="0" />
                      {/* Secondary Industry Avg 21% (Orange) */}
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#F97316" strokeWidth="6" strokeDasharray="21 100" strokeDashoffset="-76" />
                      {/* Primary Measured 3% (Green) */}
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#16A34A" strokeWidth="6" strokeDasharray="3 100" strokeDashoffset="-97" />
                    </svg>
                    <span className="absolute text-[10px] font-bold text-[#1C2B36]">76% Proxy</span>
                  </div>
                  <div className="text-[9px] text-[#556B82] flex flex-col gap-0.5 mt-2 text-left">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#16A34A] rounded-xs" /> Primary Measured (3%)</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#F97316] rounded-xs" /> Secondary Industry Avg (21%)</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#0070F2] rounded-xs" /> Secondary Proxy Data (76%)</span>
                  </div>
                </div>

                {/* Pie 2: Mode of Transport */}
                <div className="flex flex-col items-center text-center">
                  <span className="text-[11px] font-semibold text-[#556B82] mb-2">Mode of Transport</span>
                  <div className="w-28 h-28 relative flex items-center justify-center">
                    <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                      {/* Road 58% (Blue) */}
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#2563EB" strokeWidth="6" strokeDasharray="58 100" strokeDashoffset="0" />
                      {/* Inland 24% (Amber) */}
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#D97706" strokeWidth="6" strokeDasharray="24 100" strokeDashoffset="-58" />
                      {/* Sea 14% (Teal) */}
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#0D9488" strokeWidth="6" strokeDasharray="14 100" strokeDashoffset="-82" />
                      {/* Pipeline 4% (Purple) */}
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#8B5CF6" strokeWidth="6" strokeDasharray="4 100" strokeDashoffset="-96" />
                    </svg>
                    <span className="absolute text-[10px] font-bold text-[#1C2B36]">58% Road</span>
                  </div>
                  <div className="text-[9px] text-[#556B82] flex flex-col gap-0.5 mt-2 text-left">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#2563EB] rounded-xs" /> Road (58%)</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#D97706] rounded-xs" /> Inland waterway (24%)</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#0D9488] rounded-xs" /> Sea (14%)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Scope 1 & 2 Energy Split */}
            <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-xs p-4">
              <h4 className="font-bold text-[#1C2B36] text-xs mb-3">KPIs Related to GHG Scope 1 and GHG Scope 2</h4>
              <div className="grid grid-cols-3 gap-3 items-center text-center">
                {/* Energy Classification (Steam 49%, Heat 51%) */}
                <div className="flex flex-col items-center">
                  <span className="text-[10px] font-semibold text-[#556B82] mb-1">Energy Classification</span>
                  <div className="w-20 h-20 relative flex items-center justify-center">
                    <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#F97316" strokeWidth="6" strokeDasharray="49 100" strokeDashoffset="0" />
                      <circle cx="18" cy="18" r="14" fill="transparent" stroke="#0070F2" strokeWidth="6" strokeDasharray="51 100" strokeDashoffset="-49" />
                    </svg>
                    <span className="absolute text-[8px] font-bold text-[#1C2B36]">51% Heat</span>
                  </div>
                  <span className="text-[9px] text-[#556B82] mt-1">Steam 49% • Heat 51%</span>
                </div>

                {/* Sourcing Type 100% */}
                <div className="flex flex-col items-center">
                  <span className="text-[10px] font-semibold text-[#556B82] mb-1">Energy Sourcing</span>
                  <div className="w-20 h-20 relative flex items-center justify-center">
                    <div className="w-16 h-16 rounded-full bg-[#0070F2] flex items-center justify-center text-white font-bold text-[10px]">
                      100%
                    </div>
                  </div>
                  <span className="text-[9px] text-[#556B82] mt-1">Grid Standard</span>
                </div>

                {/* Energy Mix 100% */}
                <div className="flex flex-col items-center">
                  <span className="text-[10px] font-semibold text-[#556B82] mb-1">Energy Mix</span>
                  <div className="w-20 h-20 relative flex items-center justify-center">
                    <div className="w-16 h-16 rounded-full bg-[#0070F2] flex items-center justify-center text-white font-bold text-[10px]">
                      100%
                    </div>
                  </div>
                  <span className="text-[9px] text-[#556B82] mt-1">National Mix</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Row: CO2e Breakdown by GHG Scopes and GHG Categories */}
          <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-xs p-4">
            <h4 className="font-bold text-[#1C2B36] text-xs mb-3">CO2e Breakdown by GHG Scopes and GHG Categories</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              {/* Scope 1 */}
              <div className="p-3 bg-[#F8FAFC] rounded-lg flex flex-col items-center text-center">
                <span className="font-bold text-[#1C2B36] mb-1">Scope 1 – Direct emissions</span>
                <span className="text-[9px] text-[#899AA8]">in tCO2e</span>
                <div className="w-24 h-24 relative flex items-center justify-center my-2">
                  <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                    <circle cx="18" cy="18" r="14" fill="transparent" stroke="#86198F" strokeWidth="6" strokeDasharray="51 100" strokeDashoffset="0" />
                    <circle cx="18" cy="18" r="14" fill="transparent" stroke="#C026D3" strokeWidth="6" strokeDasharray="49 100" strokeDashoffset="-51" />
                  </svg>
                  <span className="absolute text-[9px] font-bold text-[#1C2B36]">51% Stat</span>
                </div>
                <div className="text-[9px] text-[#556B82] flex flex-col gap-0.5 text-left w-full">
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#86198F] rounded-xs" /> Stationary Combustion (51%)</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#C026D3] rounded-xs" /> Mobile Combustion (49%)</span>
                </div>
              </div>

              {/* Scope 2 */}
              <div className="p-3 bg-[#F8FAFC] rounded-lg flex flex-col items-center text-center justify-center min-h-[180px]">
                <span className="font-bold text-[#1C2B36] mb-1">Scope 2 – Purchased energy</span>
                <span className="text-[9px] text-[#899AA8]">in tCO2e</span>
                <div className="w-16 h-16 rounded-full bg-[#E2E8F0] my-3" />
                <span className="text-[10px] text-[#899AA8]">No location-specific deviations</span>
              </div>

              {/* Scope 3 */}
              <div className="p-3 bg-[#F8FAFC] rounded-lg flex flex-col items-center text-center">
                <span className="font-bold text-[#1C2B36] mb-1">Scope 3 – Indirect value chain</span>
                <span className="text-[9px] text-[#899AA8]">in tCO2e</span>
                <div className="w-24 h-24 relative flex items-center justify-center my-2">
                  <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                    <circle cx="18" cy="18" r="14" fill="transparent" stroke="#0070F2" strokeWidth="6" strokeDasharray="62 100" strokeDashoffset="0" />
                    <circle cx="18" cy="18" r="14" fill="transparent" stroke="#16A34A" strokeWidth="6" strokeDasharray="23 100" strokeDashoffset="-62" />
                    <circle cx="18" cy="18" r="14" fill="transparent" stroke="#06B6D4" strokeWidth="6" strokeDasharray="15 100" strokeDashoffset="-85" />
                  </svg>
                  <span className="absolute text-[9px] font-bold text-[#1C2B36]">62% Franch</span>
                </div>
                <div className="text-[9px] text-[#556B82] flex flex-col gap-0.5 text-left w-full">
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#0070F2] rounded-xs" /> Scope 3.14 - Franchises (62%)</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#16A34A] rounded-xs" /> Scope 3.5 - Waste Operations (23%)</span>
                  <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[#06B6D4] rounded-xs" /> Scope 3.8 - Leased Assets (15%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
