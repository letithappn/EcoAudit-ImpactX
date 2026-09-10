"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import { RunSummaryResponse } from "@/lib/types";
import { useRunStatus } from "@/hooks/use-run-status";
import { PipelineTracker } from "@/components/upload/pipeline-tracker";
import { KpiCards } from "@/components/dashboard/kpi-cards";
import { ScopeBreakdown } from "@/components/dashboard/scope-breakdown";
import { HotspotTable } from "@/components/dashboard/hotspot-table";
import { InsightsPanel } from "@/components/dashboard/insights-panel";
import { ActivityTable } from "@/components/activities/activity-table";
import { IsaCard } from "@/components/ui/isa-card";
import { IsaBadge } from "@/components/ui/isa-badge";
import {
  FileSpreadsheet,
  Layers,
  Sparkles,
  Download,
  ArrowLeft,
  Search,
  ShieldCheck,
  Scale,
  RefreshCw,
} from "lucide-react";

export default function RunDashboardPage() {
  const params = useParams();
  const runId = String(params?.runId || "");
  const router = useRouter();

  const { data: statusData, isComplete, isFailed } = useRunStatus(runId);
  const [summary, setSummary] = useState<RunSummaryResponse | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "activities" | "evidence" | "scenarios">("overview");

  useEffect(() => {
    if (!isComplete) return;

    let active = true;
    setLoadingSummary(true);

    apiClient
      .getRunSummary(runId)
      .then((data) => {
        if (!active) return;
        setSummary(data);
        setLoadingSummary(false);
      })
      .catch((err) => {
        if (!active) return;
        console.error("Failed to fetch run summary:", err);
        setLoadingSummary(false);
      });

    return () => {
      active = false;
    };
  }, [runId, isComplete]);

  // If pipeline is still executing, render real-time pipeline tracker
  if (!isComplete || isFailed) {
    return (
      <div className="flex-1 p-6 max-w-7xl mx-auto w-full flex flex-col gap-6">
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-mono text-[#9E9E9E] hover:text-white"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Ingestion</span>
          </Link>
        </div>

        <div className="py-12">
          <PipelineTracker runId={runId} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-6 max-w-7xl mx-auto w-full flex flex-col gap-6">
      {/* Top Breadcrumb & Metadata Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#383838] pb-4">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="p-1.5 rounded bg-[#383838] border border-[#4A4A4A] text-[#9E9E9E] hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold font-mono text-[#FFFFFF]">
                Facility Audit Run • {summary?.filename || statusData?.filename || "facility.csv"}
              </h1>
              <IsaBadge severity="safe" size="sm">
                Verified
              </IsaBadge>
            </div>
            <p className="text-xs font-mono text-[#9E9E9E] mt-0.5">
              Run ID: {runId} • Model: {statusData?.provider || "mock"} • Region: {statusData?.country || "UK"} ({statusData?.year || 2024})
            </p>
          </div>
        </div>

        {/* Action Controls: Download Dossier & Retest */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <button
            type="button"
            onClick={() => {
              if (!summary) return;
              const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(summary, null, 2));
              const downloadAnchor = document.createElement("a");
              downloadAnchor.setAttribute("href", jsonStr);
              downloadAnchor.setAttribute("download", `ecoaudit-run-${runId.slice(0, 8)}.json`);
              document.body.appendChild(downloadAnchor);
              downloadAnchor.click();
              downloadAnchor.remove();
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#383838] hover:bg-[#424242] border border-[#4A4A4A] text-[#E0E0E0] transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-[#00ACC1]" />
            <span>Export Audit Dossier (JSON)</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs (Level 1 → Level 2 Navigation) */}
      <div className="flex items-center gap-1 border-b border-[#383838] text-xs font-mono">
        <button
          type="button"
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2 border-b-2 font-bold transition-colors flex items-center gap-2 ${
            activeTab === "overview"
              ? "border-[#00ACC1] text-[#00ACC1] bg-[#00ACC1]/5"
              : "border-transparent text-[#9E9E9E] hover:text-[#E0E0E0]"
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Executive Overview (Level 1)</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("activities")}
          className={`px-4 py-2 border-b-2 font-bold transition-colors flex items-center gap-2 ${
            activeTab === "activities"
              ? "border-[#00ACC1] text-[#00ACC1] bg-[#00ACC1]/5"
              : "border-transparent text-[#9E9E9E] hover:text-[#E0E0E0]"
          }`}
        >
          <FileSpreadsheet className="w-3.5 h-3.5" />
          <span>Activity Ledger ({summary?.statistics.total_rows || 0})</span>
        </button>

        <Link
          href={`/runs/${runId}/evidence`}
          className="px-4 py-2 border-b-2 border-transparent text-[#9E9E9E] hover:text-[#E0E0E0] font-bold transition-colors flex items-center gap-2"
        >
          <Search className="w-3.5 h-3.5 text-[#43A047]" />
          <span>The Auditor&apos;s Room (Evidence)</span>
        </Link>

        <Link
          href={`/runs/${runId}/scenarios`}
          className="px-4 py-2 border-b-2 border-transparent text-[#9E9E9E] hover:text-[#E0E0E0] font-bold transition-colors flex items-center gap-2"
        >
          <Sparkles className="w-3.5 h-3.5 text-[#F57C00]" />
          <span>What-If Optimization</span>
        </Link>
      </div>

      {/* Tab 1: Overview */}
      {activeTab === "overview" && summary && (
        <div className="flex flex-col gap-6">
          {/* Level 1: Core KPI Cards */}
          <KpiCards summary={summary} />

          {/* Level 2: Scope 1, 2, 3 Proportional Decomposition */}
          <IsaCard
            title="Scope 1, 2, and 3 Boundary Analysis"
            subtitle="GHG Protocol standard categorization of direct and indirect emissions"
          >
            <ScopeBreakdown
              scopeTotals={summary.scope_totals}
              contributions={summary.scope_contributions}
              emissionsUnit={summary.emissions_unit}
            />
          </IsaCard>

          {/* Level 2: Top Ranked Emission Hotspots */}
          <IsaCard
            title="Ranked Hotspot Analysis (ISA-18.2 Anomaly Prioritization)"
            subtitle="Identifies concentrated emission sources driving >= 15% of facility baseline"
            actions={
              <span className="text-[11px] font-mono text-[#9E9E9E]">
                {summary.hotspots.length} Priority Targets
              </span>
            }
          >
            <HotspotTable
              hotspots={summary.hotspots}
              emissionsUnit={summary.emissions_unit}
            />
          </IsaCard>

          {/* Level 2: Intelligence & Audit Insights */}
          <IsaCard
            title="Automated Environmental Audit Insights"
            subtitle="Rule-based anomaly detection, tariff optimization, and regulatory alerts"
          >
            <InsightsPanel insights={summary.insights} />
          </IsaCard>
        </div>
      )}

      {/* Tab 2: Activities Ledger */}
      {activeTab === "activities" && (
        <IsaCard
          title="Facility Ingestion Ledger"
          subtitle="Detailed row-by-row accounting with AI confidence metrics and firewall validation flags"
        >
          <ActivityTable runId={runId} />
        </IsaCard>
      )}
    </div>
  );
}
