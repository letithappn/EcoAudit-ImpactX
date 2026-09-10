/**
 * Stitch Design System Authoritative Baseline Data
 * Aligned with Chicago Energy Benchmarking (28,329 Municipal & Commercial Properties)
 */

export interface FacilityHeatmapRow {
  facilityName: string;
  location: string;
  scope1: string;
  scope2: string;
  scope3: string;
  intensity: string;
  cbamExposed: boolean;
  status: "Verified" | "AI Classified" | "Audit Ready" | "Action Required";
}

export interface DrilldownCategory {
  title: string;
  scope: string;
  tonnage: string;
  percentage: string;
  color: string;
  items: {
    name: string;
    method: string;
    tonnage: string;
  }[];
}

export const STITCH_BASELINE_DATA = {
  facilityLabel: "City of Chicago Energy Benchmarking (28,329 Buildings) • Municipal & Commercial Telemetry",
  totalEmissionsTons: 29465923,
  scope1Tons: 14195747,
  scope2Tons: 15270176,
  scope3Tons: 0,
  revenueBillions: 3.42,
  intensityTonsPerMillionRev: 417.8,
  etsExposureMillions: 34.2,
  auditIntegrityPercentage: 81.0,
  renewablesPercentage: 51.8,
  naturalGasPercentage: 48.2,
  fuelOilPercentage: 0.0,

  drilldownCategories: [
    {
      title: "Scope 1: Stationary Combustion — Pipeline Natural Gas Heating",
      scope: "Scope 1",
      tonnage: "14,195,747 tCO₂e",
      percentage: "48%",
      color: "#1d4ed8",
      items: [
        { name: "Commercial Office & Hotel Space Heating (Peoples Gas)", method: "Direct Metering (kBtu)", tonnage: "7,807,661 t" },
        { name: "Multifamily Residential Central Boilers & Domestic Water", method: "Utility Metering", tonnage: "4,399,681 t" },
        { name: "Hospitals, Universities & Municipal Campuses", method: "Direct Metering (kBtu)", tonnage: "1,988,405 t" },
      ],
    },
    {
      title: "Scope 2: Purchased Electricity — ComEd Regional Power Grid",
      scope: "Scope 2",
      tonnage: "15,270,176 tCO₂e",
      percentage: "52%",
      color: "#85f8c4",
      items: [
        { name: "Commercial High-Rise HVAC, Lighting & Plug Loads", method: "ComEd Smart Metering", tonnage: "8,400,597 t" },
        { name: "Multifamily Common Areas, Elevators & Heat Pumps", method: "Utility Metering", tonnage: "4,733,755 t" },
        { name: "Digital Lakeside Data Center & Cold Storage Facilities", method: "Primary Interval Metering", tonnage: "2,135,824 t" },
      ],
    },
  ] as DrilldownCategory[],

  facilityHeatmap: [
    {
      facilityName: "Metropolitan Pier & Exposition (McCormick Place)",
      location: "301 Cermak Rd, Chicago, IL",
      scope1: "24,960 t",
      scope2: "92,078 t",
      scope3: "0 t",
      intensity: "12.7 kgCO₂e/sq ft",
      cbamExposed: false,
      status: "Verified",
    },
    {
      facilityName: "Digital Lakeside Carrier Hotel & Data Center",
      location: "350 E Cermak, Chicago, IL",
      scope1: "0 t",
      scope2: "77,456 t",
      scope3: "0 t",
      intensity: "60.5 kgCO₂e/sq ft",
      cbamExposed: false,
      status: "Verified",
    },
    {
      facilityName: "Mount Sinai Hospital & Medical Center Campus",
      location: "1525 S California Ave, Chicago, IL",
      scope1: "65,975 t",
      scope2: "4,088 t",
      scope3: "0 t",
      intensity: "69.4 kgCO₂e/sq ft",
      cbamExposed: false,
      status: "Verified",
    },
    {
      facilityName: "Cambria Hotel Chicago Loop",
      location: "32 W Randolph St, Chicago, IL",
      scope1: "86,747 t",
      scope2: "1,213 t",
      scope3: "0 t",
      intensity: "356.7 kgCO₂e/sq ft",
      cbamExposed: false,
      status: "AI Classified",
    },
    {
      facilityName: "318 N Carpenter St (Fulton Market)",
      location: "318 N Carpenter St, Chicago, IL",
      scope1: "91 t",
      scope2: "116 t",
      scope3: "0 t",
      intensity: "2.0 kgCO₂e/sq ft",
      cbamExposed: false,
      status: "Audit Ready",
    },
    {
      facilityName: "29 E Madison St (Historic Loop Tower)",
      location: "29 E Madison St, Chicago, IL",
      scope1: "900 t",
      scope2: "769 t",
      scope3: "0 t",
      intensity: "7.0 kgCO₂e/sq ft",
      cbamExposed: false,
      status: "Audit Ready",
    },
  ] as FacilityHeatmapRow[],
};
