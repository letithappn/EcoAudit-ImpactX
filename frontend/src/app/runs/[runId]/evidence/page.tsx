"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/lib/api-client";
import { EvidenceResponse } from "@/lib/types";
import { EvidencePanel } from "@/components/evidence/evidence-panel";
import { ArrowLeft, RefreshCw, ShieldCheck } from "lucide-react";

export default function EvidencePage() {
  const params = useParams();
  const runId = String(params?.runId || "");

  const [evidenceData, setEvidenceData] = useState<EvidenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEvidence = () => {
    setLoading(true);
    setError(null);
    apiClient
      .getEvidence(runId)
      .then((data) => {
        setEvidenceData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load calculation evidence");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchEvidence();
  }, [runId]);

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
                The Auditor&apos;s Room (Evidence & Calculation Lineage)
              </h1>
              <span className="px-2 py-0.5 rounded bg-[#1B3A24] border border-[#43A047]/60 text-[#43A047] text-[10px] font-mono font-bold">
                ISO 14064-3
              </span>
            </div>
            <p className="text-xs font-mono text-[#9E9E9E] mt-0.5">
              Run ID: {runId} • Immutable Audit Trace
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={fetchEvidence}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#383838] hover:bg-[#424242] border border-[#4A4A4A] text-[#E0E0E0] text-xs font-mono transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-[#00ACC1]" : ""}`} />
          <span>Refresh Evidence</span>
        </button>
      </div>

      {loading ? (
        <div className="py-20 text-center font-mono text-xs text-[#757575]">
          Reconstructing calculation lineage from deterministic ledger...
        </div>
      ) : error ? (
        <div className="p-4 rounded bg-[#3B1111] border border-[#D32F2F] text-xs font-mono text-[#D32F2F]">
          {error}
        </div>
      ) : evidenceData ? (
        <EvidencePanel
          evidence={evidenceData.evidence}
          rejections={evidenceData.calculation_rejections}
        />
      ) : null}
    </div>
  );
}
