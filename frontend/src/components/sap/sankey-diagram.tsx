"use client";

import React, { useState } from "react";

export interface SankeyData {
  totalEmissions: string;
  unit: string;
  scope1: { label: string; value: string; categories: { name: string; value: string }[] };
  scope2: { label: string; value: string; categories: { name: string; value: string }[] };
  scope3: { label: string; value: string; categories: { name: string; value: string }[] };
  products: { name: string; value: string }[];
  nonProduct: string;
}

const DEFAULT_SANKEY: SankeyData = {
  totalEmissions: "72.82",
  unit: "Ton",
  scope1: {
    label: "Scope 1 - Direct Emis...",
    value: "3.44",
    categories: [{ name: "Stationary Combustion", value: "3.44" }],
  },
  scope2: {
    label: "Scope 2 - Purchased ...",
    value: "6.60",
    categories: [{ name: "Purchased Electricity", value: "6.60" }],
  },
  scope3: {
    label: "Scope 3 - Indirect Val...",
    value: "62.78",
    categories: [
      { name: "3.1 – Purchased Good...", value: "49.86" },
      { name: "3.2 – Capital Goods", value: "2.84" },
      { name: "3.3 – Fuel- and Energy...", value: "2.53" },
      { name: "3.6 – Business Travel", value: "1.92" },
      { name: "Scope 3 – Others", value: "5.63" },
    ],
  },
  products: [
    { name: "VeganBar", value: "21.77" },
    { name: "SunnyBar", value: "44.01" },
  ],
  nonProduct: "7.04",
};

interface SankeyDiagramProps {
  data?: SankeyData;
}

