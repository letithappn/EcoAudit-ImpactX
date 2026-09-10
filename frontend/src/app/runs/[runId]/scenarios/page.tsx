"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import { ActivityDTO, RecommendationDTO, ScenarioDTO, ScenarioResponse } from "@/lib/types";
import { ScenarioForm } from "@/components/scenarios/scenario-form";
import { ScenarioResultView } from "@/components/scenarios/scenario-result";
import { RecommendationsList } from "@/components/scenarios/recommendations-list";
import { ArrowLeft, Sparkles, Sliders, RefreshCw } from "lucide-react";

export default function ScenariosPage() {
  const params = useParams();
  const runId = String(params?.runId || "");

  const [activities, setActivities] = useState<ActivityDTO[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationDTO[]>([]);
  const [customScenarios, setCustomScenarios] = useState<ScenarioDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);

    Promise.all([
      apiClient.getActivities(runId, { limit: 100 }),
      apiClient.getRecommendations(runId),
    ])
      .then(([actRes, recRes]) => {
        if (!active) return;
        setActivities(actRes.activities);
        setRecommendations(recRes.recommendations);
        setLoading(false);
      })
      .catch((err) => {
        if (!active) return;
        setError(err.message || "Failed to load scenario dependencies");
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [runId]);

  const handleScenarioCreated = (res: ScenarioResponse) => {
    setCustomScenarios((prev) => [res.scenario, ...prev]);
  };

  return (
    <div className="flex-1 p-6 max-w-7xl mx-auto w-full flex flex-col gap-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#383838] pb-4">
        <div className="flex items-center gap-3">
          <Link
            href={`/runs/${runId}`}
            className="p-1.5 rounded bg-[#383838] border border-[#4A4A4A] text-[#9E9E9E] hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold font-mono text-[#FFFFFF]">
                What-If Decarbonization & Optimization Engine
              </h1>
              <span className="px-2 py-0.5 rounded bg-[#0A3840] border border-[#00ACC1]/60 text-[#00ACC1] text-[10px] font-mono font-bold">
                SCENARIO SIMULATOR
              </span>
            </div>
            <p className="text-xs font-mono text-[#9E9E9E] mt-0.5">
              Run ID: {runId} • Deterministic Re-calculation (No ML Hallucinations)
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center font-mono text-xs text-[#757575]">
          Loading activities and AI decarbonization models...
        </div>
      ) : error ? (
        <div className="p-4 rounded bg-[#3B1111] border border-[#D32F2F] text-xs font-mono text-[#D32F2F]">
          {error}
        </div>
      ) : (
        <div className="flex flex-col gap-8">
          {/* Custom Scenario Builder Form */}
          <ScenarioForm
            runId={runId}
            activities={activities}
            onScenarioCreated={handleScenarioCreated}
          />

          {/* Newly Created Scenarios Display */}
          {customScenarios.length > 0 && (
            <div className="flex flex-col gap-4">
              <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-[#FFFFFF] flex items-center gap-2">
                <Sliders className="w-4 h-4 text-[#00ACC1]" />
                <span>Simulated Scenarios ({customScenarios.length})</span>
              </h2>
              {customScenarios.map((sc, idx) => (
                <ScenarioResultView key={idx} scenario={sc} />
              ))}
            </div>
          )}

          {/* AI Recommended Decarbonization Interventions */}
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-[#FFFFFF] flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#43A047]" />
                <span>AI Decarbonization Opportunities & Interventions</span>
              </h2>
              <span className="text-xs font-mono text-[#9E9E9E]">
                {recommendations.length} Proposals Evaluated
              </span>
            </div>
            <RecommendationsList recommendations={recommendations} />
          </div>
        </div>
      )}
    </div>
  );
}
