"use client";

import React from "react";
import { IsaSeverity } from "./isa-card";

interface IsaBadgeProps {
  severity?: IsaSeverity | string;
  size?: "sm" | "md";
  className?: string;
  children: React.ReactNode;
}

export function IsaBadge({
  severity = "normal",
  size = "md",
  className = "",
  children,
}: IsaBadgeProps) {
  // Normalize string inputs to supported severities
  const norm = String(severity).toLowerCase();
  let resolvedSeverity: IsaSeverity = "normal";

  if (norm === "critical" || norm === "rejected" || norm === "error" || norm === "fail") {
    resolvedSeverity = "critical";
  } else if (norm === "warning" || norm === "review" || norm === "high" || norm === "warn") {
    resolvedSeverity = "warning";
  } else if (norm === "active" || norm === "info" || norm === "running" || norm === "medium") {
    resolvedSeverity = "active";
  } else if (norm === "safe" || norm === "validated" || norm === "complete" || norm === "supported" || norm === "ok" || norm === "low") {
    resolvedSeverity = "safe";
  }

  const styles = {
    normal: "bg-[#424242] text-[#9E9E9E] border-[#555555]",
    safe: "bg-[#1B3A24] text-[#43A047] border-[#43A047]/50",
    active: "bg-[#0A3840] text-[#00ACC1] border-[#00ACC1]/50",
    warning: "bg-[#3D2506] text-[#F57C00] border-[#F57C00]/50",
    critical: "bg-[#3B1111] text-[#D32F2F] border-[#D32F2F]/60 isa-pulse-critical",
  }[resolvedSeverity];

  const sizeClass = size === "sm" ? "px-1.5 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs";

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-medium rounded border uppercase tracking-wider ${styles} ${sizeClass} ${className}`}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{
          backgroundColor:
            resolvedSeverity === "critical"
              ? "#D32F2F"
              : resolvedSeverity === "warning"
              ? "#F57C00"
              : resolvedSeverity === "active"
              ? "#00ACC1"
              : resolvedSeverity === "safe"
              ? "#43A047"
              : "#9E9E9E",
        }}
      />
      {children}
    </span>
  );
}
