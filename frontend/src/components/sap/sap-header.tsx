"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ChevronDown,
  Search,
  Headphones,
  MessageSquare,
  HelpCircle,
  Play,
  Upload,
  ArrowLeft,
  X,
  CheckCircle2,
} from "lucide-react";

export type SapAppId =
  | "corporate-balance"
  | "process-inbounds"
  | "analyze-esg"
  | "product-emissions"
  | "sac-stories"
  | "scenario-simulator";

interface SapHeaderProps {
  activeApp: SapAppId;
  onSelectApp: (app: SapAppId) => void;
  onTriggerDemo?: () => void;
  onOpenUpload?: () => void;
  isExecuting?: boolean;
  isGeminiActive?: boolean;
  onOpenGeminiConfig?: () => void;
}

const APPS: { id: SapAppId; title: string; subtitle: string }[] = [
  {
    id: "corporate-balance",
    title: "Corporate Balance",
    subtitle: "Sankey Flow Diagram & CO2e Balance Table (SAP SFM)",
  },
  {
    id: "process-inbounds",
    title: "Process Inbounds",
    subtitle: "Supplier Activity Inbound Management & Inspector",
  },
  {
    id: "analyze-esg",
    title: "Analyze ESG Data",
    subtitle: "Target-Driven KPI Tiles & Emissions Benchmark",
  },
  {
    id: "product-emissions",
    title: "Manage Product Emissions",
    subtitle: "Product Footprints & EU CBAM Quarterly Declarations",
  },
  {
    id: "sac-stories",
    title: "GHG Emissions Overview",
    subtitle: "SAP Analytics Cloud (SAC) Combined Finance & GHG Story",
  },
  {
    id: "scenario-simulator",
    title: "Scenario Simulator",
    subtitle: "What-If Capital Allocations, MACC & Decarbonization Sandbox",
  },
];

