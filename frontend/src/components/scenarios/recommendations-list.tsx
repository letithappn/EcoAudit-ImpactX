"use client";

import React from "react";
import { RecommendationDTO } from "@/lib/types";
import { IsaCard } from "@/components/ui/isa-card";
import { IsaBadge } from "@/components/ui/isa-badge";
import { ScenarioResultView } from "./scenario-result";
import { Sparkles, AlertCircle, ArrowRight, ShieldCheck } from "lucide-react";

interface RecommendationsListProps {
  recommendations: RecommendationDTO[];
}

export function RecommendationsList({
  recommendations,
}: RecommendationsListProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="p-8 text-center text-xs font-mono text-[#757575] bg-[#2F2F2F] rounded border border-[#4A4A4A]">
        No automated AI decarbonization recommendations proposed for this dataset.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-5 font-mono text-xs">
      {recommendations.map((rec, idx) => {
        const isSupported = rec.status.toLowerCase() === "supported";
        const isReview = rec.status.toLowerCase() === "requires_review";

        return (
          <IsaCard
            key={idx}
            title={rec.title}
            subtitle={`Target: ${rec.target_hotspot} (${rec.target_activity_ids.length} line items)`}
            severity={isSupported ? "safe" : isReview ? "warning" : "critical"}
            actions={
              <IsaBadge severity={rec.status} size="sm">
                {rec.status.replace("_", " ")}
              </IsaBadge>
            }
          >
            <div className="flex flex-col gap-4">
              {/* Rationale and AI Explanation */}
              <div className="p-3 bg-[#262626] rounded border border-[#383838]">
                <div className="flex items-center gap-1.5 text-[#00ACC1] font-bold uppercase mb-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>AI Engineering Rationale:</span>
                </div>
                <p className="text-[#E0E0E0] leading-relaxed">
                  {rec.rationale}
                </p>

                {rec.explanation && (
                  <p className="text-[11px] text-[#9E9E9E] mt-2 pt-2 border-t border-[#383838]">
                    {rec.explanation}
                  </p>
                )}
              </div>

              {/* Validation Errors if Rejected */}
              {rec.validation_errors && rec.validation_errors.length > 0 && (
                <div className="p-3 rounded bg-[#3B1111] border border-[#D32F2F] text-[#D32F2F]">
                  <div className="font-bold uppercase mb-1">
                    Firewall Verification Failures:
                  </div>
                  <ul className="list-disc list-inside">
                    {rec.validation_errors.map((err, errIdx) => (
                      <li key={errIdx}>{err}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Scenario Result Subview if evaluated */}
              {rec.scenario && (
                <div className="mt-1">
                  <div className="text-[11px] text-[#43A047] font-bold uppercase mb-2 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Verified Deterministic Impact:</span>
                  </div>
                  <ScenarioResultView scenario={rec.scenario} />
                </div>
              )}
            </div>
          </IsaCard>
        );
      })}
    </div>
  );
}
