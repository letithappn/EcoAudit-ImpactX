"use client";

import React, { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileCheck, AlertCircle, Play, Settings, Database } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { IsaCard } from "@/components/ui/isa-card";
import { SboButton } from "@/components/ui/sbo-button";

interface CsvUploaderProps {
  onDemoSubmit?: () => Promise<{ run_id: string }>;
}

export function CsvUploader({ onDemoSubmit }: CsvUploaderProps) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [provider, setProvider] = useState<"mock" | "gemini">("mock");
  const [year, setYear] = useState<number>(2024);
  const [country, setCountry] = useState<string>("UK");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (!selected.name.toLowerCase().endsWith(".csv")) {
        setError("Only .csv files are supported under ISO 14064 ingestion specs");
        return;
      }
      setFile(selected);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      if (!dropped.name.toLowerCase().endsWith(".csv")) {
        setError("Only .csv files are supported");
        return;
      }
      setFile(dropped);
      setError(null);
    }
  };

  const handleUploadSubmit = async () => {
    if (!file) {
      setError("Please select or drop a valid CSV file");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const res = await apiClient.createRun(file, provider, year, country);
      router.push(`/runs/${res.run_id}`);
    } catch (err: any) {
      setError(err.message || "Failed to initiate carbon pipeline run");
      setIsSubmitting(false);
    }
  };

  const handleDemoTrigger = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      if (onDemoSubmit) {
        const res = await onDemoSubmit();
        router.push(`/runs/${res.run_id}`);
        return;
      }
      const res = await apiClient.createDemo(provider, year, country);
      router.push(`/runs/${res.run_id}`);
    } catch (err: any) {
      setError(err.message || "Failed to initiate competition demo run");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col gap-6">
      {/* Run Parameters Configurator */}
      <IsaCard
        title="Execution Parameters"
        subtitle="Configure classification engine and geographical emission registry"
      >
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
          <div>
            <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
              AI Classification Provider
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as any)}
              className="w-full bg-[#2B2B2B] border border-[#4A4A4A] rounded px-3 py-2 text-[#E0E0E0] focus:border-[#00ACC1] focus:outline-none"
            >
              <option value="mock">Mock Provider (Deterministic Offline)</option>
              <option value="gemini">Gemini Vision/Multimodal AI (Live)</option>
            </select>
          </div>

          <div>
            <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
              Accounting Period (Year)
            </label>
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value) || 2024)}
              className="w-full bg-[#2B2B2B] border border-[#4A4A4A] rounded px-3 py-2 text-[#E0E0E0] focus:border-[#00ACC1] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
              Regional Registry / Grid
            </label>
            <select
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              className="w-full bg-[#2B2B2B] border border-[#4A4A4A] rounded px-3 py-2 text-[#E0E0E0] focus:border-[#00ACC1] focus:outline-none"
            >
              <option value="UK">UK (DESNZ / DEFRA 2024)</option>
              <option value="Egypt">Egypt (EEAA / NREA 0.458 tCO2e/MWh)</option>
              <option value="Germany">Germany (UBA Grid Factor)</option>
            </select>
          </div>
        </div>
      </IsaCard>

      {/* Main Drag-and-Drop Ingestion Canvas */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-all ${
          isDragOver
            ? "border-[#00ACC1] bg-[#00ACC1]/5"
            : file
            ? "border-[#43A047]/80 bg-[#1B3A24]/10"
            : "border-[#4A4A4A] bg-[#333333]/40 hover:border-[#757575] hover:bg-[#383838]/60"
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
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-[#1B3A24] border border-[#43A047] flex items-center justify-center text-[#43A047]">
              <FileCheck className="w-6 h-6" />
            </div>
            <div>
              <p className="font-mono text-sm font-semibold text-[#E0E0E0]">
                {file.name}
              </p>
              <p className="text-xs text-[#9E9E9E] mt-1 font-mono">
                {(file.size / 1024).toFixed(1)} KB • Ready for Validation Firewall
              </p>
            </div>
            <span className="text-[11px] text-[#00ACC1] underline mt-1">
              Click or drop another file to replace
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-[#2B2B2B] border border-[#4A4A4A] flex items-center justify-center text-[#9E9E9E]">
              <Upload className="w-6 h-6 text-[#00ACC1]" />
            </div>
            <div>
              <p className="text-base font-semibold text-[#E0E0E0]">
                Drag & drop facility activity CSV file here
              </p>
              <p className="text-xs text-[#9E9E9E] mt-1 font-mono">
                Supports fuel receipts, utility meterings, procurement & travel ledgers (up to 50MB)
              </p>
            </div>
            <div className="px-3 py-1 bg-[#424242] text-[#E0E0E0] border border-[#555555] rounded text-xs font-mono">
              Browse Local Files
            </div>
          </div>
        )}
      </div>

      {/* Error Alarm Bar */}
      {error && (
        <div className="p-3 bg-[#3B1111] border border-[#D32F2F] rounded text-xs font-mono text-[#D32F2F] flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Action Triggers: Custom Run vs 1-Click Competition Benchmark */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleDemoTrigger}
            disabled={isSubmitting}
            className="flex items-center gap-2 px-5 py-2.5 rounded bg-[#2E3B33] hover:bg-[#394B40] text-[#A5D6A7] border border-[#43A047]/60 font-mono text-xs font-bold uppercase tracking-wider transition-all disabled:opacity-50"
          >
            <Database className="w-4 h-4 text-[#43A047]" />
            <span>Load Competition Demo (33 Activities)</span>
          </button>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {file && (
            <SboButton
              onConfirm={handleUploadSubmit}
              disabled={isSubmitting}
              className="w-full sm:w-auto"
            >
              {isSubmitting ? "Executing Pipeline..." : "Execute Calculation Pipeline"}
            </SboButton>
          )}
        </div>
      </div>
    </div>
  );
}
