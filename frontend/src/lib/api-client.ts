import {
  ActivitiesResponse,
  AIConfigRequest,
  AIConfigResponse,
  AIStatusResponse,
  AITestRequest,
  AITestResponse,
  EvidenceResponse,
  RecommendationsResponse,
  RunCreateResponse,
  RunStatusResponse,
  RunSummaryResponse,
  ScenarioRequest,
  ScenarioResponse,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public detail: string
  ) {
    super(detail || `API Error ${status}: ${statusText}`);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = "";
    try {
      const data = await res.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await res.text();
    }
    throw new ApiError(res.status, res.statusText, detail);
  }
  return res.json() as Promise<T>;
}

export const apiClient = {
  async health(): Promise<{ status: string }> {
    const res = await fetch(`${BASE_URL}/api/health`);
    return handleResponse(res);
  },

  async createRun(
    file: File,
    provider: "mock" | "gemini" = "mock",
    year = 2024,
    country = "UK"
  ): Promise<RunCreateResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const query = new URLSearchParams({
      provider,
      year: year.toString(),
      country,
    });

    const res = await fetch(`${BASE_URL}/api/runs?${query}`, {
      method: "POST",
      body: formData,
    });
    return handleResponse<RunCreateResponse>(res);
  },

  async createDemo(
    provider: "mock" | "gemini" = "mock",
    year = 2024,
    country = "UK",
    preset: "competition" | "chicago" | "synthetic" = "competition"
  ): Promise<RunCreateResponse> {
    const query = new URLSearchParams({
      provider,
      year: year.toString(),
      country,
      preset,
    });

    const res = await fetch(`${BASE_URL}/api/demo?${query}`, {
      method: "POST",
    });
    return handleResponse<RunCreateResponse>(res);
  },

  async listRuns(): Promise<
    Array<{
      run_id: string;
      filename: string;
      status: string;
      stage: string;
      progress: number;
      provider: string;
      year: number;
      country: string;
    }>
  > {
    const res = await fetch(`${BASE_URL}/api/runs`);
    return handleResponse(res);
  },

  async getRunStatus(runId: string): Promise<RunStatusResponse> {
    const res = await fetch(`${BASE_URL}/api/runs/${encodeURIComponent(runId)}/status`);
    return handleResponse<RunStatusResponse>(res);
  },

  async getRunSummary(runId: string): Promise<RunSummaryResponse> {
    const res = await fetch(`${BASE_URL}/api/runs/${encodeURIComponent(runId)}/summary`);
    return handleResponse<RunSummaryResponse>(res);
  },

  async getActivities(
    runId: string,
    options: { offset?: number; limit?: number; status?: string } = {}
  ): Promise<ActivitiesResponse> {
    const query = new URLSearchParams();
    if (options.offset !== undefined) query.set("offset", options.offset.toString());
    if (options.limit !== undefined) query.set("limit", options.limit.toString());
    if (options.status) query.set("status", options.status);

    const qs = query.toString() ? `?${query}` : "";
    const res = await fetch(
      `${BASE_URL}/api/runs/${encodeURIComponent(runId)}/activities${qs}`
    );
    return handleResponse<ActivitiesResponse>(res);
  },

  async getEvidence(runId: string): Promise<EvidenceResponse> {
    const res = await fetch(`${BASE_URL}/api/runs/${encodeURIComponent(runId)}/evidence`);
    return handleResponse<EvidenceResponse>(res);
  },

  async createScenario(
    runId: string,
    request: ScenarioRequest
  ): Promise<ScenarioResponse> {
    const res = await fetch(
      `${BASE_URL}/api/runs/${encodeURIComponent(runId)}/scenarios`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      }
    );
    return handleResponse<ScenarioResponse>(res);
  },

  async getRecommendations(runId: string): Promise<RecommendationsResponse> {
    const res = await fetch(
      `${BASE_URL}/api/runs/${encodeURIComponent(runId)}/recommendations`
    );
    return handleResponse<RecommendationsResponse>(res);
  },

  async getAIStatus(): Promise<AIStatusResponse> {
    const res = await fetch(`${BASE_URL}/api/ai/status`);
    return handleResponse<AIStatusResponse>(res);
  },

  async configureAI(request: AIConfigRequest): Promise<AIConfigResponse> {
    const res = await fetch(`${BASE_URL}/api/ai/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    return handleResponse<AIConfigResponse>(res);
  },

  async testAI(request: AITestRequest): Promise<AITestResponse> {
    const res = await fetch(`${BASE_URL}/api/ai/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    return handleResponse<AITestResponse>(res);
  },
};