export function SapHeader({
  activeApp,
  onSelectApp,
  onTriggerDemo,
  onOpenUpload,
  isExecuting = false,
  isGeminiActive = false,
  onOpenGeminiConfig,
}: SapHeaderProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const currentApp = APPS.find((a) => a.id === activeApp) || APPS[0];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-[#E2E8F0] shadow-sm select-none">
      {/* Primary Top Bar */}
      <div className="h-12 px-4 flex items-center justify-between gap-4">
        {/* Left: Back + SAP Brand + App Title Dropdown */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="w-7 h-7 flex items-center justify-center text-[#556B82] hover:bg-[#F1F5F9] rounded"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>

          {/* SAP Brand Icon */}
          <div className="flex items-center gap-2">
            <div className="px-2 py-0.5 bg-[#0070F2] text-white font-bold text-xs rounded tracking-wider shadow-sm flex items-center justify-center">
              SAP
            </div>
          </div>

          {/* App Switcher Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-1 text-sm font-semibold text-[#1C2B36] hover:bg-[#F1F5F9] px-2 py-1 rounded transition-colors"
            >
              <span>{currentApp.title}</span>
              <ChevronDown className="w-3.5 h-3.5 text-[#556B82]" />
            </button>

            {dropdownOpen && (
              <div className="absolute left-0 top-full mt-1 w-80 bg-white rounded-lg shadow-xl border border-[#CBD5E1] py-1.5 z-50 animate-in fade-in slide-in-from-top-1">
                <div className="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#899AA8] border-b border-[#F1F5F9]">
                  SAP Sustainability Footprint Management
                </div>
                {APPS.map((app) => (
                  <button
                    key={app.id}
                    type="button"
                    onClick={() => {
                      onSelectApp(app.id);
                      setDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex flex-col hover:bg-[#F8FAFC] transition-colors ${
                      activeApp === app.id
                        ? "bg-[#EBF3FF] text-[#0070F2] font-semibold border-l-4 border-[#0070F2]"
                        : "text-[#1C2B36]"
                    }`}
                  >
                    <span className="font-medium text-sm">{app.title}</span>
                    <span className="text-[11px] text-[#556B82] mt-0.5">
                      {app.subtitle}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Center: Global Search Bar */}
        <div className="hidden md:flex items-center flex-1 max-w-md mx-4">
          <div className="relative w-full">
            <input
              type="text"
              readOnly
              value='Search in: "Apps"'
              className="w-full bg-[#F5F6F8] hover:bg-[#EEF2F6] border border-[#E2E8F0] rounded-full py-1.5 pl-4 pr-9 text-xs text-[#556B82] cursor-pointer"
            />
            <Search className="w-3.5 h-3.5 text-[#556B82] absolute right-3 top-2.5" />
          </div>
        </div>

        {/* Right: Quick Action Buttons & Profile Icons */}
        <div className="flex items-center gap-2 text-[#556B82]">
          {/* Quick Demo Trigger */}
          {onTriggerDemo && (
            <button
              type="button"
              onClick={onTriggerDemo}
              disabled={isExecuting}
              className="flex items-center gap-1.5 px-3 py-1 bg-[#0070F2] hover:bg-[#0057D2] text-white text-xs font-semibold rounded shadow-sm transition-colors disabled:opacity-50"
            >
              <Play className="w-3 h-3 fill-current" />
              <span>{isExecuting ? "Calculating..." : "Run Demo"}</span>
            </button>
          )}

          {/* Upload CSV trigger */}
          {onOpenUpload && (
            <button
              type="button"
              onClick={onOpenUpload}
              className="flex items-center gap-1.5 px-3 py-1 bg-white hover:bg-[#F8FAFC] border border-[#CBD5E1] text-[#1C2B36] text-xs font-semibold rounded shadow-sm transition-colors"
            >
              <Upload className="w-3 h-3 text-[#0070F2]" />
              <span>Upload CSV</span>
            </button>
          )}

          <div className="h-4 w-[1px] bg-[#E2E8F0] mx-1" />

          <button
            type="button"
            className="w-8 h-8 flex items-center justify-center hover:bg-[#F1F5F9] rounded-full text-[#556B82]"
            title="Support"
          >
            <Headphones className="w-4 h-4" />
          </button>
          <button
            type="button"
            className="w-8 h-8 flex items-center justify-center hover:bg-[#F1F5F9] rounded-full text-[#556B82]"
            title="Feedback"
          >
            <MessageSquare className="w-4 h-4" />
          </button>
          <button
            type="button"
            className="w-8 h-8 flex items-center justify-center hover:bg-[#F1F5F9] rounded-full text-[#556B82]"
            title="Help"
          >
            <HelpCircle className="w-4 h-4" />
          </button>

          {/* User Profile Avatar Avatar Pill (NW / TS / SJ) */}
          <div className="w-7 h-7 rounded-full bg-[#EBF3FF] border border-[#0070F2]/40 text-[#0070F2] text-xs font-bold flex items-center justify-center ml-1 shadow-sm">
            NW
          </div>
        </div>
      </div>

      {/* Standard* View Bar (matching Images 1 & 3) */}
      <div className="h-8 px-6 bg-[#FAFBFC] border-t border-[#F1F5F9] flex items-center justify-between text-xs text-[#556B82]">
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="flex items-center gap-1 text-[#0070F2] font-semibold hover:underline"
          >
            <span>Standard*</span>
            <ChevronDown className="w-3 h-3 text-[#0070F2]" />
          </button>
          <span className="text-[#CBD5E1]">|</span>
          <span className="text-[#899AA8] text-[11px]">
            Fiscal Period: 2024 / 2025 • Currency: USD / EGP
          </span>
        </div>

        <div className="flex items-center gap-3 text-[11px] text-[#556B82]">
          <button
            type="button"
            onClick={onOpenGeminiConfig}
            className="flex items-center gap-1.5 hover:bg-[#EEF2F6] px-2 py-0.5 rounded transition-colors cursor-pointer"
            title="Configure Google Gemini API Key & Model"
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isGeminiActive ? "bg-[#16A34A] animate-pulse" : "bg-[#D97706]"
              }`}
            />
            <span
              className={`font-semibold ${
                isGeminiActive ? "text-[#16A34A]" : "text-[#D97706]"
              }`}
            >
              {isGeminiActive ? "Gemini 2.5 Flash Active" : "Gemini AI (Configure API Key)"}
            </span>
          </button>
          <span>•</span>
          <span>ISO 14064-3 Cleanroom</span>
        </div>
      </div>
    </header>
  );
}
