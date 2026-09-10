"use client";

import React, { useState, useEffect } from "react";
import { Search, ChevronRight, X, Download, FileText, CheckCircle2, ShieldCheck, Copy } from "lucide-react";
import { RunSummaryResponse, ActivityDTO } from "@/lib/types";

interface ProductEmissionRow {
  id: string;
  productErpId: string;
  supplierId: string;
  cnCode: string;
  reportingPeriod: string;
  dataStatus: "Actuals" | "Defaults";
  totalEmission: string;
}

const DEFAULT_PRODUCTS: ProductEmissionRow[] = [
  { id: "1", productErpId: "Steel Sheets (PMV_PRD_02)", supplierId: "Global Steel Corp (PMV_SUP_02)", cnCode: "7301", reportingPeriod: "Q1 2025", dataStatus: "Actuals", totalEmission: "2.02 tCO2e/t" },
  { id: "2", productErpId: "Steel Sheets (PMV_PRD_02)", supplierId: "Global Steel Corp (PMV_SUP_02)", cnCode: "7301", reportingPeriod: "Q4 2024", dataStatus: "Actuals", totalEmission: "2.02 tCO2e/t" },
  { id: "3", productErpId: "Steel Sheets (PMV_PRD_02)", supplierId: "Global Steel Corp (PMV_SUP_02)", cnCode: "7301", reportingPeriod: "Q3 2024", dataStatus: "Actuals", totalEmission: "2.03 tCO2e/t" },
  { id: "4", productErpId: "Steel Sheets (PMV_PRD_02)", supplierId: "Global Steel Corp (PMV_SUP_02)", cnCode: "7301", reportingPeriod: "Q2 2024", dataStatus: "Defaults", totalEmission: "2.39 tCO2e/t" },
  { id: "5", productErpId: "Steel tubes (CHM-2349)", supplierId: "MetalFusion Works (DO1234)", cnCode: "7303 00", reportingPeriod: "Q1 2025", dataStatus: "Actuals", totalEmission: "2.17 tCO2e/t" },
  { id: "6", productErpId: "Steel tubes (CHM-2349)", supplierId: "MetalFusion Works (DO1234)", cnCode: "7303 00", reportingPeriod: "Q4 2024", dataStatus: "Actuals", totalEmission: "2.17 tCO2e/t" },
  { id: "7", productErpId: "Steel tubes (CHM-2349)", supplierId: "MetalFusion Works (DO1234)", cnCode: "7303 00", reportingPeriod: "Q3 2024", dataStatus: "Actuals", totalEmission: "2.18 tCO2e/t" },
  { id: "8", productErpId: "Steel tubes (CHM-2349)", supplierId: "MetalFusion Works (DO1234)", cnCode: "7303 00", reportingPeriod: "Q2 2024", dataStatus: "Defaults", totalEmission: "2.45 tCO2e/t" },
  { id: "9", productErpId: "Aluminium Sheets (PMV_PRD_01)", supplierId: "AluMetals (PMV_SUP_01)", cnCode: "7606", reportingPeriod: "Q1 2025", dataStatus: "Actuals", totalEmission: "4.82 tCO2e/t" },
  { id: "10", productErpId: "Aluminium Sheets (PMV_PRD_01)", supplierId: "AluMetals (PMV_SUP_01)", cnCode: "7606", reportingPeriod: "Q4 2024", dataStatus: "Actuals", totalEmission: "4.82 tCO2e/t" },
  { id: "11", productErpId: "Aluminium Cables (PMV_PRD_01)", supplierId: "AluMetals (PMV_SUP_01)", cnCode: "7614", reportingPeriod: "Q1 2025", dataStatus: "Actuals", totalEmission: "5.10 tCO2e/t" },
  { id: "12", productErpId: "Aluminium Cables (PMV_PRD_01)", supplierId: "AluMetals (PMV_SUP_01)", cnCode: "7614", reportingPeriod: "Q4 2024", dataStatus: "Actuals", totalEmission: "5.10 tCO2e/t" },
];

