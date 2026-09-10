"use client";

import React, { useState } from "react";
import { SankeyDiagram, SankeyData } from "../sankey-diagram";
import { Search, SlidersHorizontal, Settings, Download, ChevronRight, ChevronDown } from "lucide-react";
import { RunSummaryResponse, ActivityDTO } from "@/lib/types";

interface BalanceItem {
  id: string;
  item: string;
  subtype: string;
  subcategory: string;
  plant: string;
  type: string;
  totalCO2e: string;
}

const DEFAULT_ITEMS: BalanceItem[] = [
  {
    id: "1",
    item: "Cocoa (C001/1010/SUP01)",
    subtype: "Scope 3 – Indirect Value Chain Emissions",
    subcategory: "3.1 – Purchased Goods and Services",
    plant: "ChocoMagic HQ",
    type: "Product",
    totalCO2e: "17.64000 Ton",
  },
  {
    id: "2",
    item: "Cocoa (C001/1010/SUP02)",
    subtype: "Scope 3 – Indirect Value Chain Emissions",
    subcategory: "3.1 – Purchased Goods and Services",
    plant: "ChocoMagic HQ",
    type: "Product",
    totalCO2e: "10.10000 Ton",
  },
  {
    id: "3",
    item: "Packaging (C004/1010/SUP07)",
    subtype: "Scope 3 – Indirect Value Chain Emissions",
    subcategory: "3.1 – Purchased Goods and Services",
    plant: "ChocoMagic HQ",
    type: "Product",
    totalCO2e: "6.72000 Ton",
  },
  {
    id: "4",
    item: "Electricity (Electricity)",
    subtype: "Scope 2 – Purchased Energy",
    subcategory: "Purchased Electricity",
    plant: "ChocoMagic HQ",
    type: "Energy Source",
    totalCO2e: "6.60118 Ton",
  },
  {
    id: "5",
    item: "Packaging (C004/1010/SUP08)",
    subtype: "Scope 3 – Indirect Value Chain Emissions",
    subcategory: "3.1 – Purchased Goods and Services",
    plant: "ChocoMagic HQ",
    type: "Product",
    totalCO2e: "5.60000 Ton",
  },
  {
    id: "6",
    item: "Natural Gas (Boiler #1)",
    subtype: "Scope 1 – Direct Emissions",
    subcategory: "Stationary Combustion",
    plant: "ChocoMagic HQ",
    type: "Energy Source",
    totalCO2e: "3.44000 Ton",
  },
  {
    id: "7",
    item: "Machinery Assets (CAP-02)",
    subtype: "Scope 3 – Indirect Value Chain Emissions",
    subcategory: "3.2 – Capital Goods",
    plant: "ChocoMagic HQ",
    type: "Capital Asset",
    totalCO2e: "2.84000 Ton",
  },
  {
    id: "8",
    item: "Upstream Grid Transmission",
    subtype: "Scope 3 – Indirect Value Chain Emissions",
    subcategory: "3.3 – Fuel- and Energy-Related",
    plant: "ChocoMagic HQ",
    type: "Transmission",
    totalCO2e: "2.53000 Ton",
  },
];

interface CorporateBalanceViewProps {
  summary?: RunSummaryResponse | null;
  activities?: ActivityDTO[];
}

