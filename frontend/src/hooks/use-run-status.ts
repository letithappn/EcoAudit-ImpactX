"use client";

import { useState, useEffect, useRef } from "react";
import { apiClient } from "@/lib/api-client";
import { RunStatusResponse } from "@/lib/types";

export function useRunStatus(runId: string | null, intervalMs = 600) {
  const [data, setData] = useState<RunStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const activeRef = useRef(true);

  useEffect(() => {
    if (!runId) {
      setIsLoading(false);
      return;
    }

    activeRef.current = true;
    setIsLoading(true);
    setError(null);

    let timer: NodeJS.Timeout;

    const poll = async () => {
      try {
        const res = await apiClient.getRunStatus(runId);
        if (!activeRef.current) return;
        setData(res);
        setIsLoading(false);

        const isFinished =
          res.status === "complete" ||
          res.status === "complete_with_review" ||
          res.status === "failed";

        if (!isFinished) {
          timer = setTimeout(poll, intervalMs);
        }
      } catch (err: any) {
        if (!activeRef.current) return;
        setError(err.message || "Failed to fetch run status");
        setIsLoading(false);
      }
    };

    poll();

    return () => {
      activeRef.current = false;
      clearTimeout(timer);
    };
  }, [runId, intervalMs]);

  const isComplete =
    data?.status === "complete" || data?.status === "complete_with_review";
  const isFailed = data?.status === "failed";

  return { data, error, isLoading, isComplete, isFailed };
}
