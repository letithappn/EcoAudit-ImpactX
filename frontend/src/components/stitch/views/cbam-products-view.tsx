"use client";

import React, { useState } from "react";
import { RunSummaryResponse, ActivityDTO } from "@/lib/types";

interface CbamProductsViewProps {
  summary: RunSummaryResponse | null;
  activities: ActivityDTO[];
  onOpenUpload?: () => void;
}

export function CbamProductsView({
  summary,
  activities,
  onOpenUpload,
}: CbamProductsViewProps) {
  const [downloadingXml, setDownloadingXml] = useState(false);

  const handleDownloadXml = () => {
    setDownloadingXml(true);
    setTimeout(() => {
      const xmlData = `<?xml version="1.0" encoding="UTF-8"?>
<CBAMDeclaration xmlns="urn:eu:cbam:v1" reportingPeriod="2024-Q3" eori="NL849201948">
  <Header>
    <DeclarantName>Egyptian Advanced Manufacturing S.A.E.</DeclarantName>
    <CountryOfOrigin>EG</CountryOfOrigin>
    <TotalDeclaredTonnage>142800</TotalDeclaredTonnage>
  </Header>
  <GoodsItems>
    <GoodsItem cnCode="7208 37 00" description="Hot-rolled steel coils" embeddedEmissions="1.45" />
    <GoodsItem cnCode="7601 10 00" description="Unwrought primary aluminum" embeddedEmissions="3.80" />
    <GoodsItem cnCode="7214 20 00" description="Deformed concrete rebar" embeddedEmissions="1.18" />
  </GoodsItems>
</CBAMDeclaration>`;
      const blob = new Blob([xmlData], { type: "application/xml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "CBAM_Declaration_2024_Q3.xml";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setDownloadingXml(false);
    }, 600);
  };

  return (
    <div className="flex flex-col w-full">
      <div className="px-space-xl pt-space-xl pb-space-lg flex flex-col gap-space-lg">
        {/* Header Block */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md">
          <div className="flex flex-col gap-space-2xs">
            <div className="flex items-center gap-space-xs text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider">
              <span>Regulation (EU) 2023/956</span>
              <span className="text-outline-variant">•</span>
              <span>Transitional Customs Clearance Engine</span>
              <span className="text-outline-variant">•</span>
              <span className="font-mono-data text-secondary">EORI: NL849201948</span>
            </div>
            <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight font-bold">
              Product Carbon Footprints &amp; Export Declarations (EU CBAM)
            </h1>
            <p className="font-body-md text-body-md text-on-surface-variant max-w-4xl">
              Embedded emissions accounting per customs CN code, verified actuals vs. default values,
              and signed quarterly declarations.
            </p>
          </div>

          <div className="flex items-center gap-space-sm self-start lg:self-center">
            <button
              type="button"
              onClick={handleDownloadXml}
              disabled={downloadingXml}
              className="flex items-center gap-space-xs bg-secondary hover:bg-secondary/90 text-on-secondary px-space-lg py-space-sm rounded-lg font-label-md text-label-md font-semibold shadow-md transition-all active:scale-[0.98]"
            >
              <span className="material-symbols-outlined text-[18px]">code</span>
              <span>{downloadingXml ? "Generating XML..." : "Build CBAM XML"}</span>
            </button>
          </div>
        </div>

        {/* Regulatory Status Banner */}
        <div className="bg-surface-container-lowest rounded-xl p-space-lg shadow-sm border border-outline-variant/20 flex flex-col xl:flex-row items-start xl:items-center justify-between gap-space-lg relative overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-error" />
          <div className="flex items-start gap-space-md max-w-3xl">
            <div className="w-10 h-10 rounded-lg bg-error-container/40 flex items-center justify-center shrink-0 mt-0.5">
              <span className="material-symbols-outlined text-error text-[24px]">hourglass_top</span>
            </div>
            <div className="flex flex-col gap-space-2xs">
              <div className="flex items-center gap-space-sm flex-wrap">
                <span className="font-headline-md text-headline-md font-bold text-on-surface">
                  Q3 2024 EU CBAM Transitional Period Filing Due in 14 Days
                </span>
                <span className="bg-error-container/50 text-on-error-container font-mono-data text-[11px] px-space-xs py-space-2xs rounded uppercase font-semibold">
                  Deadline: Nov 7, 2024
                </span>
              </div>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                12 of 14 covered customs product lines verified via primary supplier installations. 2 lines require upstream precursor validation before XML compilation.
              </p>
              <div className="w-full max-w-md flex items-center gap-space-sm mt-space-xs">
                <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                  <div className="bg-on-tertiary-container h-full rounded-full" style={{ width: "85.7%" }} />
                </div>
                <span className="font-mono-data text-label-sm text-on-surface-variant whitespace-nowrap">
                  12/14 Verified (85.7%)
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-space-sm w-full xl:w-auto justify-end">
            <button
              type="button"
              onClick={onOpenUpload}
              className="flex items-center gap-space-xs bg-surface-container-low hover:bg-surface-container text-on-surface px-space-md py-space-sm rounded-lg font-label-md text-label-md"
            >
              <span className="material-symbols-outlined text-[18px]">upload</span>
              <span>Upload Supplier Actuals</span>
            </button>
          </div>
        </div>

        {/* Summary Metrics Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-space-md">
          {/* Metric 1 */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Declared Export Tonnage
              </span>
              <span className="material-symbols-outlined text-secondary text-[20px]">scale</span>
            </div>
            <div className="mt-space-md flex flex-col">
              <div className="flex items-baseline gap-space-2xs">
                <span className="font-metric-xl text-metric-xl font-bold text-on-surface">142,800</span>
                <span className="font-mono-data text-label-sm text-on-surface-variant">Tonnes</span>
              </div>
              <div className="flex items-center gap-space-xs mt-space-2xs text-on-tertiary-container font-label-sm text-label-sm">
                <span className="material-symbols-outlined text-[16px]">trending_up</span>
                <span>+14.2% vs Q2 Actuals</span>
              </div>
            </div>
            <div className="mt-space-md pt-space-xs flex justify-between items-center text-on-surface-variant font-mono-data text-[11px] bg-surface-container-low px-space-sm py-space-2xs rounded">
              <span>HS Chapters 72, 76</span>
              <span>5 CN Codes Active</span>
            </div>
          </div>

          {/* Metric 2 */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Avg Embedded Intensity
              </span>
              <span className="material-symbols-outlined text-on-tertiary-container text-[20px]">co2</span>
            </div>
            <div className="mt-space-md flex flex-col">
              <div className="flex items-baseline gap-space-2xs">
                <span className="font-metric-xl text-metric-xl font-bold text-on-surface">1.62</span>
                <span className="font-mono-data text-label-sm text-on-surface-variant">tCO₂e / Tonne</span>
              </div>
              <div className="flex items-center gap-space-xs mt-space-2xs text-on-tertiary-container font-label-sm text-label-sm">
                <span className="material-symbols-outlined text-[16px]">verified</span>
                <span>31% below EU Benchmark (2.35)</span>
              </div>
            </div>
            <div className="mt-space-md pt-space-xs flex flex-col gap-1">
              <div className="w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden flex">
                <div className="bg-secondary h-full" style={{ width: "68.9%" }} />
                <div className="bg-error/30 h-full" style={{ width: "31.1%" }} />
              </div>
              <div className="flex justify-between items-center font-mono-data text-[10px] text-on-surface-variant">
                <span>Primary: 1.62</span>
                <span>EU Benchmark: 2.35</span>
              </div>
            </div>
          </div>

          {/* Metric 3 */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Avoided CBAM Certificates
              </span>
              <span className="material-symbols-outlined text-secondary text-[20px]">savings</span>
            </div>
            <div className="mt-space-md flex flex-col">
              <div className="flex items-baseline gap-space-2xs">
                <span className="font-metric-xl text-metric-xl font-bold text-secondary">€7.84M</span>
                <span className="font-mono-data text-label-sm text-on-surface-variant">EUR</span>
              </div>
              <div className="flex items-center gap-space-xs mt-space-2xs text-on-tertiary-container font-label-sm text-label-sm">
                <span className="material-symbols-outlined text-[16px]">arrow_downward</span>
                <span>Est. Tariff Liability Saved</span>
              </div>
            </div>
            <div className="mt-space-md pt-space-xs flex justify-between items-center text-on-surface-variant font-mono-data text-[11px] bg-surface-container-low px-space-sm py-space-2xs rounded">
              <span>Shadow Price: €85/t</span>
              <span>Primary Advantage</span>
            </div>
          </div>

          {/* Metric 4 */}
          <div className="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm border border-outline-variant/20 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Customs Compliance Score
              </span>
              <span className="material-symbols-outlined text-on-tertiary-container text-[20px]">fact_check</span>
            </div>
            <div className="mt-space-md flex flex-col">
              <div className="flex items-baseline gap-space-2xs">
                <span className="font-metric-xl text-metric-xl font-bold text-on-tertiary-container">98.4%</span>
                <span className="font-mono-data text-label-sm text-on-surface-variant">Audit Index</span>
              </div>
              <div className="flex items-center gap-space-xs mt-space-2xs text-on-tertiary-container font-label-sm text-label-sm">
                <span className="material-symbols-outlined text-[16px]">check_circle</span>
                <span>Zero Penalty Status</span>
              </div>
            </div>
            <div className="mt-space-md pt-space-xs flex justify-between items-center text-on-surface-variant font-mono-data text-[11px] bg-surface-container-low px-space-sm py-space-2xs rounded">
              <span>Verified DNV-GL</span>
              <span>Registry Ready</span>
            </div>
          </div>
        </div>

        {/* Product Footprints Detail Table */}
        <div className="bg-surface-container-lowest rounded-xl p-space-xl shadow-sm border border-outline-variant/20 flex flex-col gap-space-md">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-headline-md text-headline-md text-on-surface font-bold">
                Covered Goods Footprint Register (CN Code Breakdown)
              </h2>
              <span className="font-body-sm text-body-sm text-on-surface-variant">
                Direct and indirect specific embedded emissions per customs line item.
              </span>
            </div>
            <span className="font-mono-data text-[11px] bg-surface-container-low px-space-sm py-1 rounded text-on-surface-variant">
              Regulation (EU) 2023/956 Annex IV
            </span>
          </div>

          <div className="overflow-x-auto rounded-lg border border-outline-variant/30">
            <table className="w-full text-left font-body-md text-body-md border-collapse">
              <thead>
                <tr className="bg-surface-container-low/60 text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider border-b border-outline-variant/30">
                  <th className="py-space-sm px-space-md">Customs CN Code</th>
                  <th className="py-space-sm px-space-md">Product Line</th>
                  <th className="py-space-sm px-space-md">Direct Intensity (S1)</th>
                  <th className="py-space-sm px-space-md">Indirect Intensity (S2)</th>
                  <th className="py-space-sm px-space-md">Total Embedded (tCO₂e/t)</th>
                  <th className="py-space-sm px-space-md">EU Default Benchmark</th>
                  <th className="py-space-sm px-space-md">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-mono-data font-bold text-secondary">
                    7208 37 00
                  </td>
                  <td className="py-space-sm px-space-md font-medium text-on-surface">
                    Flat-Rolled Steel Coils (Hot-Rolled)
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data">1.12 t/t</td>
                  <td className="py-space-sm px-space-md font-mono-data">0.33 t/t</td>
                  <td className="py-space-sm px-space-md font-mono-data font-bold text-on-surface">
                    1.45 tCO₂e/t
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-error">
                    2.15 tCO₂e/t
                  </td>
                  <td className="py-space-sm px-space-md">
                    <span className="inline-flex items-center gap-[3px] px-space-xs py-[2px] rounded text-[11px] font-semibold bg-tertiary-container/10 text-on-tertiary-container">
                      <span className="material-symbols-outlined text-[14px]">verified</span>
                      Primary Verified
                    </span>
                  </td>
                </tr>

                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-mono-data font-bold text-secondary">
                    7601 10 00
                  </td>
                  <td className="py-space-sm px-space-md font-medium text-on-surface">
                    Unwrought Non-Alloyed Primary Aluminum
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data">2.10 t/t</td>
                  <td className="py-space-sm px-space-md font-mono-data">1.70 t/t</td>
                  <td className="py-space-sm px-space-md font-mono-data font-bold text-on-surface">
                    3.80 tCO₂e/t
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-error">
                    6.80 tCO₂e/t
                  </td>
                  <td className="py-space-sm px-space-md">
                    <span className="inline-flex items-center gap-[3px] px-space-xs py-[2px] rounded text-[11px] font-semibold bg-tertiary-container/10 text-on-tertiary-container">
                      <span className="material-symbols-outlined text-[14px]">verified</span>
                      Primary Verified
                    </span>
                  </td>
                </tr>

                <tr className="hover:bg-surface-container-low/30 transition-colors">
                  <td className="py-space-sm px-space-md font-mono-data font-bold text-secondary">
                    7214 20 00
                  </td>
                  <td className="py-space-sm px-space-md font-medium text-on-surface">
                    Deformed Concrete Reinforcing Steel Bars
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data">0.88 t/t</td>
                  <td className="py-space-sm px-space-md font-mono-data">0.30 t/t</td>
                  <td className="py-space-sm px-space-md font-mono-data font-bold text-on-surface">
                    1.18 tCO₂e/t
                  </td>
                  <td className="py-space-sm px-space-md font-mono-data text-error">
                    1.90 tCO₂e/t
                  </td>
                  <td className="py-space-sm px-space-md">
                    <span className="inline-flex items-center gap-[3px] px-space-xs py-[2px] rounded text-[11px] font-semibold bg-tertiary-container/10 text-on-tertiary-container">
                      <span className="material-symbols-outlined text-[14px]">verified</span>
                      Primary Verified
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
