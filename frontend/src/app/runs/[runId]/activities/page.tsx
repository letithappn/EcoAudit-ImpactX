"use client";

import React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { IsaCard } from "@/components/ui/isa-card";
import { ActivityTable } from "@/components/activities/activity-table";

export default function ActivitiesPage() {
  const params = useParams();
  const runId = String(params?.runId || "");

  return (
    <div className="flex-1 p-6 max-w-7xl mx-auto w-full flex flex-col gap-6">
      <div className="flex items-center gap-3">
        <Link
          href={`/runs/${runId}`}
          className="p-1.5 rounded bg-[#383838] border border-[#4A4A4A] text-[#9E9E9E] hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-xl font-bold font-mono text-[#FFFFFF]">
            Facility Activity Ledger
          </h1>
          <p className="text-xs font-mono text-[#9E9E9E] mt-0.5">
            Run ID: {runId}
          </p>
        </div>
      </div>

      <IsaCard
        title="Activity Records & Validation Audit"
        subtitle="Individual line-item emissions, factors applied, and physical validation checks"
      >
        <ActivityTable runId={runId} />
      </IsaCard>
    </div>
  );
}
