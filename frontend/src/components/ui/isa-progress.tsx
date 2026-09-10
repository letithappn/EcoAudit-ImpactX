"use client";

import React from "react";

export const PIPELINE_STAGES = [
  "Uploading",
  "Parsing",
  "AI Classification",
  "Validation",
  "Carbon Calculation",
  "Carbon Intelligence",
  "Scenario Analysis",
  "Recommendations",
] as const;

export type PipelineStage = (typeof PIPELINE_STAGES)[number] | string;

interface IsaProgressProps {
  stage?: PipelineStage;
  progress?: number; // 0 - 100
  showStageList?: boolean;
  className?: string;
}

export function IsaProgress({
  stage = "Uploading",
  progress = 0,
  showStageList = false,
  className = "",
}: IsaProgressProps) {
  const clampedProgress = Math.min(100, Math.max(0, Math.round(progress)));
  const currentStageIndex = PIPELINE_STAGES.indexOf(stage as any);

  return (
    <div className={`flex flex-col gap-2.5 ${className}`}>
      <div className="flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#00ACC1] animate-ping" />
          <span className="text-[#E0E0E0] font-semibold tracking-wide">
            {stage}
          </span>
        </div>
        <span className="text-[#00ACC1] font-bold">{clampedProgress}%</span>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-[#262626] rounded overflow-hidden border border-[#4A4A4A]">
        <div
          className="h-full bg-gradient-to-r from-[#00838F] to-[#00ACC1] transition-all duration-300 ease-out"
          style={{ width: `${clampedProgress}%` }}
        />
      </div>

      {/* Optional Stepper of 8 Stages */}
      {showStageList && (
        <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5 pt-2">
          {PIPELINE_STAGES.map((s, idx) => {
            const isCompleted = currentStageIndex > idx || clampedProgress === 100;
            const isCurrent = currentStageIndex === idx && clampedProgress < 100;

            let border = "border-[#424242]";
            let text = "text-[#757575]";
            let bg = "bg-[#2B2B2B]";

            if (isCompleted) {
              border = "border-[#43A047]/60";
              text = "text-[#43A047]";
              bg = "bg-[#1B3A24]/30";
            } else if (isCurrent) {
              border = "border-[#00ACC1]";
              text = "text-[#00ACC1]";
              bg = "bg-[#0A3840]/40";
            }

            return (
              <div
                key={s}
                className={`p-1.5 rounded border ${border} ${bg} flex flex-col items-center justify-center text-center`}
              >
                <span className="text-[10px] font-mono text-[#9E9E9E]">
                  0{idx + 1}
                </span>
                <span className={`text-[10px] font-medium leading-tight truncate w-full ${text}`}>
                  {s}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
