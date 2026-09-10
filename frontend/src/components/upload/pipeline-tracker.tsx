"use client";

import React from "react";
import { useRunStatus } from "@/hooks/use-run-status";
import { IsaCard } from "@/components/ui/isa-card";
import { IsaProgress } from "@/components/ui/isa-progress";
import { IsaBadge } from "@/components/ui/isa-badge";
import { CheckCircle2, AlertTriangle, AlertOctagon, Terminal } from "lucide-react";

interface PipelineTrackerProps {
  runId: string;
  onComplete?: () => void;
}

export function PipelineTracker({ runId, onComplete }: PipelineTrackerProps) {
  const { data, error, isComplete, isFailed } = useRunStatus(runId);

  React.useEffect(() => {
    if (isComplete && onComplete) {
      onComplete();
    }
  }, [isComplete, onComplete]);

  const stats = data?.statistics || {};

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col gap-6">
      {/* Primary Pipeline Progress Engine */}
      <IsaCard
        title={`Pipeline Execution • Run ID: ${runId.slice(0, 8)}...`}
        severity={isFailed ? "critical" : isComplete ? "safe" : "active"}
        actions={
          data && (
            <IsaBadge severity={data.status}>
              {data.status.replace("_", " ")}
            </IsaBadge>
          )
        }
      >
        <div className="flex flex-col gap-4">
          <IsaProgress
            stage={data?.stage || "Uploading"}
            progress={data?.progress || 0}
            showStageList={true}
          />

          {error && (
            <div className="p-3 rounded bg-[#3B1111] border border-[#D32F2F] text-xs font-mono text-[#D32F2F] flex items-center gap-2 mt-2">
              <AlertOctagon className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {isFailed && data?.error && (
            <div className="p-3 rounded bg-[#3B1111] border border-[#D32F2F] text-xs font-mono text-[#D32F2F] flex items-center gap-2 mt-2">
              <AlertOctagon className="w-4 h-4 flex-shrink-0" />
              <span>Engine Error: {data.error}</span>
            </div>
          )}
        </div>
      </IsaCard>

      {/* Real-time Industrial Telemetry Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3 rounded bg-[#383838] border border-[#4A4A4A] flex flex-col">
          <span className="text-[10px] font-mono uppercase text-[#9E9E9E]">
            Ingested Rows
          </span>
          <span className="text-xl font-bold font-mono text-[#E0E0E0] mt-1">
            {stats.total_rows !== undefined ? stats.total_rows : "—"}
          </span>
          <span className="text-[10px] font-mono text-[#757575] mt-0.5">
            CSV Records
          </span>
        </div>

        <div className="p-3 rounded bg-[#383838] border border-[#4A4A4A] flex flex-col">
          <span className="text-[10px] font-mono uppercase text-[#9E9E9E]">
            Firewall Validated
          </span>
          <span className="text-xl font-bold font-mono text-[#43A047] mt-1">
            {stats.validated !== undefined ? stats.validated : "—"}
          </span>
          <span className="text-[10px] font-mono text-[#757575] mt-0.5">
            Schema & Physical Bounds
          </span>
        </div>

        <div className="p-3 rounded bg-[#383838] border border-[#4A4A4A] flex flex-col">
          <span className="text-[10px] font-mono uppercase text-[#9E9E9E]">
            Calculated Activities
          </span>
          <span className="text-xl font-bold font-mono text-[#00ACC1] mt-1">
            {stats.calculated !== undefined ? stats.calculated : "—"}
          </span>
          <span className="text-[10px] font-mono text-[#757575] mt-0.5">
            100% Deterministic
          </span>
        </div>

        <div className="p-3 rounded bg-[#383838] border border-[#4A4A4A] flex flex-col">
          <span className="text-[10px] font-mono uppercase text-[#9E9E9E]">
            Accounting Coverage
          </span>
          <span className="text-xl font-bold font-mono text-[#E0E0E0] mt-1">
            {stats.coverage_percentage !== undefined
              ? `${stats.coverage_percentage}%`
              : "—"}
          </span>
          <span className="text-[10px] font-mono text-[#757575] mt-0.5">
            Authoritative GHG Scope
          </span>
        </div>
      </div>
    </div>
  );
}
