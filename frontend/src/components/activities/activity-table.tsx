"use client";

import React, { useState, useEffect } from "react";
import { ActivityDTO } from "@/lib/types";
import { apiClient } from "@/lib/api-client";
import { IsaBadge } from "@/components/ui/isa-badge";
import { ChevronLeft, ChevronRight, Filter, AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

interface ActivityTableProps {
  runId: string;
}

export function ActivityTable({ runId }: ActivityTableProps) {
  const [activities, setActivities] = useState<ActivityDTO[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [limit] = useState(25);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    apiClient
      .getActivities(runId, { offset, limit, status: statusFilter })
      .then((res) => {
        if (!active) return;
        setActivities(res.activities);
        setTotal(res.total);
        setLoading(false);
      })
      .catch((err) => {
        if (!active) return;
        setError(err.message || "Failed to load activities");
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [runId, offset, limit, statusFilter]);

  const handleFilter = (status?: string) => {
    setStatusFilter(status);
    setOffset(0);
  };

  const totalPages = Math.ceil(total / limit) || 1;
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="flex flex-col gap-4 font-mono text-xs">
      {/* Table Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-[#2B2B2B] rounded border border-[#4A4A4A]">
        <div className="flex items-center gap-1.5">
          <Filter className="w-3.5 h-3.5 text-[#9E9E9E]" />
          <span className="text-[#9E9E9E] font-semibold uppercase mr-2">Filter:</span>
          <button
            type="button"
            onClick={() => handleFilter(undefined)}
            className={`px-2.5 py-1 rounded transition-colors ${
              statusFilter === undefined
                ? "bg-[#00838F] text-white font-bold"
                : "bg-[#383838] text-[#9E9E9E] hover:text-white"
            }`}
          >
            All ({total})
          </button>
          <button
            type="button"
            onClick={() => handleFilter("validated")}
            className={`px-2.5 py-1 rounded transition-colors ${
              statusFilter === "validated"
                ? "bg-[#1B3A24] text-[#43A047] border border-[#43A047] font-bold"
                : "bg-[#383838] text-[#9E9E9E] hover:text-white"
            }`}
          >
            Validated
          </button>
          <button
            type="button"
            onClick={() => handleFilter("review")}
            className={`px-2.5 py-1 rounded transition-colors ${
              statusFilter === "review"
                ? "bg-[#3D2506] text-[#F57C00] border border-[#F57C00] font-bold"
                : "bg-[#383838] text-[#9E9E9E] hover:text-white"
            }`}
          >
            Review Required
          </button>
          <button
            type="button"
            onClick={() => handleFilter("rejected")}
            className={`px-2.5 py-1 rounded transition-colors ${
              statusFilter === "rejected"
                ? "bg-[#3B1111] text-[#D32F2F] border border-[#D32F2F] font-bold"
                : "bg-[#383838] text-[#9E9E9E] hover:text-white"
            }`}
          >
            Rejected
          </button>
        </div>

        {/* Pagination Navigation */}
        <div className="flex items-center gap-2 text-[#9E9E9E]">
          <span>
            Page {currentPage} of {totalPages} ({total} items)
          </span>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setOffset(Math.max(0, offset - limit))}
              disabled={offset === 0 || loading}
              className="p-1 rounded bg-[#383838] border border-[#4A4A4A] disabled:opacity-40 hover:text-white"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => setOffset(offset + limit)}
              disabled={offset + limit >= total || loading}
              className="p-1 rounded bg-[#383838] border border-[#4A4A4A] disabled:opacity-40 hover:text-white"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded bg-[#3B1111] border border-[#D32F2F] text-[#D32F2F]">
          {error}
        </div>
      )}

      {/* Grid Table */}
      <div className="overflow-x-auto border border-[#4A4A4A] rounded bg-[#2B2B2B]">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-[#4A4A4A] bg-[#232323] text-[#9E9E9E]">
              <th className="py-2.5 px-3 uppercase font-semibold">Row</th>
              <th className="py-2.5 px-3 uppercase font-semibold">Activity Description</th>
              <th className="py-2.5 px-3 uppercase font-semibold">Quantity</th>
              <th className="py-2.5 px-3 uppercase font-semibold">Unit</th>
              <th className="py-2.5 px-3 uppercase font-semibold">Scope / Category</th>
              <th className="py-2.5 px-3 uppercase font-semibold text-center">AI Confidence</th>
              <th className="py-2.5 px-3 uppercase font-semibold text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#383838]">
            {loading ? (
              <tr>
                <td colSpan={7} className="py-10 text-center text-[#757575]">
                  Loading activity ledger records...
                </td>
              </tr>
            ) : activities.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-10 text-center text-[#757575]">
                  No activities found matching criteria.
                </td>
              </tr>
            ) : (
              activities.map((act, idx) => (
                <tr
                  key={act.activity_id || idx}
                  className="hover:bg-[#333333] transition-colors"
                >
                  <td className="py-2.5 px-3 text-[#757575]">
                    {act.source_row ?? "—"}
                  </td>
                  <td className="py-2.5 px-3 max-w-xs truncate font-medium text-[#E0E0E0]" title={act.description || ""}>
                    {act.description || act.activity_type || "Unclassified Activity"}
                  </td>
                  <td className="py-2.5 px-3 font-bold text-[#FFFFFF]">
                    {act.quantity ?? "—"}
                  </td>
                  <td className="py-2.5 px-3 text-[#00ACC1]">
                    {act.unit ?? "—"}
                  </td>
                  <td className="py-2.5 px-3 text-[#9E9E9E]">
                    <span>{act.scope || "Unassigned"}</span>
                    {act.category && (
                      <span className="text-[10px] text-[#757575] block">
                        {act.category}
                      </span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    {act.confidence ? (
                      <span
                        className={`font-semibold ${
                          parseFloat(act.confidence) >= 0.9
                            ? "text-[#43A047]"
                            : parseFloat(act.confidence) >= 0.7
                            ? "text-[#F57C00]"
                            : "text-[#D32F2F]"
                        }`}
                      >
                        {(parseFloat(act.confidence) * 100).toFixed(0)}%
                      </span>
                    ) : (
                      <span className="text-[#757575]">—</span>
                    )}
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <IsaBadge severity={act.validation_status} size="sm">
                      {act.validation_status}
                    </IsaBadge>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
