"use client";

import React, { useState, useRef } from "react";
import { X, Upload, FileCheck, Play, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { RunCreateResponse } from "@/lib/types";

interface IngestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRunCreated: (res: RunCreateResponse) => void;
}

export function IngestionModal({ isOpen, onClose, onRunCreated }: IngestionModalProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [provider, setProvider] = useState<"gemini" | "mock">("gemini");
  const [year, setYear] = useState(2024);
  const [country, setCountry] = useState("Egypt");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (!selected.name.toLowerCase().endsWith(".csv")) {
        setError("Only .csv activity files are supported");
        return;
      }
      setFile(selected);
      setError(null);
    }
  };

  const handleUploadSubmit = async () => {
    if (!file) {
      setError("Please select a valid CSV file");
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
      setSubmitting(false);
    }
  };

  const handleDemoSubmit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await apiClient.createDemo(provider, year, country);
      onRunCreated(res);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to start demo pipeline");
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl border border-[#CBD5E1] w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 text-xs select-none">
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-[#E2E8F0] bg-[#FAFBFC] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="px-2 py-0.5 bg-[#0070F2] text-white font-bold text-xs rounded">
              SAP
            </div>
            <h3 className="font-bold text-[#1C2B36]">
              Process Activity Ingestion & Ledger Run
            </h3>
          </div>
          <button type="button" onClick={onClose} className="text-[#899AA8] hover:text-[#1C2B36]">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 flex flex-col gap-4">
          {/* Config Parameters */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[#556B82] font-semibold mb-1">AI Classifier:</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value as any)}
                className="w-full bg-white border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
              >
                <option value="gemini">Gemini Vision AI (Live API Key)</option>
                <option value="mock">Deterministic Mock AI (Offline)</option>
              </select>
            </div>

            <div>
              <label className="block text-[#556B82] font-semibold mb-1">Grid / Region:</label>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full bg-white border border-[#CBD5E1] rounded px-2.5 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
              >
                <option value="Egypt">Egypt (EEAA 0.458 tCO2e/MWh)</option>
                <option value="UK">UK (DESNZ / DEFRA 2024)</option>
                <option value="Germany">Germany (UBA Factor)</option>
              </select>
            </div>
          </div>

          {/* Drag and Drop Box */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-[#CBD5E1] hover:border-[#0070F2] bg-[#F8FAFC] rounded-lg p-6 flex flex-col items-center justify-center cursor-pointer transition-all text-center"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <FileCheck className="w-8 h-8 text-[#16A34A]" />
                <span className="font-semibold text-[#1C2B36]">{file.name}</span>
                <span className="text-[11px] text-[#899AA8]">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <Upload className="w-8 h-8 text-[#0070F2]" />
                <span className="font-semibold text-[#1C2B36]">Click or drag facility activity CSV here</span>
                <span className="text-[11px] text-[#899AA8]">Supports Scope 1 direct fuels, Scope 2 power bills, Scope 3 supplies</span>
              </div>
            )}
          </div>

          {error && (
            <div className="p-2.5 bg-[#FEF2F2] border border-[#FCA5A5] text-[#DC2626] rounded flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Quick Demo Trigger Button */}
          <div className="pt-2 border-t border-[#E2E8F0] flex items-center justify-between">
            <button
              type="button"
              onClick={handleDemoSubmit}
              disabled={submitting}
              className="px-3 py-1.5 bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#1C2B36] rounded font-semibold transition-colors flex items-center gap-1.5"
            >
              <Play className="w-3 h-3 text-[#16A34A] fill-current" />
              <span>Load 33-Row Benchmark Demo</span>
            </button>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 border border-[#CBD5E1] rounded text-[#556B82] hover:bg-[#F8FAFC]"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleUploadSubmit}
                disabled={submitting || !file}
                className="px-4 py-1.5 bg-[#0070F2] hover:bg-[#0057D2] text-white rounded font-semibold transition-colors disabled:opacity-50"
              >
                {submitting ? "Starting..." : "Start Ingestion"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
