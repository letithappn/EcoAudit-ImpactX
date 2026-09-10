"use client";

import React, { useState, useEffect } from "react";
import {
  Search,
  ExternalLink,
  ChevronRight,
  X,
  Calendar,
  MoreHorizontal,
  CheckSquare,
  Square,
  Copy,
  Sparkles,
} from "lucide-react";
import { RunSummaryResponse, ActivityDTO } from "@/lib/types";

interface InboundRow {
  id: string;
  product: string;
  supplier: string;
  activityStatus: "Requested" | "Not requested" | "Received";
  footprintStatus: "Valid" | "No Data";
  reasoning?: string | null;
  scope?: string | null;
  category?: string | null;
  quantity?: string | null;
  unit?: string | null;
  errors?: string[];
}

const DEFAULT_INBOUNDS: InboundRow[] = [
  { id: "1", product: "Frame Main (P123A)", supplier: "BikeTech (B2435)", activityStatus: "Requested", footprintStatus: "Valid" },
  { id: "2", product: "Frame Rear Triangle (B789C)", supplier: "BikeTech (B2435)", activityStatus: "Not requested", footprintStatus: "No Data" },
  { id: "3", product: "Seat Tube (X456Y)", supplier: "BikeTech (B2435)", activityStatus: "Not requested", footprintStatus: "No Data" },
  { id: "4", product: "Chainstays (M123N)", supplier: "BikeTech (B2435)", activityStatus: "Not requested", footprintStatus: "No Data" },
  { id: "5", product: "Fork Tube (C789D)", supplier: "ForkMaster (F1276)", activityStatus: "Requested", footprintStatus: "Valid" },
  { id: "6", product: "Fork Crown (Q456R)", supplier: "ForkMaster (F1276)", activityStatus: "Not requested", footprintStatus: "No Data" },
  { id: "7", product: "Steerer Tube (A789B)", supplier: "ForkMaster (F1276)", activityStatus: "Not requested", footprintStatus: "No Data" },
  { id: "8", product: "Lower Leg (K123L)", supplier: "ForkMaster (F1276)", activityStatus: "Requested", footprintStatus: "No Data" },
  { id: "9", product: "Handlebar Body (D789E)", supplier: "HandleTech (H9876)", activityStatus: "Received", footprintStatus: "Valid" },
  { id: "10", product: "Handlebar Grips (Y456Z)", supplier: "GripTech (G6654)", activityStatus: "Received", footprintStatus: "Valid" },
  { id: "11", product: "Handlebar Stem (E123F)", supplier: "StemPro (S6694)", activityStatus: "Received", footprintStatus: "Valid" },
  { id: "12", product: "Seatpost (L789M)", supplier: "CarbonRider (C6694)", activityStatus: "Received", footprintStatus: "Valid" },
  { id: "13", product: "Saddle (N456P)", supplier: "ComfyRide (C3594)", activityStatus: "Not requested", footprintStatus: "No Data" },
  { id: "14", product: "Pedals (G789H)", supplier: "PedalTech (P3324)", activityStatus: "Received", footprintStatus: "Valid" },
];

interface ProcessInboundsViewProps {
  summary?: RunSummaryResponse | null;
  activities?: ActivityDTO[];
}

