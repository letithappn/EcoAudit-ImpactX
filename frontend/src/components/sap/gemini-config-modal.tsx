"use client";

import React, { useState, useEffect } from "react";
import { X, Key, Sparkles, CheckCircle2, AlertCircle, Eye, EyeOff, Loader2, Cpu } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { AIStatusResponse } from "@/lib/types";

interface GeminiConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfigured?: (status: AIStatusResponse) => void;
}

export function GeminiConfigModal({ isOpen, onClose, onConfigured }: GeminiConfigModalProps) {
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [model, setModel] = useState("gemini-2.5-flash");
  const [currentStatus, setCurrentStatus] = useState<AIStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setFeedback(null);
    apiClient.getAIStatus()
      .then((res) => {
        setCurrentStatus(res);
        if (res.model) setModel(res.model);
      })
      .catch((err) => {
        console.error("Failed to load AI status:", err);
      });
  }, [isOpen]);

  if (!isOpen) return null;

  const handleTestConnection = async () => {
    if (!apiKey.trim()) {
      setFeedback({ type: "error", message: "Please enter an API Key to test." });
      return;
    }
    setIsTesting(true);
    setFeedback(null);
    try {
      const res = await apiClient.testAI({
        api_key: apiKey.trim(),
        model,
      });
      if (res.success) {
        setFeedback({
          type: "success",
          message: `${res.message}. Verified Gemini API connectivity.`,
        });
      } else {
        setFeedback({
          type: "error",
          message: `Connection failed: ${res.message}`,
        });
      }
    } catch (err: any) {
      setFeedback({
        type: "error",
        message: err.message || "Failed to test Gemini connection.",
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSaveAndActivate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      setFeedback({ type: "error", message: "Please enter a valid Gemini API Key." });
      return;
    }

    setIsLoading(true);
    setFeedback(null);

    try {
      const res = await apiClient.configureAI({
        api_key: apiKey.trim(),
        model,
      });

      const updatedStatus: AIStatusResponse = {
        configured: true,
        provider: "gemini",
        model: res.model,
        status: "active",
        message: res.message,
      };

      setCurrentStatus(updatedStatus);
      setFeedback({ type: "success", message: "Gemini API key configured and activated successfully!" });
      if (onConfigured) {
        onConfigured(updatedStatus);
      }
      setTimeout(() => {
        onClose();
      }, 1200);
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Failed to configure Gemini API." });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 select-none">
      <div className="bg-white rounded-xl shadow-2xl border border-[#CBD5E1] w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 text-xs">
        {/* Modal Header */}
        <div className="px-5 py-3.5 border-b border-[#E2E8F0] bg-[#FAFBFC] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-[#EBF3FF] border border-[#0070F2]/30 flex items-center justify-center text-[#0070F2]">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <div>
              <h3 className="font-bold text-[#1C2B36] text-sm">
                Google Gemini API Configuration
              </h3>
              <p className="text-[11px] text-[#556B82]">
                Enterprise AI Engine for Semantic Classification & Optimization
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-[#899AA8] hover:text-[#1C2B36] p-1 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSaveAndActivate} className="p-5 flex flex-col gap-4">
          {/* Status Banner */}
          <div
            className={`p-3 rounded-lg border flex items-center justify-between ${
              currentStatus?.configured
                ? "bg-[#F0FDF4] border-[#BBF7D0] text-[#166534]"
                : "bg-[#FFFBEB] border-[#FDE68A] text-[#92400E]"
            }`}
          >
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  currentStatus?.configured ? "bg-[#16A34A]" : "bg-[#D97706]"
                }`}
              />
              <span className="font-semibold">
                Status: {currentStatus?.configured ? "Gemini AI Active" : "Mock Engine (Offline)"}
              </span>
            </div>
            <span className="font-mono text-[11px] bg-white/70 px-2 py-0.5 rounded border border-current/20">
              {currentStatus?.model || "gemini-2.5-flash"}
            </span>
          </div>

          {/* Key Input */}
          <div>
            <label className="block text-[#1C2B36] font-semibold mb-1 flex items-center gap-1.5">
              <Key className="w-3.5 h-3.5 text-[#0070F2]" />
              <span>Gemini API Key:</span>
            </label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={
                  currentStatus?.configured
                    ? "•••••••••••••••••••••••••••••••• (Active)"
                    : "Enter your Google Gemini API Key (AIzaSy...)"
                }
                className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-2 pr-10 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none font-mono"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-2.5 top-2.5 text-[#899AA8] hover:text-[#1C2B36]"
              >
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-[11px] text-[#899AA8] mt-1">
              Your key is loaded into runtime memory for this server session to process classifications.
            </p>
          </div>

          {/* Model Selector */}
          <div>
            <label className="block text-[#1C2B36] font-semibold mb-1 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-[#0070F2]" />
              <span>Gemini Model Family:</span>
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-2 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
            >
              <option value="gemini-2.5-flash">
                gemini-2.5-flash (Recommended — Fast, Multimodal, High Reasoning)
              </option>
              <option value="gemini-2.0-flash">
                gemini-2.0-flash (Low Latency Classification)
              </option>
            </select>
          </div>

          {/* Feedback message */}
          {feedback && (
            <div
              className={`p-2.5 rounded text-xs flex items-center gap-2 ${
                feedback.type === "success"
                  ? "bg-[#F0FDF4] border border-[#BBF7D0] text-[#166534]"
                  : "bg-[#FEF2F2] border border-[#FCA5A5] text-[#DC2626]"
              }`}
            >
              {feedback.type === "success" ? (
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
              )}
              <span>{feedback.message}</span>
            </div>
          )}

          {/* Modal Actions */}
          <div className="pt-3 border-t border-[#E2E8F0] flex items-center justify-between">
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noreferrer"
              className="text-[#0070F2] hover:underline font-semibold text-[11px] flex items-center gap-1"
            >
              Get Gemini API Key &rarr;
            </a>

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
                onClick={handleTestConnection}
                disabled={isTesting || isLoading}
                className="px-3 py-1.5 border border-[#0070F2] text-[#0070F2] hover:bg-[#EBF3FF] rounded font-semibold transition-colors flex items-center gap-1.5 disabled:opacity-50"
              >
                {isTesting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                <span>Test Connection</span>
              </button>
              <button
                type="submit"
                disabled={isLoading || isTesting}
                className="px-4 py-1.5 bg-[#0070F2] hover:bg-[#0057D2] text-white rounded font-semibold transition-colors flex items-center gap-1.5 disabled:opacity-50"
              >
                {isLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                <span>Save & Activate</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
