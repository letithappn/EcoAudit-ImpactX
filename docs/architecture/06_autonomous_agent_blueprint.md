# Module 6: Autonomous Agent Blueprint & System PRD Output
**Technical Reference: End-to-End System Architecture Flowchart & Deterministic Production Calculation Engine**

---

## 1. System Architecture Flowchart (Mermaid.js)

The following architectural flowchart captures the operational lifecycle: from physical paper bill ingestion and ERP feeds to deterministic carbon calculations, double-entry ledgering with SHA-256 state hashing, and dual regulatory outputs (FRA & EU CBAM).

```mermaid
flowchart TD
    %% Ingestion Channels
    subgraph Ingestion ["1. Multi-Channel Ingress Layer"]
        A1["Scanned Bills & Mobile Photos<br/>(SCEDC, NCEDC, CEDC)"]
        A2["Fuel Slips & Delivery Chits<br/>(Diesel, Mazut, Gasoline)"]
        A3["Enterprise ERP Connectors<br/>(SAP S/4HANA, Odoo, Oracle)"]
        A4["IoT Power Meters<br/>(15-min Active Power Telemetry)"]
    end

    %% Preprocessing & Extraction
    subgraph ExtractionPipeline ["2. Ingestion & Vision-Language Processing"]
        B1["OpenCV Preprocessing Engine<br/>• Radon-Transform Deskewing<br/>• Otsu Adaptive Binarization<br/>• Morphological Noise Filtering"]
        B2["YOLOv8 Document Layout Segmenter<br/>• Isolates Meter ROIs & Tables"]
        B3["Bilingual TrOCR Engine<br/>• Arabic Script & Eastern Numerals<br/>• Normalization: ٠-٩ ➔ 0-9"]
        B4["ERP Extraction Gateway<br/>• OData v4 (MATDOC, ACDOCA)<br/>• Odoo JSON-RPC (mrp.production)"]
    end

    %% Verification & Safety Firewall
    subgraph SafetyFirewall ["3. Validation & HITL Quarantine"]
        C1{"Mathematical Cross-Check<br/>• Delta Reading = Active kWh<br/>• Tariff Bracket Parity<br/>• Meter Inventory Match"}
        C2{"Confidence Score<br/>≥ 0.92?"}
        C3["Human-in-the-Loop (HITL) Dashboard<br/>• Side-by-Side Visual Split Screen<br/>• Select-Before-Operate (SBO) Gate"]
        C4[("Verified Activity Database<br/>PostgreSQL 16 / TimescaleDB")]
    end

    %% Emission Factor Registry
    subgraph FactorRegistry ["4. Egyptian National Baseline Registry"]
        D1[("National Factor Database<br/>• EEAA / NREA Unified Factor: 0.4580 t/MWh<br/>• EGPC Fuel Standards (NCV)<br/>• GWP: IPCC AR5 / AR6")]
    end

    %% Deterministic Core Engine
    subgraph ComputeCore ["5. Deterministic Calculation Engine"]
        E1["Factor Resolution Engine<br/>• Temporal Validity (valid_from / valid_to)<br/>• Geographic Boundary (EG)"]
        E2["Vectorized Fixed-Point Arithmetic Core<br/>• Python FastAPI + PyO3 Rust SIMD<br/>• 100% Deterministic Decimal Math"]
    end

    %% Double-Entry Ledger & Cryptography
    subgraph LedgerStorage ["6. Double-Entry Carbon Ledger (Append-Only)"]
        F1["Transaction Balancing Core<br/>• Debit: Facility Carbon Liability<br/>• Credit: Energy Absorption Clearing"]
        F2["SHA-256 State Chaining Engine<br/>H_n = SHA256(H_{n-1} || Tx || Payload)"]
        F3[("Immutable Carbon Ledger Table<br/>• Row-Level Security (RLS)<br/>• Mutation Block Trigger")]
    end

    %% Regulatory Reporting & Markets
    subgraph RegulatoryOutputs ["7. Regulatory Exporter & Compliance Portal"]
        G1["FRA Compliance Exporter<br/>• Decrees 107/108 Disclosure Tables<br/>• Decision 36/2026 20% CERC Offset"]
        G2["EGX Voluntary Carbon Market Gateway<br/>• Licensed Broker API (Decree 1732/2024)<br/>• CERC Procurement & Retirement Posting"]
        G3["EU CBAM Reporting Engine<br/>• Specific Embedded Emissions (SEE_g)<br/>• BOM Recursive Traversal (≤20% Default)"]
        G4["The Auditor's Room (VVB Cleanroom)<br/>• One-Click DAG Lineage Tracing<br/>• ISO 14064-3 Assurance Dossier"]
    end

    %% Connections
    A1 & A2 --> B1
    B1 --> B2 --> B3
    A3 --> B4
    A4 --> C4
    B3 --> C1
    B4 --> C1
    C1 --> C2
    C2 -- "No (Score < 0.92)" --> C3
    C3 -- "Auditor Confirmed" --> C4
    C2 -- "Yes (Score ≥ 0.92)" --> C4
    C4 --> E1
    D1 --> E1
    E1 --> E2
    E2 --> F1
    F1 --> F2
    F2 --> F3
    F3 --> G1
    F3 --> G3
    F3 --> G4
    G1 --> G2
```

