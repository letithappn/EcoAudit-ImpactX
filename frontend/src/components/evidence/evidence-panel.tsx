"use client";

import React, { useState } from "react";
import { EvidenceDTO } from "@/lib/types";
import { IsaCard } from "@/components/ui/isa-card";
import { IsaBadge } from "@/components/ui/isa-badge";
import {
  FileText,
  Search,
  CheckCircle2,
  AlertOctagon,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  Hash,
} from "lucide-react";

interface EvidencePanelProps {
  evidence: EvidenceDTO[];
  rejections?: Record<string, string>[];
}

export function EvidencePanel({ evidence, rejections = [] }: EvidencePanelProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const filteredEvidence = evidence.filter((item) => {
    const term = searchTerm.toLowerCase();
    return (
      item.activity_description.toLowerCase().includes(term) ||
      item.factor.source.toLowerCase().includes(term) ||
      item.factor.factor_id.toLowerCase().includes(term) ||
      item.trace.formula_description.toLowerCase().includes(term)
    );
  });

  return (
    <div className="flex flex-col gap-6 font-mono text-xs">
      {/* VVB Auditor Cleanroom Header Notice */}
      <div className="p-4 rounded bg-[#232323] border border-[#00ACC1]/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded bg-[#0A3840] border border-[#00ACC1] text-[#00ACC1]">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-[#FFFFFF] uppercase">
              ISO 14064-3 / VVB Cleanroom & Lineage Explorer
            </h3>
            <p className="text-[11px] text-[#9E9E9E]">
              100% cryptographic trace from facility invoice line items to government factor datasets.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-1 rounded bg-[#1B3A24] border border-[#43A047]/60 text-[#43A047] text-[10px] font-bold">
            ZERO HALLUCINATIONS: FIXED-POINT
          </span>
        </div>
      </div>

      {/* Rejections Alert (if any calculations were rejected by Firewall) */}
      {rejections.length > 0 && (
        <IsaCard
          title="Firewall Calculation Rejections"
          subtitle="Records quarantined due to missing official factor or physical impossibility"
          severity="critical"
        >
          <div className="flex flex-col gap-2">
            {rejections.map((rej, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded bg-[#2B2B2B] border border-[#D32F2F]/40 flex items-start gap-2 text-[#D32F2F]"
              >
                <AlertOctagon className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">
                    Row {rej.source_row || "—"} (ID: {rej.activity_id}):
                  </span>{" "}
                  <span>{rej.reason}</span>
                </div>
              </div>
            ))}
          </div>
        </IsaCard>
      )}

      {/* Filter & Search Bar */}
      <div className="flex items-center justify-between gap-4 p-3 bg-[#2B2B2B] rounded border border-[#4A4A4A]">
        <div className="flex items-center gap-2 flex-1 max-w-md">
          <Search className="w-4 h-4 text-[#9E9E9E]" />
          <input
            type="text"
            placeholder="Search activities, factor IDs, or source datasets..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-transparent border-none text-[#E0E0E0] placeholder-[#757575] focus:outline-none text-xs"
          />
        </div>
        <span className="text-[#9E9E9E] text-[11px]">
          Showing {filteredEvidence.length} of {evidence.length} Evidence Records
        </span>
      </div>

      {/* Evidence Lineage Cards */}
      <div className="flex flex-col gap-3">
        {filteredEvidence.map((item) => {
          const isExpanded = expandedIds.has(item.result_id);
          const trace = item.trace;
          const factor = item.factor;

          return (
            <div
              key={item.result_id}
              className="rounded border border-[#4A4A4A] bg-[#333333] overflow-hidden transition-all"
            >
              {/* Card Header Line */}
              <div
                onClick={() => toggleExpand(item.result_id)}
                className="p-3.5 flex items-center justify-between gap-4 cursor-pointer hover:bg-[#383838] transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <button
                    type="button"
                    className="text-[#9E9E9E] hover:text-[#FFFFFF]"
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4" />
                    ) : (
                      <ChevronRight className="w-4 h-4" />
                    )}
                  </button>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-[#FFFFFF] truncate">
                        {item.activity_description}
                      </span>
                      {item.source_row && (
                        <span className="text-[10px] text-[#757575]">
                          (Row #{item.source_row})
                        </span>
                      )}
                    </div>
                    <div className="text-[11px] text-[#9E9E9E] mt-0.5 flex items-center gap-2">
                      <span>{trace.scope}</span>
                      <span>•</span>
                      <span>{trace.category}</span>
                      <span>•</span>
                      <span className="text-[#00ACC1]">{factor.source}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 flex-shrink-0">
                  <div className="text-right">
                    <div className="text-sm font-bold text-[#43A047]">
                      {item.emissions_value} {item.emissions_unit}
                    </div>
                    <div className="text-[10px] text-[#757575]">
                      Factor: {factor.factor_value} {factor.factor_unit}
                    </div>
                  </div>
                  <IsaBadge severity="safe" size="sm">
                    Verified
                  </IsaBadge>
                </div>
              </div>

              {/* Expandable Deep Trace Inspection */}
              {isExpanded && (
                <div className="p-4 border-t border-[#424242] bg-[#2B2B2B] flex flex-col gap-4 text-xs">
                  {/* Calculation Formula Decomposition */}
                  <div className="p-3 rounded bg-[#232323] border border-[#4A4A4A]">
                    <span className="text-[#00ACC1] font-bold uppercase block mb-1">
                      Deterministic Mathematical Formula:
                    </span>
                    <p className="text-[#E0E0E0] font-semibold font-mono">
                      {trace.formula_description}
                    </p>
                    <div className="mt-2 text-[11px] text-[#9E9E9E] grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-[#383838]">
                      <div>
                        <span className="text-[#757575] block">Input Qty:</span>
                        <span className="text-[#FFFFFF]">
                          {trace.input_quantity} {trace.input_unit}
                        </span>
                      </div>
                      <div>
                        <span className="text-[#757575] block">Conversion:</span>
                        <span className="text-[#FFFFFF]">
                          {trace.conversion_factor_applied}
                        </span>
                      </div>
                      <div>
                        <span className="text-[#757575] block">Normalized:</span>
                        <span className="text-[#FFFFFF]">
                          {trace.normalized_quantity} {trace.normalized_unit}
                        </span>
                      </div>
                      <div>
                        <span className="text-[#757575] block">Factor Value:</span>
                        <span className="text-[#FFFFFF]">
                          {trace.emission_factor_value} {trace.emission_factor_unit}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Official Factor Metadata */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
                    <div className="p-3 rounded bg-[#262626] border border-[#383838]">
                      <span className="text-[#9E9E9E] font-bold uppercase block mb-1">
                        Emission Factor Provenance
                      </span>
                      <div className="flex flex-col gap-1 text-[#E0E0E0]">
                        <div>
                          <span className="text-[#757575]">Registry ID:</span>{" "}
                          <span className="text-[#00ACC1]">{factor.factor_id}</span>
                        </div>
                        <div>
                          <span className="text-[#757575]">Source & Dataset:</span>{" "}
                          {factor.source} ({factor.dataset})
                        </div>
                        <div>
                          <span className="text-[#757575]">Vintage Year:</span>{" "}
                          {factor.year} (v{factor.version})
                        </div>
                        <div>
                          <span className="text-[#757575]">Country / Grid:</span>{" "}
                          {factor.country}
                        </div>
                      </div>
                    </div>

                    <div className="p-3 rounded bg-[#262626] border border-[#383838]">
                      <span className="text-[#9E9E9E] font-bold uppercase block mb-1">
                        Methodology & Applicability
                      </span>
                      <p className="text-[#E0E0E0] mb-1">{factor.methodology}</p>
                      <p className="text-[10px] text-[#757575]">
                        {factor.applicability_notes}
                      </p>
                      {factor.is_proxy && (
                        <span className="inline-block mt-2 text-[10px] text-[#F57C00] font-semibold">
                          ⚠️ Regional Proxy factor applied
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
