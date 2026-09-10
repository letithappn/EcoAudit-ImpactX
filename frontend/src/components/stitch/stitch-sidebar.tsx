"use client";

import React from "react";

export type StitchViewId =
  | "executive-overview"
  | "cbam-and-product-footprints"
  | "multi-year-esg-targets"
  | "scope-3-and-suppliers"
  | "carbon-balance-ledger"
  | "decarbonization-simulator";

interface StitchSidebarProps {
  activeView: StitchViewId;
  onSelectView: (view: StitchViewId) => void;
  isGeminiActive?: boolean;
}

interface NavItem {
  id: StitchViewId;
  label: string;
  icon: string;
}

const NAV_ITEMS: NavItem[] = [
  {
    id: "executive-overview",
    label: "Executive Overview",
    icon: "dashboard",
  },
  {
    id: "cbam-and-product-footprints",
    label: "CBAM & Product Footprints",
    icon: "verified",
  },
  {
    id: "multi-year-esg-targets",
    label: "Multi-Year ESG Targets",
    icon: "trending_down",
  },
  {
    id: "scope-3-and-suppliers",
    label: "Scope 3 & Suppliers",
    icon: "local_shipping",
  },
  {
    id: "carbon-balance-ledger",
    label: "Carbon Balance Ledger",
    icon: "account_balance",
  },
  {
    id: "decarbonization-simulator",
    label: "Decarbonization Simulator",
    icon: "tune",
  },
];

export function StitchSidebar({
  activeView,
  onSelectView,
  isGeminiActive = false,
}: StitchSidebarProps) {
  return (
    <aside className="fixed left-0 top-0 h-full w-72 bg-primary-container text-on-primary border-r border-outline-variant/20 z-50 flex flex-col justify-between select-none shadow-[0_1px_8px_rgba(0,0,0,0.08)]">
      <div className="flex flex-col">
        {/* Brand Header */}
        <div className="h-16 px-space-lg flex items-center justify-between border-b border-outline-variant/15">
          <div className="flex items-center gap-space-sm cursor-pointer" onClick={() => onSelectView("executive-overview")}>
            <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center text-white shadow-sm ring-1 ring-white/20">
              <span className="material-symbols-outlined text-[20px]">eco</span>
            </div>
            <span className="font-headline-md text-headline-md font-bold tracking-tight text-on-primary">
              EcoAudit<span className="text-secondary-fixed">AI</span>
            </span>
          </div>
          <span className="px-space-xs py-space-2xs bg-surface-tint/20 text-secondary-fixed font-mono-data text-[10px] rounded uppercase font-semibold tracking-wider">
            v3.4 Audited
          </span>
        </div>

        {/* Section Label */}
        <div className="px-space-lg pt-space-lg pb-space-xs">
          <div className="font-label-sm text-label-sm uppercase tracking-widest text-on-primary-container font-semibold">
            Emission Intelligence
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex flex-col gap-space-2xs px-space-md">
          {NAV_ITEMS.map((item) => {
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectView(item.id)}
                className={`w-full flex items-center gap-space-md px-space-md py-space-sm rounded-lg transition-all group text-left ${
                  isActive
                    ? "bg-secondary text-on-secondary font-semibold shadow-[0_1px_4px_rgba(0,0,0,0.2)]"
                    : "text-inverse-on-surface/80 hover:bg-surface-container-high/15 hover:text-inverse-on-surface font-normal"
                }`}
              >
                <span
                  className={`material-symbols-outlined text-[20px] transition-colors ${
                    isActive
                      ? "text-white"
                      : "text-inverse-on-surface/70 group-hover:text-inverse-on-surface"
                  }`}
                >
                  {item.icon}
                </span>
                <span className="font-label-md text-label-md">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Engine Status Bottom Card */}
      <div className="p-space-md border-t border-outline-variant/15 bg-primary-container/90">
        <div className="p-space-sm bg-surface-container-low/10 rounded-lg border border-outline-variant/20 flex flex-col gap-space-xs">
          <div className="flex items-center justify-between">
            <span className="font-label-sm text-label-sm text-tertiary-fixed font-semibold flex items-center gap-space-2xs">
              <span className="w-2 h-2 rounded-full bg-tertiary-fixed animate-pulse"></span>
              {isGeminiActive ? "Gemini 2.5 Active" : "Engine Active"}
            </span>
            <span className="font-mono-data text-mono-data text-on-primary-container text-[11px]">
              GHG Protocol
            </span>
          </div>
          <p className="font-body-sm text-body-sm text-inverse-on-surface/70 text-[11px] leading-tight">
            Double-entry Scope 1, 2 & 3 Ledger aligned with CBAM Regulation (EU) 2023/956.
          </p>
        </div>
      </div>
    </aside>
  );
}
