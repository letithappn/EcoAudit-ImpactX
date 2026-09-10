"use client";

import React, { useState } from "react";
import { ActivityDTO, ScenarioRequest, ScenarioResponse } from "@/lib/types";
import { apiClient } from "@/lib/api-client";
import { IsaCard } from "@/components/ui/isa-card";
import { SboButton } from "@/components/ui/sbo-button";
import { Sparkles, Sliders, AlertCircle, ArrowRight } from "lucide-react";

interface ScenarioFormProps {
  runId: string;
  activities: ActivityDTO[];
  onScenarioCreated: (res: ScenarioResponse) => void;
}

export function ScenarioForm({
  runId,
  activities,
  onScenarioCreated,
}: ScenarioFormProps) {
  const [name, setName] = useState("Industrial Energy Efficiency Overhaul");
  const [description, setDescription] = useState("Simulated 20% efficiency gains on thermal combustion assets");
  const [interventionType, setInterventionType] = useState<
    "PercentageReduction" | "AbsoluteReduction" | "FuelSubstitution"
  >("PercentageReduction");

  const [reductionPercentage, setReductionPercentage] = useState("20");
  const [reductionAmount, setReductionAmount] = useState("1000");

  // Fuel substitution state
  const [newActivityType, setNewActivityType] = useState("electricity_grid");
  const [newUnit, setNewUnit] = useState("kwh");
  const [newScope, setNewScope] = useState("Scope 2");
  const [newCategory, setNewCategory] = useState("Electricity");
  const [conversionMultiplier, setConversionMultiplier] = useState("1.0");
  const [newUnitPrice, setNewUnitPrice] = useState("");

  const [selectedActivityIds, setSelectedActivityIds] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Quick action: select top 5 validated activities
  const handleSelectTop = () => {
    const valid = activities
      .filter((a) => a.activity_id && a.validation_status === "validated")
      .slice(0, 5)
      .map((a) => a.activity_id as string);
    setSelectedActivityIds(valid);
  };

  const handleToggleActivity = (id: string) => {
    setSelectedActivityIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleSubmit = async () => {
    if (selectedActivityIds.length === 0) {
      setError("Please select at least one target activity to apply the intervention to");
      return;
    }

    setSubmitting(true);
    setError(null);

    const request: ScenarioRequest = {
      name,
      description,
      target_activity_ids: selectedActivityIds,
      intervention_type: interventionType,
      ...(interventionType === "PercentageReduction"
        ? { reduction_percentage: reductionPercentage }
        : {}),
      ...(interventionType === "AbsoluteReduction"
        ? { reduction_amount: reductionAmount }
        : {}),
      ...(interventionType === "FuelSubstitution"
        ? {
            new_activity_type: newActivityType,
            new_unit: newUnit,
            new_scope: newScope,
            new_category: newCategory,
            conversion_multiplier: conversionMultiplier,
            new_unit_price: newUnitPrice || undefined,
          }
        : {}),
    };

    try {
      const res = await apiClient.createScenario(runId, request);
      onScenarioCreated(res);
      setSubmitting(false);
    } catch (err: any) {
      setError(err.message || "Failed to evaluate deterministic scenario");
      setSubmitting(false);
    }
  };

  return (
    <IsaCard
      title="What-If Decarbonization Scenario Builder"
      subtitle="Deterministic mathematical modeling of industrial interventions and Capex payback"
    >
      <div className="flex flex-col gap-5 font-mono text-xs">
        {/* Title & Description */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
              Scenario Designation
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-[#2B2B2B] border border-[#4A4A4A] rounded px-3 py-2 text-[#E0E0E0] focus:border-[#00ACC1] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
              Operational Hypothesis / Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-[#2B2B2B] border border-[#4A4A4A] rounded px-3 py-2 text-[#E0E0E0] focus:border-[#00ACC1] focus:outline-none"
            />
          </div>
        </div>

        {/* Intervention Mode Selector */}
        <div>
          <label className="block text-[#9E9E9E] uppercase mb-2 font-semibold">
            Intervention Methodology
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => setInterventionType("PercentageReduction")}
              className={`p-3 rounded border text-left transition-all ${
                interventionType === "PercentageReduction"
                  ? "bg-[#0A3840] border-[#00ACC1] text-[#00ACC1]"
                  : "bg-[#2B2B2B] border-[#4A4A4A] text-[#9E9E9E] hover:text-[#E0E0E0]"
              }`}
            >
              <div className="font-bold uppercase">1. Percentage Reduction</div>
              <div className="text-[10px] text-[#757575] mt-1">
                E.g. VFD drives, insulation, boiler tuning (5% - 40%)
              </div>
            </button>

            <button
              type="button"
              onClick={() => setInterventionType("AbsoluteReduction")}
              className={`p-3 rounded border text-left transition-all ${
                interventionType === "AbsoluteReduction"
                  ? "bg-[#0A3840] border-[#00ACC1] text-[#00ACC1]"
                  : "bg-[#2B2B2B] border-[#4A4A4A] text-[#9E9E9E] hover:text-[#E0E0E0]"
              }`}
            >
              <div className="font-bold uppercase">2. Absolute Reduction</div>
              <div className="text-[10px] text-[#757575] mt-1">
                Fixed curtailment or metered volume cut
              </div>
            </button>

            <button
              type="button"
              onClick={() => setInterventionType("FuelSubstitution")}
              className={`p-3 rounded border text-left transition-all ${
                interventionType === "FuelSubstitution"
                  ? "bg-[#0A3840] border-[#00ACC1] text-[#00ACC1]"
                  : "bg-[#2B2B2B] border-[#4A4A4A] text-[#9E9E9E] hover:text-[#E0E0E0]"
              }`}
            >
              <div className="font-bold uppercase">3. Fuel Substitution</div>
              <div className="text-[10px] text-[#757575] mt-1">
                Fuel switching: Oil/Gas → Electrification or Green H2
              </div>
            </button>
          </div>
        </div>

        {/* Dynamic Fields per Intervention */}
        <div className="p-4 rounded bg-[#2B2B2B] border border-[#383838]">
          {interventionType === "PercentageReduction" && (
            <div className="max-w-xs">
              <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
                Reduction Percentage (%)
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={reductionPercentage}
                onChange={(e) => setReductionPercentage(e.target.value)}
                className="w-full bg-[#333333] border border-[#4A4A4A] rounded px-3 py-2 text-[#FFFFFF] font-bold focus:border-[#00ACC1] focus:outline-none"
              />
            </div>
          )}

          {interventionType === "AbsoluteReduction" && (
            <div className="max-w-xs">
              <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
                Absolute Consumption Cut (Original Activity Units)
              </label>
              <input
                type="number"
                min="1"
                value={reductionAmount}
                onChange={(e) => setReductionAmount(e.target.value)}
                className="w-full bg-[#333333] border border-[#4A4A4A] rounded px-3 py-2 text-[#FFFFFF] font-bold focus:border-[#00ACC1] focus:outline-none"
              />
            </div>
          )}

          {interventionType === "FuelSubstitution" && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
                  Replacement Fuel Type
                </label>
                <select
                  value={newActivityType}
                  onChange={(e) => setNewActivityType(e.target.value)}
                  className="w-full bg-[#333333] border border-[#4A4A4A] rounded px-3 py-2 text-[#FFFFFF] focus:border-[#00ACC1] focus:outline-none"
                >
                  <option value="electricity_grid">Grid Electricity</option>
                  <option value="natural_gas">Natural Gas</option>
                  <option value="biomass">Biomass Pellets</option>
                </select>
              </div>

              <div>
                <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
                  Efficiency Multiplier
                </label>
                <input
                  type="text"
                  value={conversionMultiplier}
                  onChange={(e) => setConversionMultiplier(e.target.value)}
                  placeholder="e.g. 0.85 for COP efficiency"
                  className="w-full bg-[#333333] border border-[#4A4A4A] rounded px-3 py-2 text-[#FFFFFF] focus:border-[#00ACC1] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[#9E9E9E] uppercase mb-1 font-semibold">
                  Unit Price ($ / unit)
                </label>
                <input
                  type="text"
                  value={newUnitPrice}
                  onChange={(e) => setNewUnitPrice(e.target.value)}
                  placeholder="Optional cost rate"
                  className="w-full bg-[#333333] border border-[#4A4A4A] rounded px-3 py-2 text-[#FFFFFF] focus:border-[#00ACC1] focus:outline-none"
                />
              </div>
            </div>
          )}
        </div>

        {/* Target Activities Selection */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-[#9E9E9E] uppercase font-semibold">
              Select Target Facility Line Items ({selectedActivityIds.length} selected)
            </label>
            <button
              type="button"
              onClick={handleSelectTop}
              className="text-[11px] text-[#00ACC1] hover:underline"
            >
              Select Top Emitters
            </button>
          </div>

          <div className="max-h-48 overflow-y-auto border border-[#4A4A4A] rounded bg-[#2B2B2B] p-2 flex flex-col gap-1">
            {activities
              .filter((a) => a.activity_id)
              .map((act) => {
                const isSelected = selectedActivityIds.includes(act.activity_id!);
                return (
                  <div
                    key={act.activity_id}
                    onClick={() => handleToggleActivity(act.activity_id!)}
                    className={`p-2 rounded border cursor-pointer flex items-center justify-between transition-colors ${
                      isSelected
                        ? "bg-[#0A3840] border-[#00ACC1] text-[#FFFFFF]"
                        : "bg-[#333333] border-transparent text-[#9E9E9E] hover:text-[#E0E0E0]"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => {}} // Handled by parent div
                        className="rounded accent-[#00ACC1]"
                      />
                      <span className="truncate">
                        {act.description || act.activity_type}
                      </span>
                    </div>
                    <span className="font-bold text-[#E0E0E0] flex-shrink-0 ml-2">
                      {act.quantity} {act.unit}
                    </span>
                  </div>
                );
              })}
          </div>
        </div>

        {error && (
          <div className="p-3 rounded bg-[#3B1111] border border-[#D32F2F] text-[#D32F2F] flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Submit with SBO Confirmation */}
        <div className="flex justify-end pt-2">
          <SboButton
            onConfirm={handleSubmit}
            disabled={submitting || selectedActivityIds.length === 0}
            confirmLabel="Confirm Execute Simulation?"
          >
            {submitting ? "Evaluating Engine Math..." : "Run Scenario Simulation"}
          </SboButton>
        </div>
      </div>
    </IsaCard>
  );
}