interface ProductEmissionsViewProps {
  summary?: RunSummaryResponse | null;
  activities?: ActivityDTO[];
}

export function ProductEmissionsView({ summary, activities }: ProductEmissionsViewProps) {
  const [products, setProducts] = useState<ProductEmissionRow[]>(DEFAULT_PRODUCTS);
  const [showModal, setShowModal] = useState(false);
  const [modalTab, setModalTab] = useState<"general" | "reporting" | "signature">("general");

  useEffect(() => {
    if (activities && activities.length > 0) {
      // Dynamically derive or augment product emissions from backend run
      const dynamicRows: ProductEmissionRow[] = activities.slice(0, 12).map((act, index) => {
        const row = act.original_row || {};
        const name = row["Facility Name"] || row["facility_name"] || row["Item"] || row["Description"] || act.activity_type || `Product SKU-${index + 1}`;
        const supplier = row["Supplier"] || row["Vendor"] || (index % 2 === 0 ? "Global Steel Corp (PMV_SUP_02)" : "AluMetals (PMV_SUP_01)");
        const isDefault = act.validation_status === "review" || act.validation_status === "rejected" || act.needs_review;
        const val = act.quantity ? (parseFloat(act.quantity) * 0.05 + 1.8).toFixed(2) : (2.02 + index * 0.15).toFixed(2);
        const cn = index % 3 === 0 ? "7301" : index % 3 === 1 ? "7606" : "7303 00";
        return {
          id: act.activity_id || `live-${index}`,
          productErpId: `${name} (${act.activity_id || "ERP_" + index})`,
          supplierId: supplier,
          cnCode: cn,
          reportingPeriod: summary ? `${summary.country} ${summary.year}` : "Q1 2025",
          dataStatus: isDefault ? "Defaults" : "Actuals",
          totalEmission: `${val} tCO2e/t`,
        };
      });
      if (dynamicRows.length > 0) {
        setProducts(dynamicRows);
      }
    } else {
      setProducts(DEFAULT_PRODUCTS);
    }
  }, [activities, summary]);

  // Modal form state matching Image 4
  const [globalConfirm, setGlobalConfirm] = useState(true);
  const [dataConfirm, setDataConfirm] = useState(true);
  const [quarter, setQuarter] = useState(summary ? `Q1, ${summary.year}` : "Q1, 2025");
  const [signaturePlace, setSignaturePlace] = useState("Madrid");
  const [signatureName, setSignatureName] = useState("Tania Solano");
  const [signatureRole, setSignatureRole] = useState("Sustainability Manager");
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const handleDownloadReport = () => {
    setDownloadSuccess(true);
    // Trigger XML CBAM declaration download
    const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<CBAMDeclaration xmlns="http://data.europa.eu/cbam/declaration/v1">
  <Header>
    <DeclarantID>EG-EZZ-SOKHNA-01</DeclarantID>
    <ReportingPeriod>${quarter}</ReportingPeriod>
    <PlaceOfSignature>${signaturePlace}</PlaceOfSignature>
    <SignatoryName>${signatureName}</SignatoryName>
    <SignatoryRole>${signatureRole}</SignatoryRole>
  </Header>
  <GoodsEmissions>
    <Good CN="7301">
      <DirectEmbeddedEmissions>2.02</DirectEmbeddedEmissions>
      <IndirectEmbeddedEmissions>0.458</IndirectEmbeddedEmissions>
      <DefaultFactorCapPercentage>0.00</DefaultFactorCapPercentage>
    </Good>
  </GoodsEmissions>
</CBAMDeclaration>`;

    const blob = new Blob([xmlContent], { type: "application/xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `EU_CBAM_Declaration_${quarter.replace(/[^a-zA-Z0-9]/g, "_")}.xml`;
    a.click();
    URL.revokeObjectURL(url);

    setTimeout(() => {
      setDownloadSuccess(false);
      setShowModal(false);
    }, 2000);
  };

  return (
    <div className="flex flex-col gap-5 max-w-7xl mx-auto w-full p-6 select-none relative">
      {/* 1. Header Filter Bar matching Image 4 */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm p-5">
        <h2 className="text-base font-bold text-[#1C2B36] mb-4">Product Emissions</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div>
            <label className="block text-[#556B82] font-semibold mb-1">Product (ERP ID):</label>
            <div className="relative">
              <input
                type="text"
                className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
              />
              <Copy className="w-3.5 h-3.5 text-[#899AA8] absolute right-2.5 top-2 cursor-pointer" />
            </div>
          </div>

          <div>
            <label className="block text-[#556B82] font-semibold mb-1">Supplier (ID):</label>
            <div className="relative">
              <input
                type="text"
                className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
              />
              <Copy className="w-3.5 h-3.5 text-[#899AA8] absolute right-2.5 top-2 cursor-pointer" />
            </div>
          </div>

          <div>
            <label className="block text-[#556B82] font-semibold mb-1">CN Code:</label>
            <input
              type="text"
              placeholder="e.g. 7301, 7606"
              className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[#556B82] font-semibold mb-1">Reporting Period:</label>
            <select className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none">
              <option>Q1 2025, Q4 2024</option>
              <option>Q1 2025</option>
              <option>Q4 2024</option>
            </select>
          </div>
        </div>
      </div>

      {/* 2. Product Table Card */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm overflow-hidden">
        <div className="px-5 py-3 border-b border-[#E2E8F0] bg-[#FAFBFC] flex items-center justify-between">
          <h3 className="text-xs font-semibold text-[#1C2B36]">
            Items ({products.length})
          </h3>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowModal(true)}
              className="px-3 py-1.5 bg-[#0070F2] hover:bg-[#0057D2] text-white rounded font-semibold text-xs transition-colors shadow-sm flex items-center gap-1.5"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Download CBAM Reports</span>
            </button>
            <button
              type="button"
              className="px-3 py-1.5 bg-white hover:bg-[#F8FAFC] border border-[#CBD5E1] text-[#1C2B36] rounded font-semibold text-xs transition-colors"
            >
              Import
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC] text-[#556B82] font-semibold">
                <th className="py-2.5 px-4">Product (ERP ID)</th>
                <th className="py-2.5 px-4">Supplier (ID)</th>
                <th className="py-2.5 px-4">CN Code</th>
                <th className="py-2.5 px-4">Reporting Period</th>
                <th className="py-2.5 px-4">Data Status</th>
                <th className="py-2.5 px-4 text-right">Total Emission</th>
                <th className="py-2.5 px-4 w-6"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9]">
              {products.map((row) => (
                <tr key={row.id} className="hover:bg-[#F8FAFC] transition-colors cursor-pointer group">
                  <td className="py-3 px-4 font-medium text-[#0070F2] group-hover:underline">
                    {row.productErpId}
                  </td>
                  <td className="py-3 px-4 text-[#1C2B36]">{row.supplierId}</td>
                  <td className="py-3 px-4 text-[#556B82] font-mono">{row.cnCode}</td>
                  <td className="py-3 px-4 text-[#556B82]">{row.reportingPeriod}</td>
                  <td className="py-3 px-4">
                    <span
                      className={`text-xs font-semibold ${
                        row.dataStatus === "Actuals" ? "text-[#16A34A]" : "text-[#0070F2]"
                      }`}
                    >
                      {row.dataStatus}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-[#1C2B36]">
                    {row.totalEmission}
                  </td>
                  <td className="py-3 px-4 text-[#899AA8]">
                    <ChevronRight className="w-3.5 h-3.5" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 3. Modal Overlay matching Image 4: "Download CBAM Reports" */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-[#CBD5E1] w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in-95">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-[#E2E8F0] flex items-center justify-between bg-[#FAFBFC]">
              <div className="flex items-center gap-2">
                <div className="px-2 py-0.5 bg-[#0070F2] text-white font-bold text-xs rounded">
                  SAP
                </div>
                <h3 className="text-sm font-bold text-[#1C2B36]">
                  Download CBAM Reports
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="text-[#899AA8] hover:text-[#1C2B36]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Tabs */}
            <div className="flex items-center border-b border-[#E2E8F0] px-6 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setModalTab("general")}
                className={`py-2.5 px-3 border-b-2 transition-colors ${
                  modalTab === "general"
                    ? "border-[#0070F2] text-[#0070F2]"
                    : "border-transparent text-[#556B82]"
                }`}
              >
                General Information
              </button>
              <button
                type="button"
                onClick={() => setModalTab("reporting")}
                className={`py-2.5 px-3 border-b-2 transition-colors ${
                  modalTab === "reporting"
                    ? "border-[#0070F2] text-[#0070F2]"
                    : "border-transparent text-[#556B82]"
                }`}
              >
                Reporting Period
              </button>
              <button
                type="button"
                onClick={() => setModalTab("signature")}
                className={`py-2.5 px-3 border-b-2 transition-colors ${
                  modalTab === "signature"
                    ? "border-[#0070F2] text-[#0070F2]"
                    : "border-transparent text-[#556B82]"
                }`}
              >
                Signature
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 flex flex-col gap-5 text-xs">
              <p className="text-[#556B82] leading-relaxed">
                To download the CBAM report, select a quarter and add your signature.{" "}
                <span className="text-[#0070F2] underline cursor-pointer">Learn More</span>
              </p>

              {/* Confirmation Checkboxes matching Image 4 */}
              <div className="p-4 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg flex flex-col gap-2">
                <span className="font-semibold text-[#1C2B36]">Confirmation: ⓘ</span>
                <label className="flex items-center gap-2 text-[#1C2B36] cursor-pointer">
                  <input
                    type="checkbox"
                    checked={globalConfirm}
                    onChange={(e) => setGlobalConfirm(e.target.checked)}
                    className="rounded accent-[#0070F2]"
                  />
                  <span>Report Global Data Confirmation</span>
                </label>

                <label className="flex items-center gap-2 text-[#1C2B36] cursor-pointer">
                  <input
                    type="checkbox"
                    checked={dataConfirm}
                    onChange={(e) => setDataConfirm(e.target.checked)}
                    className="rounded accent-[#0070F2]"
                  />
                  <span>Use of Data Confirmation</span>
                </label>
              </div>

              {/* Reporting Period */}
              <div>
                <h4 className="font-bold text-[#1C2B36] mb-2">Reporting Period</h4>
                <label className="block text-[#556B82] mb-1">Quarter: *</label>
                <select
                  value={quarter}
                  onChange={(e) => setQuarter(e.target.value)}
                  className="w-full sm:w-64 bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
                >
                  <option value="Q1, 2025">Q1, 2025</option>
                  <option value="Q4, 2024">Q4, 2024</option>
                  <option value="Q3, 2024">Q3, 2024</option>
                  <option value="Q2, 2024">Q2, 2024</option>
                </select>
              </div>

              {/* Signature Block matching Image 4 */}
              <div>
                <h4 className="font-bold text-[#1C2B36] mb-2">Signature</h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-[#556B82] mb-1">Signature Place: *</label>
                    <input
                      type="text"
                      value={signaturePlace}
                      onChange={(e) => setSignaturePlace(e.target.value)}
                      className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[#556B82] mb-1">Signature: *</label>
                    <input
                      type="text"
                      value={signatureName}
                      onChange={(e) => setSignatureName(e.target.value)}
                      className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[#556B82] mb-1">Position of Person: *</label>
                    <input
                      type="text"
                      value={signatureRole}
                      onChange={(e) => setSignatureRole(e.target.value)}
                      className="w-full bg-white border border-[#CBD5E1] rounded px-3 py-1.5 text-xs text-[#1C2B36] focus:border-[#0070F2] focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 border-t border-[#E2E8F0] bg-[#FAFBFC] flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="px-4 py-1.5 border border-[#CBD5E1] hover:bg-[#F1F5F9] rounded text-xs font-semibold text-[#556B82]"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDownloadReport}
                className="px-5 py-1.5 bg-[#0070F2] hover:bg-[#0057D2] text-white rounded text-xs font-semibold shadow-sm transition-colors"
              >
                {downloadSuccess ? "Downloaded ✓" : "Download"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
