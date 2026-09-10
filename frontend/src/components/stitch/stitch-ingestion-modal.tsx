"use client";

import React, { useState, useRef } from "react";
import { apiClient } from "@/lib/api-client";
import { RunCreateResponse } from "@/lib/types";

interface StitchIngestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRunCreated: (res: RunCreateResponse) => void;
  isGeminiActive?: boolean;
}

export function StitchIngestionModal({
  isOpen,
  onClose,
  onRunCreated,
  isGeminiActive = false,
}: StitchIngestionModalProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [provider, setProvider] = useState<"gemini" | "mock">(
    isGeminiActive ? "gemini" : "mock"
  );
  const [year, setYear] = useState(2024);
  const [country, setCountry] = useState("Egypt");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processSelectedFile(e.target.files[0]);
    }
  };

  const processSelectedFile = (selected: File) => {
    if (!selected.name.toLowerCase().endsWith(".csv")) {
      setError("Only .csv activity and invoice files are supported");
      return;
    }
    setFile(selected);
    setError(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleUploadSubmit = async () => {
    if (!file) {
      setError("Please select or drop a valid CSV file");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await apiClient.createRun(file, provider, year, country);
      onRunCreated(res);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to start pipeline run");
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuickLoad = async (preset: "competition" | "chicago", label: string) => {
    setSubmitting(true);
    setError(null);
    try {
      const selectedCountry = preset === "chicago" ? "UK" : country;
      const res = await apiClient.createDemo(provider, year, selectedCountry, preset);
      onRunCreated(res);
      onClose();
    } catch (err: any) {
      setError(err.message || `Failed to load ${label}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-surface-container-lowest rounded-2xl shadow-2xl border border-outline-variant/30 w-full max-w-xl overflow-hidden animate-in fade-in zoom-in-95 text-on-surface">
        {/* Modal Header */}
        <div className="px-space-xl py-space-md border-b border-outline-variant/20 bg-surface-container-low/40 flex items-center justify-between">
          <div className="flex items-center gap-space-sm">
            <div className="w-7 h-7 rounded-lg bg-secondary text-white flex items-center justify-center">
              <span className="material-symbols-outlined text-[18px]">upload_file</span>
            </div>
            <div className="flex flex-col">
              <h3 className="font-headline-md text-headline-md font-bold text-on-surface">
                New Ingestion &amp; Audit Run
              </h3>
              <span className="font-body-sm text-body-sm text-on-surface-variant">
                GHG Protocol Double-Entry Ingestion Pipeline
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-on-surface-variant hover:bg-surface-container-high transition-colors"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-space-xl flex flex-col gap-space-lg">
          {/* Quick-Load Datasets (Option A) */}
          <div className="flex flex-col gap-space-xs">
            <div className="flex items-center justify-between">
              <label className="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold flex items-center gap-space-xs">
                <span className="material-symbols-outlined text-[16px] text-secondary">
                  dataset
                </span>
                <span>Quick-Load Sample Datasets (1-Click)</span>
              </label>
              <span className="font-mono-data text-[11px] text-on-tertiary-container bg-tertiary-fixed/20 px-space-xs py-[2px] rounded font-semibold">
                Instant Verification
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-sm mt-1">
              <button
                type="button"
                disabled={submitting}
                onClick={() => handleQuickLoad("competition", "Egypt Heavy Industry")}
                className="flex flex-col p-space-sm rounded-xl border border-outline-variant/40 bg-surface-container-low/50 hover:bg-surface-container-high/40 hover:border-secondary transition-all text-left group"
              >
                <div className="flex items-center justify-between">
                  <span className="font-label-md text-label-md text-on-surface font-semibold group-hover:text-secondary">
                    Egypt Heavy Industry
                  </span>
                  <span className="material-symbols-outlined text-[16px] text-secondary opacity-0 group-hover:opacity-100 transition-opacity">
                    play_circle
                  </span>
                </div>
                <span className="font-body-sm text-body-sm text-on-surface-variant text-[11px] mt-0.5">
                  Steel, aluminum smelting &amp; direct combustion Scope 1-3
                </span>
              </button>

              <button
                type="button"
                disabled={submitting}
                onClick={() => handleQuickLoad("chicago", "Chicago Energy Benchmark")}
                className="flex flex-col p-space-sm rounded-xl border border-outline-variant/40 bg-surface-container-low/50 hover:bg-surface-container-high/40 hover:border-secondary transition-all text-left group"
              >
                <div className="flex items-center justify-between">
                  <span className="font-label-md text-label-md text-on-surface font-semibold group-hover:text-secondary">
                    Chicago Energy Benchmark
                  </span>
                  <span className="material-symbols-outlined text-[16px] text-secondary opacity-0 group-hover:opacity-100 transition-opacity">
                    play_circle
                  </span>
                </div>
                <span className="font-body-sm text-body-sm text-on-surface-variant text-[11px] mt-0.5">
                  Real municipal telemetry, natural gas &amp; commercial electricity (28k rows)
                </span>
              </button>
            </div>
          </div>

          {/* Divider */}
          <div className="relative flex items-center justify-center">
            <div className="w-full border-t border-outline-variant/30" />
            <span className="absolute bg-surface-container-lowest px-space-md font-mono-data text-[11px] uppercase tracking-wider text-on-surface-variant">
              Or Upload Custom CSV
            </span>
          </div>

          {/* Drag & Drop Box */}
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-space-xl flex flex-col items-center justify-center cursor-pointer transition-all text-center select-none ${
              dragOver
                ? "border-secondary bg-surface-container-high/50"
                : file
                ? "border-on-tertiary-container bg-tertiary-container/5"
                : "border-outline-variant/60 hover:border-secondary bg-surface-container-low/30 hover:bg-surface-container-low/60"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
            {file ? (
              <div className="flex flex-col items-center gap-space-xs">
                <span className="material-symbols-outlined text-[36px] text-on-tertiary-container">
                  task_alt
                </span>
                <span className="font-label-md text-label-md text-on-surface font-semibold">
                  {file.name}
                </span>
                <span className="font-mono-data text-[11px] text-on-surface-variant">
                  {(file.size / 1024).toFixed(1)} KB • Click to choose another file
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-space-xs">
                <span className="material-symbols-outlined text-[36px] text-secondary">
                  cloud_upload
                </span>
                <span className="font-label-md text-label-md text-on-surface font-semibold">
                  Drag and drop your activity CSV file here
                </span>
                <span className="font-body-sm text-body-sm text-on-surface-variant text-[11px]">
                  Supports Scope 1 direct fuels, Scope 2 power bills, Scope 3 purchased goods
                </span>
              </div>
            )}
          </div>

          {/* Parameters Configuration */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-space-md">
            <div className="flex flex-col gap-space-2xs">
              <label className="font-label-sm text-label-sm text-on-surface-variant font-semibold">
                Grid / Emission Factor Authority:
              </label>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="bg-surface-container-low border border-outline-variant/40 rounded-lg px-space-md py-space-xs font-body-md text-body-md text-on-surface focus:outline-none focus:border-secondary"
              >
                <option value="Egypt">Egypt (EEAA Grid 0.458 tCO2e/MWh)</option>
                <option value="UK">UK (DESNZ / DEFRA 2024)</option>
                <option value="Germany">EU Germany (UBA Benchmarks)</option>
              </select>
            </div>

            <div className="flex flex-col gap-space-2xs">
              <label className="font-label-sm text-label-sm text-on-surface-variant font-semibold">
                AI Classification Provider:
              </label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value as any)}
                className="bg-surface-container-low border border-outline-variant/40 rounded-lg px-space-md py-space-xs font-body-md text-body-md text-on-surface focus:outline-none focus:border-secondary"
              >
                <option value="gemini">Google Gemini 2.5 Flash (Live LLM)</option>
                <option value="mock">Deterministic Rule Engine (Offline)</option>
              </select>
            </div>
          </div>

          {/* Error notice */}
          {error && (
            <div className="p-space-sm bg-error-container text-on-error-container rounded-lg font-body-sm text-body-sm flex items-center gap-space-xs">
              <span className="material-symbols-outlined text-[18px]">error</span>
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-space-xl py-space-md border-t border-outline-variant/20 bg-surface-container-low/40 flex items-center justify-between">
          <span className="font-mono-data text-[11px] text-on-surface-variant">
            ISO 14064-1 Compliant • SHA-256 Verified
          </span>
          <div className="flex items-center gap-space-sm">
            <button
              type="button"
              onClick={onClose}
              className="px-space-md py-space-xs rounded-lg font-label-md text-label-md text-on-surface-variant hover:bg-surface-container-high transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={!file || submitting}
              onClick={handleUploadSubmit}
              className="flex items-center gap-space-xs bg-secondary hover:bg-secondary/90 disabled:opacity-50 text-on-secondary px-space-lg py-space-xs rounded-lg font-label-md text-label-md font-semibold transition-all shadow-sm"
            >
              {submitting ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Executing Pipeline...</span>
                </>
              ) : (
                <>
                  <span className="material-symbols-outlined text-[18px]">rocket_launch</span>
                  <span>Upload &amp; Calculate</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
