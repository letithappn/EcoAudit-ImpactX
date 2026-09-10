"use client";

import React from "react";

export type IsaSeverity = "normal" | "safe" | "active" | "warning" | "critical";

interface IsaCardProps {
  title?: string;
  subtitle?: string;
  severity?: IsaSeverity;
  className?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export function IsaCard({
  title,
  subtitle,
  severity = "normal",
  className = "",
  children,
  actions,
}: IsaCardProps) {
  // ISA-101 Report-by-Exception:
  // Neutral gray borders for normal; high-contrast borders only when deviating
  const severityBorder = {
    normal: "border-[#4A4A4A]",
    safe: "border-[#43A047]/60",
    active: "border-[#00ACC1]",
    warning: "border-[#F57C00]",
    critical: "border-[#D32F2F] shadow-[0_0_12px_rgba(211,47,47,0.25)]",
  }[severity];

  const severityHeaderAccent = {
    normal: "border-b-[#4A4A4A]/50",
    safe: "border-b-[#43A047]/40",
    active: "border-b-[#00ACC1]/50",
    warning: "border-b-[#F57C00]/60",
    critical: "border-b-[#D32F2F]",
  }[severity];

  return (
    <div
      className={`bg-[#383838] rounded-md border ${severityBorder} transition-all duration-150 overflow-hidden flex flex-col ${className}`}
    >
      {(title || actions) && (
        <div
          className={`px-4 py-3 border-b ${severityHeaderAccent} flex items-center justify-between gap-2 bg-[#2F2F2F]/60`}
        >
          <div>
            {title && (
              <h3 className="text-sm font-semibold tracking-wide text-[#E0E0E0] uppercase font-mono">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-xs text-[#9E9E9E] mt-0.5">{subtitle}</p>
            )}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className="p-4 flex-1">{children}</div>
    </div>
  );
}
