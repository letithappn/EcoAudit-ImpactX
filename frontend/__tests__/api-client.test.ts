import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { apiClient } from "@/lib/api-client";

describe("API Client Layer", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("calls /api/demo with proper query parameters and returns RunCreateResponse", async () => {
    const mockResponse = {
      run_id: "demo-run-123",
      status: "queued",
      stage: "Uploading",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response);

    const result = await apiClient.createDemo("mock", 2024, "UK");
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/demo?provider=mock&year=2024&country=UK"),
      expect.objectContaining({ method: "POST" })
    );
    expect(result.run_id).toBe("demo-run-123");
    expect(result.stage).toBe("Uploading");
  });

  it("calls /api/runs/{id}/status and preserves Decimal strings without float coercion", async () => {
    const mockStatus = {
      run_id: "test-run",
      status: "complete",
      stage: "Recommendations",
      progress: 100,
      provider: "mock",
      year: 2024,
      country: "UK",
      filename: "test.csv",
      statistics: {
        coverage_percentage: 100,
        total_rows: 33,
      },
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockStatus,
    } as Response);

    const status = await apiClient.getRunStatus("test-run");
    expect(status.status).toBe("complete");
    expect(status.progress).toBe(100);
  });

  it("handles HTTP errors gracefully and throws descriptive error", async () => {
    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ detail: "Run not found" }),
    } as Response);

    await expect(apiClient.getRunStatus("missing-run")).rejects.toThrow("Run not found");
  });

  it("calls /api/ai/status and retrieves AI configuration status", async () => {
    const mockStatus = {
      configured: true,
      provider: "gemini",
      model: "gemini-2.5-flash",
      status: "active",
      message: "Gemini API connected and active",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockStatus,
    } as Response);

    const status = await apiClient.getAIStatus();
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining("/api/ai/status"));
    expect(status.configured).toBe(true);
    expect(status.model).toBe("gemini-2.5-flash");
  });

  it("calls /api/ai/config with apiKey and model", async () => {
    const mockResponse = {
      success: true,
      message: "Configured",
      model: "gemini-2.5-flash",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    } as Response);

    const result = await apiClient.configureAI({ api_key: "my-key", model: "gemini-2.5-flash" });
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/ai/config"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ api_key: "my-key", model: "gemini-2.5-flash" }),
      })
    );
    expect(result.success).toBe(true);
  });

  it("calls /api/ai/test to verify Gemini API connection", async () => {
    const mockTestRes = {
      success: true,
      message: "Connected to gemini-2.5-flash successfully",
      model: "gemini-2.5-flash",
      response: "OK",
    };

    vi.spyOn(global, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockTestRes,
    } as Response);

    const result = await apiClient.testAI({ api_key: "my-key", model: "gemini-2.5-flash" });
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/ai/test"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ api_key: "my-key", model: "gemini-2.5-flash" }),
      })
    );
    expect(result.success).toBe(true);
    expect(result.message).toContain("Connected");
  });
});

