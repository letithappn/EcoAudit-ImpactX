"use client";

import React from "react";
import { InsightDTO } from "@/lib/types";
import { IsaBadge } from "@/components/ui/isa-badge";
import { Lightbulb, Info, AlertTriangle, CheckCircle2 } from "lucide-react";

interface InsightsPanelProps {
  insights: InsightDTO[];
}

export function InsightsPanel({ insights }: InsightsPanelProps) {
  if (!insights || insights.length === 0) {
    return (
      <div className="p-6 text-center text-xs font-mono text-[#757575] bg-[#2F2F2F] rounded border border-[#4A4A4A]">
        No automated anomaly or optimization insights generated for this dataset.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {insights.map((item, idx) => {
        const isCritical = item.severity.toLowerCase() === "critical";
        const isWarning = item.severity.toLowerCase() === "warning" || item.severity.toLowerCase() === "high";

        return (
          <div
            key={idx}
            className={`p-4 rounded bg-[#333333] border transition-all flex flex-col justify-between ${
              isCritical
                ? "border-[#D32F2F]/60 shadow-[0_0_8px_rgba(211,47,47,0.15)]"
                : isWarning
                ? "border-[#F57C00]/50"
                : "border-[#4A4A4A]"
            }`}
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-1.5">
                  <Lightbulb
                    className={`w-4 h-4 ${
                      isCritical
                        ? "text-[#D32F2F]"
                        : isWarning
                        ? "text-[#F57C00]"
                        : "text-[#00ACC1]"
                    }`}
                  />
                  <span className="font-mono text-xs font-bold text-[#E0E0E0]">
                    {item.title}
                  </span>
                </div>
                <IsaBadge severity={item.severity} size="sm">
                  {item.severity}
                </IsaBadge>
              </div>

              <p className="text-xs text-[#9E9E9E] leading-relaxed">
                {item.detail}
              </p>
            </div>

            {item.evidence && (
              <div className="mt-3 pt-2 border-t border-[#424242] flex items-center gap-1.5 text-[11px] font-mono text-[#00ACC1]">
                <Info className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="truncate">{item.evidence}</span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
