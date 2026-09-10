"use client";

import React, { useState, useEffect } from "react";
import { StitchSidebar, StitchViewId } from "@/components/stitch/stitch-sidebar";
import { StitchHeader } from "@/components/stitch/stitch-header";
import { StitchIngestionModal } from "@/components/stitch/stitch-ingestion-modal";
import { GeminiConfigModal } from "@/components/sap/gemini-config-modal";
import { ExecutiveOverviewView } from "@/components/stitch/views/executive-overview-view";
import { CarbonBalanceView } from "@/components/stitch/views/carbon-balance-view";
import { ScenarioSimulatorView } from "@/components/stitch/views/scenario-simulator-view";
import { CbamProductsView } from "@/components/stitch/views/cbam-products-view";
import { Scope3SuppliersView } from "@/components/stitch/views/scope3-suppliers-view";
import { EsgTargetsView } from "@/components/stitch/views/esg-targets-view";
import { apiClient } from "@/lib/api-client";
import { RunSummaryResponse, ActivityDTO, RunCreateResponse } from "@/lib/types";
import { useRunStatus } from "@/hooks/use-run-status";

export default function AppMasterPage() {
  const [activeView, setActiveView] = useState<StitchViewId>("executive-overview");
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isGeminiModalOpen, setIsGeminiModalOpen] = useState(false);
  const [isGeminiActive, setIsGeminiActive] = useState(false);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [summary, setSummary] = useState<RunSummaryResponse | null>(null);
  const [activities, setActivities] = useState<ActivityDTO[]>([]);
  const [bannerVisible, setBannerVisible] = useState(true);

  const { data: statusData, isComplete, isFailed } = useRunStatus(activeRunId, 500);

  // Check initial AI status & discover active runs
  useEffect(() => {
    apiClient
      .getAIStatus()
      .then((res) => {
        setIsGeminiActive(res.configured);
      })
      .catch((err) => {
        console.warn("AI status check note:", err);
      });

    // Check if runId is in URL query parameters
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const urlRunId = params.get("runId");
      if (urlRunId) {
        setActiveRunId(urlRunId);
        return;
      }
    }

    // Auto-discover existing runs from backend or launch Chicago benchmark
    apiClient
      .listRuns()
      .then((runs) => {
        if (runs && runs.length > 0) {
          // Prefer completed Chicago run (dual-scope UK factor calculation first) or newest run
          const chicagoRun =
            runs.find(
              (r) =>
                r.filename?.toLowerCase().includes("chicago") &&
                r.status.startsWith("complete") &&
                r.country === "UK"
            ) ||
            runs.find(
              (r) =>
                r.filename?.toLowerCase().includes("chicago") &&
                r.status.startsWith("complete")
            );
          const completedRun =
            chicagoRun ||
            runs.find((r) => r.status.startsWith("complete")) ||
            runs[0];
          setActiveRunId(completedRun.run_id);
        } else {
          // If store is empty, automatically trigger Chicago Energy Benchmark run
          apiClient
            .createDemo("mock", 2024, "UK", "chicago")
            .then((res) => {
              setActiveRunId(res.run_id);
            })
            .catch((err) => {
              console.warn("Auto-demo initialization note:", err);
            });
        }
      })
      .catch((err) => {
        console.warn("Run discovery note:", err);
      });
  }, []);

  // When pipeline completes, fetch authoritative summary and activities
  useEffect(() => {
    if (!activeRunId || !isComplete) return;

    let active = true;

    Promise.all([
      apiClient.getRunSummary(activeRunId),
      apiClient.getActivities(activeRunId, { limit: 150 }),
    ])
      .then(([sumRes, actRes]) => {
        if (!active) return;
        setSummary(sumRes);
        // Prioritize validated rows so real measured buildings are showcased immediately
        const sorted = [...actRes.activities].sort((a, b) => {
          if (a.validation_status === "validated" && b.validation_status !== "validated") return -1;
          if (a.validation_status !== "validated" && b.validation_status === "validated") return 1;
          return 0;
        });
        setActivities(sorted);
      })
      .catch((err) => {
        console.error("Failed to load run outputs:", err);
      });

    return () => {
      active = false;
    };
  }, [activeRunId, isComplete]);

  const handleRunCreated = (res: RunCreateResponse) => {
    setBannerVisible(true);
    setActiveRunId(res.run_id);
  };

  const facilityLabel = summary?.filename?.toLowerCase().includes("chicago")
    ? `City of Chicago Energy Benchmarking (28,329 Buildings) • FY2024 Telemetry`
    : summary?.filename
    ? `${summary.filename} • FY2024 Audit Run`
    : "Global Operations (All 14 Facilities) | FY2024 / Q3 CBAM Cycle";

  return (
    <div className="min-h-screen flex bg-surface font-body-md text-on-surface antialiased">
      {/* 1. Stitch Fixed Deep Navy Sidebar */}
      <StitchSidebar
        activeView={activeView}
        onSelectView={setActiveView}
        isGeminiActive={isGeminiActive}
      />

      {/* 2. Main Workspace Layout */}
      <div className="pl-72 flex flex-col min-h-screen w-full">
        {/* Top Header */}
        <StitchHeader
          onOpenUpload={() => setIsUploadOpen(true)}
          onOpenGeminiConfig={() => setIsGeminiModalOpen(true)}
          isGeminiActive={isGeminiActive}
          activeRunId={activeRunId}
          facilityLabel={facilityLabel}
        />

        {/* Live Pipeline Execution Progress Banner */}
        {activeRunId && bannerVisible && (
          <div className="mt-16 bg-surface-container-high/60 border-b border-outline-variant/30 px-space-xl py-space-xs flex items-center justify-between text-xs select-none text-on-surface">
            <div className="flex items-center gap-space-md">
              {!isComplete && !isFailed ? (
                <span className="w-3.5 h-3.5 border-2 border-secondary/30 border-t-secondary rounded-full animate-spin flex-shrink-0" />
              ) : isComplete ? (
                <span className="material-symbols-outlined text-[18px] text-on-tertiary-container flex-shrink-0">
                  task_alt
                </span>
              ) : (
                <span className="material-symbols-outlined text-[18px] text-error flex-shrink-0">
                  error
                </span>
              )}

              <div className="flex items-center gap-space-xs">
                <span className="font-bold text-on-surface">
                  Pipeline Stage ({statusData?.stage || "Processing"}):
                </span>
                <span className="font-semibold text-secondary">
                  {statusData?.progress || 0}%
                </span>
                <span className="text-on-surface-variant font-mono-data text-[11px]">
                  • Run ID: {activeRunId.slice(0, 8)}... •{" "}
                  {isComplete
                    ? `Calculated Total: ${parseFloat(summary?.total_emissions || "0").toLocaleString()} ${summary?.emissions_unit || "kgCO2e"}`
                    : "Ingesting rows and evaluating double-entry ledger..."}
                </span>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setBannerVisible(false)}
              className="text-on-surface-variant hover:text-on-surface p-1 rounded hover:bg-surface-container-high"
            >
              <span className="material-symbols-outlined text-[16px]">close</span>
            </button>
          </div>
        )}

        {/* Dynamic Stitch Views matching Selected Navigation */}
        <main className={`w-full flex-1 bg-surface ${!activeRunId || !bannerVisible ? "pt-16" : ""}`}>
          {activeView === "executive-overview" && (
            <ExecutiveOverviewView
              summary={summary}
              activities={activities}
              onOpenUpload={() => setIsUploadOpen(true)}
            />
          )}

          {activeView === "cbam-and-product-footprints" && (
            <CbamProductsView
              summary={summary}
              activities={activities}
              onOpenUpload={() => setIsUploadOpen(true)}
            />
          )}

          {activeView === "multi-year-esg-targets" && (
            <EsgTargetsView
              summary={summary}
              onOpenUpload={() => setIsUploadOpen(true)}
            />
          )}

          {activeView === "scope-3-and-suppliers" && (
            <Scope3SuppliersView
              summary={summary}
              activities={activities}
              onOpenUpload={() => setIsUploadOpen(true)}
            />
          )}

          {activeView === "carbon-balance-ledger" && (
            <CarbonBalanceView
              summary={summary}
              activities={activities}
              onOpenUpload={() => setIsUploadOpen(true)}
            />
          )}

          {activeView === "decarbonization-simulator" && (
            <ScenarioSimulatorView
              summary={summary}
              activities={activities}
              activeRunId={activeRunId}
            />
          )}
        </main>
      </div>

      {/* 3. Stitch CSV Ingestion & 1-Click Preset Modal */}
      <StitchIngestionModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onRunCreated={handleRunCreated}
        isGeminiActive={isGeminiActive}
      />

      {/* 4. Gemini Configuration Modal */}
      <GeminiConfigModal
        isOpen={isGeminiModalOpen}
        onClose={() => setIsGeminiModalOpen(false)}
        onConfigured={(st) => setIsGeminiActive(st.configured)}
      />
    </div>
  );
}
