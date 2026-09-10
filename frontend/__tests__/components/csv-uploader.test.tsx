import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import { CsvUploader } from "@/components/upload/csv-uploader";

// Mock next/navigation useRouter
const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe("CsvUploader Component", () => {
  it("renders upload zone and competition demo trigger", () => {
    render(<CsvUploader />);
    expect(screen.getByText(/Drag & drop facility activity CSV/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Load Competition Demo/i })).toBeInTheDocument();
  });

  it("triggers demo run on one-click demo button", async () => {
    const mockCreateDemo = vi.fn().mockResolvedValue({
      run_id: "demo-test-run-456",
      status: "queued",
      stage: "Uploading",
    });

    render(<CsvUploader onDemoSubmit={mockCreateDemo} />);
    const demoButton = screen.getByRole("button", { name: /Load Competition Demo/i });
    fireEvent.click(demoButton);

    expect(mockCreateDemo).toHaveBeenCalled();
  });
});