export function SankeyDiagram({ data = DEFAULT_SANKEY }: SankeyDiagramProps) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Layout coordinate constants
  // Width: 1050, Height: 440
  // Columns:
  // Col 0: Categories (x: 50 - 150)
  // Col 1: Scopes (x: 250 - 350)
  // Col 2: Center Pillar: Total Emissions (x: 480 - 520)
  // Col 3: Product Subcategories (x: 640 - 740)
  // Col 4: Final Products (x: 850 - 930)

  // Node Positions Y
  const leftNodes = [
    { id: "stat_comb", label: "Stationary Combustion", value: `${data.scope1.categories[0]?.value || "3.44"} Ton`, y: 40, color: "#2563EB", scope: "s1" },
    { id: "purch_elec", label: "Purchased Electricity", value: `${data.scope2.categories[0]?.value || "6.60"} Ton`, y: 105, color: "#D97706", scope: "s2" },
    { id: "s3_1", label: data.scope3.categories[0]?.name || "3.1 – Purchased Good...", value: `${data.scope3.categories[0]?.value || "49.86"} Ton`, y: 175, color: "#65A30D", scope: "s3", height: 50 },
    { id: "s3_2", label: data.scope3.categories[1]?.name || "3.2 – Capital Goods", value: `${data.scope3.categories[1]?.value || "2.84"} Ton`, y: 245, color: "#65A30D", scope: "s3" },
    { id: "s3_3", label: data.scope3.categories[2]?.name || "3.3 – Fuel- and Energy...", value: `${data.scope3.categories[2]?.value || "2.53"} Ton`, y: 295, color: "#65A30D", scope: "s3" },
    { id: "s3_6", label: data.scope3.categories[3]?.name || "3.6 – Business Travel", value: `${data.scope3.categories[3]?.value || "1.92"} Ton`, y: 345, color: "#65A30D", scope: "s3" },
    { id: "s3_oth", label: data.scope3.categories[4]?.name || "Scope 3 – Others", value: `${data.scope3.categories[4]?.value || "5.63"} Ton`, y: 395, color: "#65A30D", scope: "s3" },
  ];

  const scopeNodes = [
    { id: "s1", label: data.scope1.label, value: `${data.scope1.value} Ton`, y: 140, color: "#2563EB", strokeWidth: 8 },
    { id: "s2", label: data.scope2.label, value: `${data.scope2.value} Ton`, y: 210, color: "#D97706", strokeWidth: 14 },
    { id: "s3", label: data.scope3.label, value: `${data.scope3.value} Ton`, y: 290, color: "#65A30D", strokeWidth: 80 },
  ];

  const rightNodes = [
    { id: "sold_prod", label: "Sold Products", value: "65.78 Ton", y: 180, color: "#C026D3", strokeWidth: 65 },
    { id: "closing_inv", label: "Closing: Product Inve...", value: "0.00 Ton", y: 265, color: "#C026D3", strokeWidth: 4 },
    { id: "non_prod", label: "Non-Product Emissions", value: `${data.nonProduct} Ton`, y: 330, color: "#9E9E9E", strokeWidth: 15 },
  ];

  const productNodes = [
    { id: "prod_1", label: data.products[0]?.name || "VeganBar", value: `${data.products[0]?.value || "21.77"} Ton`, y: 200, color: "#C026D3", strokeWidth: 28 },
    { id: "prod_2", label: data.products[1]?.name || "SunnyBar", value: `${data.products[1]?.value || "44.01"} Ton`, y: 260, color: "#C026D3", strokeWidth: 40 },
  ];

  return (
    <div className="w-full bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-4 overflow-x-auto select-none">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-[#1C2B36]">
          Corporate CO2e Balance
        </h3>
        <div className="flex items-center gap-2 text-xs text-[#556B82]">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#2563EB]" /> Scope 1
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#D97706]" /> Scope 2
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#65A30D]" /> Scope 3
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#C026D3]" /> Product Outflow
          </span>
        </div>
      </div>

      <div className="min-w-[1000px] h-[450px] relative">
        <svg className="w-full h-full" viewBox="0 0 1020 440">
          {/* Defs for Flow Gradients */}
          <defs>
            <linearGradient id="grad-s1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#2563EB" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#2563EB" stopOpacity="0.85" />
            </linearGradient>
            <linearGradient id="grad-s2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#D97706" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#D97706" stopOpacity="0.85" />
            </linearGradient>
            <linearGradient id="grad-s3" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#65A30D" stopOpacity="0.85" />
              <stop offset="100%" stopColor="#65A30D" stopOpacity="0.9" />
            </linearGradient>
            <linearGradient id="grad-magenta" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#C026D3" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#A21CAF" stopOpacity="0.95" />
            </linearGradient>
          </defs>

          {/* Flow 1: Stationary Combustion -> Scope 1 */}
          <path
            d="M 145 40 C 200 40, 200 140, 250 140"
            fill="none"
            stroke="url(#grad-s1)"
            strokeWidth="6"
            strokeLinecap="round"
          />

          {/* Flow 2: Purchased Electricity -> Scope 2 */}
          <path
            d="M 145 105 C 200 105, 200 210, 250 210"
            fill="none"
            stroke="url(#grad-s2)"
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Flow 3: 3.1 Purchased Goods -> Scope 3 (Thick Ribbon) */}
          <path
            d="M 145 185 C 200 185, 200 280, 250 280"
            fill="none"
            stroke="url(#grad-s3)"
            strokeWidth="50"
          />

          {/* Flow 4-7: Other Scope 3 Categories -> Scope 3 */}
          <path
            d="M 145 245 C 200 245, 210 295, 250 295"
            fill="none"
            stroke="#65A30D"
            strokeWidth="8"
            opacity="0.85"
          />
          <path
            d="M 145 295 C 200 295, 215 310, 250 310"
            fill="none"
            stroke="#65A30D"
            strokeWidth="6"
            opacity="0.85"
          />
          <path
            d="M 145 345 C 190 345, 215 320, 250 320"
            fill="none"
            stroke="#65A30D"
            strokeWidth="5"
            opacity="0.85"
          />
          <path
            d="M 145 395 C 190 395, 215 330, 250 330"
            fill="none"
            stroke="#65A30D"
            strokeWidth="10"
            opacity="0.85"
          />

          {/* Scope 1 -> Total Pillar */}
          <path
            d="M 345 140 C 400 140, 420 230, 490 230"
            fill="none"
            stroke="#2563EB"
            strokeWidth="6"
          />

          {/* Scope 2 -> Total Pillar */}
          <path
            d="M 345 210 C 400 210, 430 235, 490 235"
            fill="none"
            stroke="#D97706"
            strokeWidth="10"
          />

          {/* Scope 3 -> Total Pillar (Massive ribbon) */}
          <path
            d="M 345 300 C 410 300, 440 260, 490 260"
            fill="none"
            stroke="url(#grad-s3)"
            strokeWidth="65"
          />

          {/* Center Pillar: Total Emissions Bar */}
          <rect
            x="490"
            y="215"
            width="12"
            height="110"
            fill="#0F766E"
            rx="2"
          />

          {/* Total Pillar -> Sold Products (Magenta Ribbon) */}
          <path
            d="M 502 245 C 550 245, 590 195, 645 195"
            fill="none"
            stroke="url(#grad-magenta)"
            strokeWidth="65"
          />

          {/* Total Pillar -> Closing Inventory */}
          <path
            d="M 502 280 C 560 280, 590 270, 645 270"
            fill="none"
            stroke="#C026D3"
            strokeWidth="4"
          />

          {/* Total Pillar -> Non-Product Emissions */}
          <path
            d="M 502 300 C 550 300, 590 335, 645 335"
            fill="none"
            stroke="#78716C"
            strokeWidth="12"
          />

          {/* Sold Products -> VeganBar & SunnyBar */}
          <path
            d="M 740 185 C 790 185, 800 205, 845 205"
            fill="none"
            stroke="url(#grad-magenta)"
            strokeWidth="28"
          />
          <path
            d="M 740 215 C 790 215, 800 265, 845 265"
            fill="none"
            stroke="url(#grad-magenta)"
            strokeWidth="40"
          />

          {/* Node Cards (HTML-like SVG ForeignObjects for exact styling matching Image 1) */}
          {/* Left Category Nodes */}
          {leftNodes.map((n) => (
            <foreignObject
              key={n.id}
              x={45}
              y={n.y - 18}
              width={100}
              height={38}
            >
              <div className="bg-white border border-[#CBD5E1] rounded shadow-xs p-1 text-center hover:border-[#0070F2] transition-colors cursor-pointer">
                <div className="text-[10px] font-medium text-[#1C2B36] truncate leading-tight">
                  {n.label}
                </div>
                <div className="text-[9px] font-bold text-[#556B82]">
                  {n.value}
                </div>
              </div>
            </foreignObject>
          ))}

          {/* Middle Scope Nodes */}
          {scopeNodes.map((s) => (
            <foreignObject
              key={s.id}
              x={250}
              y={s.y - 18}
              width={95}
              height={38}
            >
              <div className="bg-white border border-[#CBD5E1] rounded shadow-xs p-1 text-center hover:border-[#0070F2] transition-colors cursor-pointer">
                <div className="text-[10px] font-medium text-[#1C2B36] truncate leading-tight">
                  {s.label}
                </div>
                <div className="text-[9px] font-bold text-[#556B82]">
                  {s.value}
                </div>
              </div>
            </foreignObject>
          ))}

          {/* Center Pillar Badge */}
          <foreignObject x={450} y={175} width={90} height={36}>
            <div className="bg-white border border-[#0F766E] rounded shadow-sm p-1 text-center">
              <div className="text-[10px] font-bold text-[#0F766E] leading-tight">
                Total Emissions
              </div>
              <div className="text-[9px] font-extrabold text-[#1C2B36]">
                {data.totalEmissions} {data.unit}
              </div>
            </div>
          </foreignObject>

          {/* Right Subcategory Nodes */}
          {rightNodes.map((r) => (
            <foreignObject
              key={r.id}
              x={645}
              y={r.y - 18}
              width={95}
              height={38}
            >
              <div className="bg-white border border-[#CBD5E1] rounded shadow-xs p-1 text-center hover:border-[#C026D3] transition-colors cursor-pointer">
                <div className="text-[10px] font-medium text-[#1C2B36] truncate leading-tight">
                  {r.label}
                </div>
                <div className="text-[9px] font-bold text-[#556B82]">
                  {r.value}
                </div>
              </div>
            </foreignObject>
          ))}

          {/* Final Products Nodes */}
          {productNodes.map((p) => (
            <foreignObject
              key={p.id}
              x={845}
              y={p.y - 16}
              width={80}
              height={34}
            >
              <div className="bg-white/90 rounded p-1 text-left">
                <div className="text-[10px] font-semibold text-[#86198F] leading-tight">
                  {p.label}
                </div>
                <div className="text-[9px] text-[#556B82]">
                  {p.value}
                </div>
              </div>
            </foreignObject>
          ))}
        </svg>
      </div>
    </div>
  );
}