export function CorporateBalanceView({ summary, activities }: CorporateBalanceViewProps) {
  const [searchTerm, setSearchTerm] = useState("");

  // Dynamically map backend summary to Sankey if available
  let sankeyData: SankeyData | undefined;
  if (summary) {
    sankeyData = {
      totalEmissions: summary.total_emissions,
      unit: summary.emissions_unit,
      scope1: {
        label: "Scope 1 - Direct Emis...",
        value: summary.scope_totals["Scope 1"] || "0",
        categories: [{ name: "Stationary Combustion", value: summary.scope_totals["Scope 1"] || "0" }],
      },
      scope2: {
        label: "Scope 2 - Purchased ...",
        value: summary.scope_totals["Scope 2"] || "0",
        categories: [{ name: "Purchased Electricity", value: summary.scope_totals["Scope 2"] || "0" }],
      },
      scope3: {
        label: "Scope 3 - Indirect Val...",
        value: summary.scope_totals["Scope 3"] || "0",
        categories: [
          { name: "3.1 – Purchased Goods", value: summary.scope_totals["Scope 3"] || "0" },
          { name: "3.2 – Capital Goods", value: "0" },
          { name: "3.3 – Fuel-Related", value: "0" },
          { name: "3.6 – Business Travel", value: "0" },
          { name: "Scope 3 – Others", value: "0" },
        ],
      },
      products: [
        { name: "Product Billet A", value: (parseFloat(summary.total_emissions) * 0.4).toFixed(2) },
        { name: "Product Billet B", value: (parseFloat(summary.total_emissions) * 0.5).toFixed(2) },
      ],
      nonProduct: (parseFloat(summary.total_emissions) * 0.1).toFixed(2),
    };
  }

  // Display items
  const items = activities && activities.length > 0
    ? activities.map((a, i) => ({
        id: a.activity_id || String(i),
        item: a.description || a.activity_type || `Item #${i + 1}`,
        subtype: a.scope ? `${a.scope} Emissions` : "Scope 3",
        subcategory: a.category || "General Activity",
        plant: "Ain Sokhna Facility",
        type: a.unit?.toLowerCase().includes("kwh") || a.unit?.toLowerCase().includes("mwh") ? "Energy Source" : "Product",
        totalCO2e: `${a.quantity || "—"} ${summary?.emissions_unit || "Ton"}`,
      }))
    : DEFAULT_ITEMS;

  const filteredItems = items.filter((it) =>
    it.item.toLowerCase().includes(searchTerm.toLowerCase()) ||
    it.subtype.toLowerCase().includes(searchTerm.toLowerCase()) ||
    it.subcategory.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto w-full p-6 select-none">
      {/* 1. Sankey Flow Diagram Card */}
      <SankeyDiagram data={sankeyData} />

      {/* 2. Corporate CO2e Balance Table Card */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden">
        {/* Table Header Controls */}
        <div className="px-5 py-3.5 border-b border-[#E2E8F0] flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#FAFBFC]">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-[#1C2B36]">
              Corporate CO2e Balance ({filteredItems.length})
            </h3>
          </div>

          <div className="flex items-center gap-2 text-xs text-[#556B82]">
            {/* Search Input */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search table..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-white border border-[#CBD5E1] rounded-md py-1 pl-7 pr-2 text-xs text-[#1C2B36] focus:outline-none focus:border-[#0070F2]"
              />
              <Search className="w-3.5 h-3.5 text-[#899AA8] absolute left-2 top-2" />
            </div>

            <button
              type="button"
              className="p-1.5 hover:bg-[#F1F5F9] rounded text-[#556B82] border border-[#CBD5E1]"
              title="Filters"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
            </button>

            <button
              type="button"
              className="p-1.5 hover:bg-[#F1F5F9] rounded text-[#556B82] border border-[#CBD5E1]"
              title="Settings"
            >
              <Settings className="w-3.5 h-3.5" />
            </button>

            <button
              type="button"
              onClick={() => {
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(filteredItems, null, 2));
                const a = document.createElement("a");
                a.href = dataStr;
                a.download = "corporate-balance.json";
                a.click();
              }}
              className="p-1.5 hover:bg-[#F1F5F9] rounded text-[#556B82] border border-[#CBD5E1]"
              title="Export"
            >
              <Download className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC] text-[#556B82] font-semibold">
                <th className="py-2.5 px-4">Item</th>
                <th className="py-2.5 px-4">Item Subtype</th>
                <th className="py-2.5 px-4">Item Subcategory</th>
                <th className="py-2.5 px-4">Plant</th>
                <th className="py-2.5 px-4">Item Type</th>
                <th className="py-2.5 px-4 text-right">Total CO2e</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9]">
              {filteredItems.map((row) => (
                <tr
                  key={row.id}
                  className="hover:bg-[#F8FAFC] transition-colors cursor-pointer group"
                >
                  <td className="py-3 px-4 font-medium text-[#0070F2] group-hover:underline">
                    {row.item}
                  </td>
                  <td className="py-3 px-4 text-[#1C2B36]">
                    {row.subtype}
                  </td>
                  <td className="py-3 px-4 text-[#556B82]">
                    {row.subcategory}
                  </td>
                  <td className="py-3 px-4 text-[#556B82]">
                    {row.plant}
                  </td>
                  <td className="py-3 px-4 text-[#556B82]">
                    {row.type}
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-[#1C2B36]">
                    {row.totalCO2e}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