export function ProcessInboundsView({ summary, activities }: ProcessInboundsViewProps) {
  const [inbounds, setInbounds] = useState<InboundRow[]>(DEFAULT_INBOUNDS);
  const [selectedId, setSelectedId] = useState<string>("2");
  const [checkedIds, setCheckedIds] = useState<Set<string>>(new Set(["2"]));
  const [activityStatusFilter, setActivityStatusFilter] = useState("All");
  const [footprintStatusFilter, setFootprintStatusFilter] = useState("All");
  const [commentText, setCommentText] = useState("");
  const [requestSent, setRequestSent] = useState(false);

  useEffect(() => {
    if (activities && activities.length > 0) {
      const mapped: InboundRow[] = activities.slice(0, 14).map((act, index) => {
        const row = act.original_row || {};
        const product = row["Item"] || row["Description"] || row["facility_name"] || act.activity_type || `Material Inbound #${index + 1}`;
        const supplier = row["Supplier"] || row["Vendor"] || (index % 2 === 0 ? "BikeTech (B2435)" : "ForkMaster (F1276)");
        const actStatus = act.validation_status === "validated" ? "Received" : act.validation_status === "review" ? "Requested" : "Not requested";
        const fpStatus = act.validation_status === "validated" ? "Valid" : "No Data";
        return {
          id: act.activity_id || `inbound-${index}`,
          product: `${product} (${act.activity_id || "PO_" + index})`,
          supplier,
          activityStatus: actStatus,
          footprintStatus: fpStatus,
          reasoning: act.reasoning,
          scope: act.scope,
          category: act.category,
          quantity: act.quantity,
          unit: act.unit,
          errors: act.validation_errors,
        };
      });
      if (mapped.length > 0) {
        setInbounds(mapped);
        setSelectedId(mapped[0].id);
        setCheckedIds(new Set([mapped[0].id]));
      }
    } else {
      setInbounds(DEFAULT_INBOUNDS);
    }
  }, [activities]);

  const selectedItem = inbounds.find((i) => i.id === selectedId) || inbounds[0];

  const toggleCheck = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setCheckedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const filteredInbounds = inbounds.filter((item) => {
    if (activityStatusFilter !== "All" && item.activityStatus !== activityStatusFilter) return false;
    if (footprintStatusFilter !== "All" && item.footprintStatus !== footprintStatusFilter) return false;
    return true;
  });

  const handleRequestFootprint = () => {
    setRequestSent(true);
    setInbounds((prev) =>
      prev.map((item) =>
        item.id === selectedItem.id ? { ...item, activityStatus: "Requested" } : item
      )
    );
    setTimeout(() => setRequestSent(false), 3000);
  };

  return (
    <div className="flex flex-col gap-5 max-w-7xl mx-auto w-full p-6 select-none">
      {/* 1. Header Filter Bar matching Image 2 */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-[#1C2B36]">Inbounds</h2>
          <button type="button" className="text-[#556B82] hover:text-[#0070F2]">
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div>
            <label className="block text-[#556B82] font-semibold mb-1">Product (ID):</label>
            <div className="relative">
              <input
                type="text"
                placeholder=""
                className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
              />
              <Copy className="w-3.5 h-3.5 text-[#899AA8] absolute right-2.5 top-2 cursor-pointer" />
            </div>
          </div>

          <div>
            <label className="block text-[#556B82] font-semibold mb-1">Supplier (ID):</label>
            <div className="relative">
              <input
                type="text"
                placeholder=""
                className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
              />
              <Copy className="w-3.5 h-3.5 text-[#899AA8] absolute right-2.5 top-2 cursor-pointer" />
            </div>
          </div>

          <div>
            <label className="block text-[#556B82] font-semibold mb-1">Activity Status:</label>
            <select
              value={activityStatusFilter}
              onChange={(e) => setActivityStatusFilter(e.target.value)}
              className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
            >
              <option value="All">All</option>
              <option value="Requested">Requested</option>
              <option value="Not requested">Not requested</option>
              <option value="Received">Received</option>
            </select>
          </div>

          <div>
            <label className="block text-[#556B82] font-semibold mb-1">Footprint Status:</label>
            <select
              value={footprintStatusFilter}
              onChange={(e) => setFootprintStatusFilter(e.target.value)}
              className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
            >
              <option value="All">All</option>
              <option value="Valid">Valid</option>
              <option value="No Data">No Data</option>
            </select>
          </div>
        </div>
      </div>

      {/* 2. Split Workspace: Inbounds Table (Left) + Detail Drawer (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Table Section (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden">
          <div className="px-5 py-3 border-b border-[#E2E8F0] bg-[#FAFBFC] flex items-center justify-between">
            <h3 className="text-xs font-semibold text-[#1C2B36]">
              Inbounds ({filteredInbounds.length})
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC] text-[#556B82] font-semibold">
                  <th className="py-2.5 px-3 w-8">
                    <input
                      type="checkbox"
                      checked={checkedIds.size === filteredInbounds.length}
                      onChange={(e) => {
                        if (e.target.checked) setCheckedIds(new Set(filteredInbounds.map((i) => i.id)));
                        else setCheckedIds(new Set());
                      }}
                      className="rounded accent-[#0070F2]"
                    />
                  </th>
                  <th className="py-2.5 px-3 font-semibold">Product (ID)</th>
                  <th className="py-2.5 px-3 font-semibold">Supplier (ID)</th>
                  <th className="py-2.5 px-3 font-semibold">Activity Status</th>
                  <th className="py-2.5 px-3 font-semibold">Footprint Status</th>
                  <th className="py-2.5 px-3 w-6"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9]">
                {filteredInbounds.map((row) => {
                  const isSelected = selectedId === row.id;
                  const isChecked = checkedIds.has(row.id);

                  return (
                    <tr
                      key={row.id}
                      onClick={() => setSelectedId(row.id)}
                      className={`hover:bg-[#F8FAFC] transition-colors cursor-pointer ${
                        isSelected ? "bg-[#EDF4FE] font-medium" : ""
                      }`}
                    >
                      <td className="py-2.5 px-3" onClick={(e) => toggleCheck(row.id, e)}>
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {}}
                          className="rounded accent-[#0070F2] cursor-pointer"
                        />
                      </td>
                      <td className="py-2.5 px-3 font-medium text-[#0070F2] hover:underline">
                        {row.product}
                      </td>
                      <td className="py-2.5 px-3 text-[#1C2B36]">
                        {row.supplier}
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`text-xs ${
                            row.activityStatus === "Requested"
                              ? "text-[#0070F2] font-semibold"
                              : row.activityStatus === "Received"
                              ? "text-[#16A34A] font-semibold"
                              : "text-[#556B82]"
                          }`}
                        >
                          {row.activityStatus}
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`text-xs ${
                            row.footprintStatus === "Valid"
                              ? "text-[#16A34A] font-semibold"
                              : "text-[#556B82]"
                          }`}
                        >
                          {row.footprintStatus}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-[#899AA8]">
                        <ChevronRight className="w-3.5 h-3.5" />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Detail Inspector Drawer matching Image 2 (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5 flex flex-col gap-5">
          {/* Drawer Header */}
          <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-3">
            <h3 className="text-base font-bold text-[#1C2B36]">
              {selectedItem.supplier.split(" ")[0]}
            </h3>
            <button
              type="button"
              className="text-[#899AA8] hover:text-[#1C2B36]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Section 1: Product Footprint Card */}
          <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg p-4 flex flex-col gap-3 text-xs">
            <h4 className="font-bold text-[#1C2B36]">Product Footprint</h4>

            <div>
              <span className="text-[#556B82] block text-[11px]">Product (ID):</span>
              <span className="font-semibold text-[#0070F2] hover:underline cursor-pointer">
                {selectedItem.product}
              </span>
            </div>

            <div>
              <span className="text-[#556B82] block text-[11px]">Footprint Status:</span>
              <span
                className={`font-semibold ${
                  selectedItem.footprintStatus === "Valid" ? "text-[#16A34A]" : "text-[#556B82]"
                }`}
              >
                {selectedItem.footprintStatus}
              </span>
            </div>
          </div>

          {/* Section 2: Inbound Process Card */}
          <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg p-4 flex flex-col gap-3 text-xs">
            <h4 className="font-bold text-[#1C2B36]">Inbound Process</h4>

            <div>
              <span className="text-[#556B82] block text-[11px]">Activity Status:</span>
              <span className="text-[#1C2B36] font-semibold">{selectedItem.activityStatus}</span>
            </div>

            <div>
              <label className="text-[#556B82] block text-[11px] mb-1">Comment:</label>
              <textarea
                rows={2}
                placeholder="Add a comment"
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                className="w-full bg-white border border-[#CBD5E1] rounded p-2 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
              />
            </div>

            <div className="flex items-center gap-2 pt-1">
              <button
                type="button"
                onClick={handleRequestFootprint}
                className="flex-1 px-4 py-2 bg-[#0070F2] hover:bg-[#0057D2] text-white rounded font-semibold text-xs transition-colors shadow-sm"
              >
                {requestSent ? "Request Sent ✓" : "Request Footprint"}
              </button>
              <button
                type="button"
                className="p-2 bg-white border border-[#CBD5E1] rounded hover:bg-[#F1F5F9] text-[#556B82]"
              >
                <MoreHorizontal className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Section 3: AI Semantic Trace & Classification Reasoning */}
          {selectedItem.reasoning && (
            <div className="bg-[#F8FAFC] border border-[#BFDBFE] rounded-lg p-4 flex flex-col gap-2.5 text-xs">
              <div className="flex items-center gap-1.5 text-[#0070F2] font-bold">
                <Sparkles className="w-3.5 h-3.5" />
                <h4>AI Classification & Audit Reasoning</h4>
              </div>
              <p className="p-2.5 bg-white border border-[#CBD5E1] rounded text-[11px] text-[#1C2B36] font-mono leading-relaxed break-words">
                {selectedItem.reasoning}
              </p>
              {selectedItem.scope && (
                <div className="flex items-center gap-2 pt-0.5">
                  <span className="px-2 py-0.5 bg-[#EBF3FF] border border-[#BFDBFE] text-[#0070F2] rounded text-[10px] font-semibold">
                    {selectedItem.scope}
                  </span>
                  {selectedItem.category && (
                    <span className="px-2 py-0.5 bg-[#F1F5F9] border border-[#E2E8F0] text-[#556B82] rounded text-[10px]">
                      {selectedItem.category}
                    </span>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Section 4: Activity Timeline Card */}
          <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg p-4 flex flex-col gap-2 text-xs">
            <h4 className="font-bold text-[#1C2B36]">Activity</h4>
            <div className="flex items-center gap-3 py-2 text-[#556B82]">
              <div className="w-8 h-8 rounded bg-[#EBF3FF] border border-[#0070F2]/30 flex items-center justify-center text-[#0070F2]">
                <Calendar className="w-4 h-4" />
              </div>
              <span className="text-xs">No activity so far</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