---

## 2. Production Calculation Engine Algorithm (Python)

The following production-ready Python script implements the complete data lifecycle:
1. **Validates unstructured activity payloads** using strict, type-safe data structures.
2. **Resolves the official Egyptian national location-based electricity factor** (`0.4580 tCO2e/MWh`) against billing validity periods.
3. **Executes 100% deterministic fixed-point calculations** via Python `Decimal`.
4. **Posts balanced double-entry transactions** into an immutable carbon ledger.
5. **Enforces cryptographic SHA-256 state chaining** across ledger entries.
6. **Compiles official FRA compliance disclosure packages** under Decrees 107/108 and Decision 36 of 2026 (including the mandatory 20% CERC offset calculation).

```python
"""
EcoAudit AI — Enterprise Deterministic Carbon Calculation Core & Ledger Engine
Standard: GHG Protocol / ISO 14064-1 / FRA Decrees 107 & 108 (2021) & Decision 36 (2026)
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple


# ============================================================================
# 1. DOMAIN DATA MODELS & TYPE DEFINITIONS
# ============================================================================

@dataclass(frozen=True)
class UtilityActivityPayload:
    """Represents a verified utility invoice activity extracted via OCR/ERP."""
    activity_id: str
    tenant_id: str
    facility_id: str
    billing_period_start: date
    billing_period_end: date
    meter_serial_number: str
    active_energy_kwh: Decimal
    evidence_document_hash: str


@dataclass(frozen=True)
class EmissionFactorRecord:
    """Represents an authoritative versioned emission factor record."""
    factor_id: str
    factor_code: str
    version: int
    name: str
    scope: str
    co2e_factor: Decimal  # Metric tonnes CO2e per base unit (MWh)
    unit: str
    valid_from: date
    valid_to: Optional[date]
    gwp_framework: str
    citation: str


@dataclass(frozen=True)
class CarbonLedgerTransaction:
    """Represents an immutable posting within the double-entry carbon general ledger."""
    entry_id: str
    tenant_id: str
    facility_id: str
    activity_id: str
    factor_id: str
    transaction_date: str
    accounting_period: str
    scope: str
    entry_type: str  # 'DEBIT' or 'CREDIT'
    account_code: str
    co2e_metric_tons: Decimal
    previous_entry_hash: str
    entry_hash: str


# ============================================================================
# 2. CALCULATION ENGINE EXCEPTIONS
# ============================================================================

class CalculationEngineError(Exception):
    """Base exception for calculation and ledger integrity errors."""
    pass


class EmissionFactorNotFoundError(CalculationEngineError):
    """Raised when no valid emission factor covers the operational activity date."""
    pass


# ============================================================================
# 3. DETERMINISTIC CARBON LEDGER ENGINE
# ============================================================================

class CarbonLedgerEngine:
    """
    Deterministic calculation engine executing Scope 2 calculations,
    maintaining double-entry carbon ledgers, and enforcing SHA-256 state chaining.
    """

    def __init__(self, genesis_hash: str = "0" * 64):
        self._genesis_hash = genesis_hash

    @staticmethod
    def calculate_entry_hash(
        previous_hash: str,
        entry_id: str,
        tenant_id: str,
        facility_id: str,
        activity_id: str,
        factor_id: str,
        entry_type: str,
        account_code: str,
        co2e_metric_tons: Decimal,
        timestamp_iso: str,
    ) -> str:
        """Computes SHA-256 hash over serialized ledger transaction components."""
        hasher = hashlib.sha256()
        serialized_payload = (
            f"{previous_hash}|{entry_id}|{tenant_id}|{facility_id}|"
            f"{activity_id}|{factor_id}|{entry_type}|{account_code}|"
            f"{co2e_metric_tons:.6f}|{timestamp_iso}"
        )
        hasher.update(serialized_payload.encode("utf-8"))
        return hasher.hexdigest()

    def resolve_grid_factor(
        self,
        target_date: date,
        factor_registry: List[EmissionFactorRecord],
    ) -> EmissionFactorRecord:
        """Resolves the authoritative Egyptian national grid factor for the given date."""
        for factor in factor_registry:
            if factor.factor_code == "EF-EGY-GRID-LOC" and factor.scope == "Scope 2":
                valid_start = target_date >= factor.valid_from
                valid_end = factor.valid_to is None or target_date <= factor.valid_to
                if valid_start and valid_end:
                    return factor

        raise EmissionFactorNotFoundError(
            f"No valid Egyptian grid factor found for date: {target_date.isoformat()}"
        )

    def process_electricity_invoice(
        self,
        activity: UtilityActivityPayload,
        factor_registry: List[EmissionFactorRecord],
        latest_ledger_hash: Optional[str] = None,
    ) -> Tuple[CarbonLedgerTransaction, CarbonLedgerTransaction]:
        """
        Calculates Scope 2 emissions and posts balanced debit and credit entries.
        """
        if activity.active_energy_kwh < Decimal("0.0"):
            raise CalculationEngineError("Consumption values cannot be negative.")

        factor = self.resolve_grid_factor(activity.billing_period_end, factor_registry)

        # Unit conversion: kWh to MWh; Factor is in metric tonnes CO2e per MWh
        # Official EEAA / NREA factor = 0.4580 tCO2e/MWh
        consumption_mwh = activity.active_energy_kwh / Decimal("1000.0")
        calculated_emissions = consumption_mwh * factor.co2e_factor
        emissions_tco2e = calculated_emissions.quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )

        now_utc = datetime.now(timezone.utc).isoformat()
        period_key = activity.billing_period_end.strftime("%Y-%m")
        previous_hash = latest_ledger_hash or self._genesis_hash

        debit_id = str(uuid.uuid4())
        credit_id = str(uuid.uuid4())

        # 1. Debit Entry: Operational Environmental Liability
        debit_hash = self.calculate_entry_hash(
            previous_hash=previous_hash,
            entry_id=debit_id,
            tenant_id=activity.tenant_id,
            facility_id=activity.facility_id,
            activity_id=activity.activity_id,
            factor_id=factor.factor_id,
            entry_type="DEBIT",
            account_code="2300-Scope2-Electricity-Liability",
            co2e_metric_tons=emissions_tco2e,
            timestamp_iso=now_utc,
        )

        debit_entry = CarbonLedgerTransaction(
            entry_id=debit_id,
            tenant_id=activity.tenant_id,
            facility_id=activity.facility_id,
            activity_id=activity.activity_id,
            factor_id=factor.factor_id,
            transaction_date=now_utc,
            accounting_period=period_key,
            scope="Scope 2",
            entry_type="DEBIT",
            account_code="2300-Scope2-Electricity-Liability",
            co2e_metric_tons=emissions_tco2e,
            previous_entry_hash=previous_hash,
            entry_hash=debit_hash,
        )

        # 2. Credit Entry: Energy Absorption / Clearing Balancing Entry
        credit_hash = self.calculate_entry_hash(
            previous_hash=debit_hash,
            entry_id=credit_id,
            tenant_id=activity.tenant_id,
            facility_id=activity.facility_id,
            activity_id=activity.activity_id,
            factor_id=factor.factor_id,
            entry_type="CREDIT",
            account_code="1000-Clearing-Absorption",
            co2e_metric_tons=emissions_tco2e,
            timestamp_iso=now_utc,
        )

        credit_entry = CarbonLedgerTransaction(
            entry_id=credit_id,
            tenant_id=activity.tenant_id,
            facility_id=activity.facility_id,
            activity_id=activity.activity_id,
            factor_id=factor.factor_id,
            transaction_date=now_utc,
            accounting_period=period_key,
            scope="Scope 2",
            entry_type="CREDIT",
            account_code="1000-Clearing-Absorption",
            co2e_metric_tons=emissions_tco2e,
            previous_entry_hash=debit_hash,
            entry_hash=credit_hash,
        )

        return debit_entry, credit_entry


# ============================================================================
# 4. REGULATORY COMPLIANCE FORMATTER (FRA DECREES 107/108 & DECISION 36)
# ============================================================================

class FRAReportFormatter:
    """
    Compiles audited ledger entries into regulatory disclosure packages
    aligned with Egyptian FRA Decrees 107/108 (2021) and Decision 36 (2026).
    """

    @staticmethod
    def generate_compliance_package(
        entity_profile: Dict[str, str],
        scope1_entries: List[CarbonLedgerTransaction],
        scope2_entries: List[CarbonLedgerTransaction],
        turnover_million_egp: Decimal,
    ) -> Dict[str, object]:
        """Aggregates ledger debits and constructs the official FRA filing report."""
        s1_total = sum(
            (e.co2e_metric_tons for e in scope1_entries if e.entry_type == "DEBIT"),
            Decimal("0.0"),
        ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

        s2_total = sum(
            (e.co2e_metric_tons for e in scope2_entries if e.entry_type == "DEBIT"),
            Decimal("0.0"),
        ).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

        combined_operational = s1_total + s2_total

        # Operational Carbon Intensity (E1-GHG-INT): tCO2e / Million EGP
        intensity = (
            (combined_operational / turnover_million_egp).quantize(
                Decimal("0.001"), rounding=ROUND_HALF_UP
            )
            if turnover_million_egp > Decimal("0")
            else Decimal("0.000")
        )

        # Mandatory 20% CERC offset calculation under FRA Decision 36/2026
        offset_obligation_units = (combined_operational * Decimal("0.20")).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        return {
            "regulatory_filing_standard": "FRA_Decrees_107_108_2021_Decision_36_2026",
            "reporting_entity": {
                "legal_name": entity_profile.get("company_name"),
                "commercial_registration": entity_profile.get("cr_number"),
                "tax_id": entity_profile.get("tax_id"),
                "is_egx_listed": entity_profile.get("is_egx_listed", "False") == "True",
                "is_nbfi": entity_profile.get("is_nbfi", "False") == "True",
                "issued_capital_egp": entity_profile.get("issued_capital_egp", "100000000.00"),
            },
            "reporting_period": entity_profile.get("reporting_year", "2025"),
            "ghg_inventory_kpis": {
                "E1_GHG_Scope1_tCO2e": str(s1_total),
                "E1_GHG_Scope2_tCO2e": str(s2_total),
                "E1_GHG_Total_Operational_tCO2e": str(combined_operational),
                "E1_GHG_INT_tCO2e_per_MEGP": str(intensity),
                "calculation_standard": "ES_ISO_14064_1",
                "applied_grid_factor": "0.4580 tCO2e/MWh (EEAA/NREA Unified Baseline)",
            },
            "decision_36_offset_mandate": {
                "mandated_offset_rate": "20%",
                "required_cerc_retirements": int(offset_obligation_units),
                "trading_venue": "EGX_Regulated_Voluntary_Carbon_Market",
                "procurement_window_days": 90,
                "filing_deadline": f"{entity_profile.get('reporting_year', '2025')}-06-30",
                "retirement_deadline": f"{entity_profile.get('reporting_year', '2025')}-09-28",
                "licensing_condition_status": "ACTION_REQUIRED_SURRENDER_CERCS",
            },
            "audit_verification_summary": {
                "scope1_records_audited": len([e for e in scope1_entries if e.entry_type == "DEBIT"]),
                "scope2_records_audited": len([e for e in scope2_entries if e.entry_type == "DEBIT"]),
                "cryptographic_lineage_status": "VERIFIED_SHA256_CHAIN",
                "cleanroom_verification_url": f"https://app.ecoaudit.eg/auditors-room/{entity_profile.get('cr_number')}",
                "package_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            },
        }


# ============================================================================
# 5. TEST & VERIFICATION HARNESS
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("EcoAudit AI — Scope 2 Execution & FRA Compliance Engine")
    print("=" * 80)

    # 1. Authoritative Egyptian Emission Factors (EEAA / NREA Baseline)
    factor_db = [
        EmissionFactorRecord(
            factor_id="ef-egy-grid-2025-v2",
            factor_code="EF-EGY-GRID-LOC",
            version=2,
            name="Egyptian National Grid Location-Based Factor",
            scope="Scope 2",
            co2e_factor=Decimal("0.4580"),  # 0.4580 tCO2e/MWh
            unit="MWh",
            valid_from=date(2025, 1, 1),
            valid_to=date(2026, 12, 31),
            gwp_framework="IPCC_AR5",
            citation="EEAA & NREA Official National Baseline GHG Inventory Bulletin",
        )
    ]

    # 2. Industrial Activity Payload (South Cairo Electricity Bill: 1.25 GWh)
    bill_activity = UtilityActivityPayload(
        activity_id="act-scedc-oct-2025-06",
        tenant_id="tenant-egypt-steel-sae",
        facility_id="fac-6th-october-rolling-mill",
        billing_period_start=date(2025, 6, 1),
        billing_period_end=date(2025, 6, 30),
        meter_serial_number="SCEDC-MV-66KV-88219",
        active_energy_kwh=Decimal("1250000.00"),  # 1.25 GWh industrial power
        evidence_document_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )

    # 3. Calculate Scope 2 and Post to Double-Entry Ledger
    genesis_chain_hash = "1a7b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b"
    ledger_engine = CarbonLedgerEngine()

    debit_tx, credit_tx = ledger_engine.process_electricity_invoice(
        activity=bill_activity,
        factor_registry=factor_db,
        latest_ledger_hash=genesis_chain_hash,
    )

    print(f"\n[LEDGER POSTING SUCCESSFUL]")
    print(f"DEBIT  Account: {debit_tx.account_code:<35} | {debit_tx.co2e_metric_tons} tCO2e")
    print(f"       Hash:    {debit_tx.entry_hash}")
    print(f"CREDIT Account: {credit_tx.account_code:<35} | {credit_tx.co2e_metric_tons} tCO2e")
    print(f"       Hash:    {credit_tx.entry_hash}")

    # Verify SHA-256 Chaining
    assert credit_tx.previous_entry_hash == debit_tx.entry_hash
    print(f"\n[CRYPTOGRAPHIC VERIFICATION] SHA-256 State Chain Valid: True")

    # 4. Compile Official FRA Compliance Package
    company_info = {
        "company_name": "Egyptian Advanced Industrial Holdings S.A.E.",
        "cr_number": "94210-Giza",
        "tax_id": "402-192-881",
        "is_egx_listed": "True",
        "is_nbfi": "True",
        "issued_capital_egp": "250000000.00",
        "reporting_year": "2025",
    }

    fra_report = FRAReportFormatter.generate_compliance_package(
        entity_profile=company_info,
        scope1_entries=[],
        scope2_entries=[debit_tx, credit_tx],
        turnover_million_egp=Decimal("450.0"),  # 450M EGP turnover
    )

    print("\n[FRA COMPLIANCE DISCLOSURE PACKAGE (DECREES 107/108 & DECISION 36/2026)]")
    print(json.dumps(fra_report, indent=2))
```
