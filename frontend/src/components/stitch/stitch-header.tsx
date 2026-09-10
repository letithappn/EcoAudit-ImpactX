"use client";

import React from "react";

interface StitchHeaderProps {
  onOpenUpload: () => void;
  onOpenGeminiConfig?: () => void;
  isGeminiActive?: boolean;
  activeRunId?: string | null;
  facilityLabel?: string;
}

export function StitchHeader({
  onOpenUpload,
  onOpenGeminiConfig,
  isGeminiActive = false,
  activeRunId,
  facilityLabel = "Global Operations (All 14 Facilities) | FY2024 / Q3 CBAM Cycle",
}: StitchHeaderProps) {
  return (
    <header className="fixed top-0 left-72 right-0 h-16 bg-surface-container-lowest/95 backdrop-blur-md z-40 flex items-center justify-between px-space-xl border-b border-outline-variant/30 shadow-[0_1px_3px_rgba(11,28,48,0.04)]">
      {/* Left section: Facility Selector & Audit Status */}
      <div className="flex items-center gap-space-lg">
        <div className="flex items-center gap-space-sm bg-surface-container-low px-space-md py-space-xs rounded-lg border border-outline-variant/40">
          <span className="material-symbols-outlined text-[18px] text-secondary">domain</span>
          <span className="font-label-md text-label-md text-on-surface font-semibold">
            {facilityLabel}
          </span>
          <span className="material-symbols-outlined text-[18px] text-on-surface-variant cursor-pointer">
            arrow_drop_down
          </span>
        </div>

        <div className="flex items-center gap-space-xs bg-tertiary-container/10 text-on-tertiary-container px-space-md py-space-xs rounded-full border border-tertiary-fixed/30 font-label-sm text-label-sm font-semibold">
          <span className="material-symbols-outlined text-[16px] text-on-tertiary-container">
            task_alt
          </span>
          <span>CBAM Readiness: 94.2% Audit Ready</span>
        </div>
      </div>

      {/* Right section: Actions & Profile */}
      <div className="flex items-center gap-space-lg">
        {/* Gemini AI Settings indicator */}
        {onOpenGeminiConfig && (
          <button
            type="button"
            onClick={onOpenGeminiConfig}
            className="flex items-center gap-space-xs bg-surface-container-low hover:bg-surface-container text-on-surface px-space-sm py-space-xs rounded-lg border border-outline-variant/40 text-label-sm font-label-sm font-medium transition-colors"
            title="Configure Google Gemini API"
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isGeminiActive ? "bg-[#069669]" : "bg-[#899AA8]"
              }`}
            />
            <span className="text-on-surface-variant">
              {isGeminiActive ? "Gemini 2.5 Flash" : "AI Offline"}
            </span>
          </button>
        )}

        {/* Quick Search */}
        <button
          type="button"
          onClick={onOpenUpload}
          className="hidden md:flex items-center gap-space-xs bg-surface-container-low hover:bg-surface-container text-on-surface px-space-sm py-space-xs rounded-lg border border-outline-variant/40 text-label-sm font-label-sm font-medium"
        >
          <span className="material-symbols-outlined text-[16px] text-on-surface-variant">
            search
          </span>
          <span className="text-on-surface-variant">Quick Search</span>
          <kbd className="px-space-2xs py-[1px] bg-surface-container-high rounded text-[10px] font-mono-data text-on-surface-variant">
            ⌘K
          </kbd>
        </button>

        {/* Primary Action Button: Ingestion / Audit Run */}
        <button
          type="button"
          onClick={onOpenUpload}
          className="flex items-center gap-space-xs bg-secondary hover:bg-secondary/90 text-on-secondary px-space-md py-space-xs rounded-lg font-label-md text-label-md font-semibold transition-all shadow-[0_1px_3px_rgba(29,78,216,0.3)] hover:shadow-[0_2px_6px_rgba(29,78,216,0.4)] active:scale-[0.98]"
        >
          <span className="material-symbols-outlined text-[18px]">add_circle</span>
          <span>+ New Ingestion / Audit Run</span>
        </button>

        {/* Notification Bell */}
        <div className="relative flex items-center cursor-pointer">
          <span className="material-symbols-outlined text-[22px] text-on-surface-variant hover:text-on-surface transition-colors">
            notifications
          </span>
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-error text-on-error rounded-full text-[10px] font-bold flex items-center justify-center font-mono-data">
            3
          </span>
        </div>

        <div className="h-8 w-px bg-outline-variant/30" />

        {/* User Profile */}
        <div className="flex items-center gap-space-sm">
          <div className="flex flex-col text-right">
            <span className="font-label-md text-label-md text-on-surface font-semibold">
              Dr. Aris Thorne
            </span>
            <span className="font-body-sm text-body-sm text-on-surface-variant text-[11px]">
              Chief Sustainability Officer
            </span>
          </div>
          <div className="w-8 h-8 rounded-full bg-secondary/15 text-secondary border border-outline-variant/40 flex items-center justify-center font-bold text-xs ring-1 ring-secondary/20">
            AT
          </div>
        </div>
      </div>
    </header>
  );
}
