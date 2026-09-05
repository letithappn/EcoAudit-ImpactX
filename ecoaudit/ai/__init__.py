"""AI Data Extraction & Classification layer for EcoAudit.

This package provides the AI-powered classification pipeline that converts
messy corporate data into structured ActivityData candidates. The AI is
a classification layer only — the deterministic carbon engine remains
the sole calculator.

Architecture:
    Raw Corporate Data
        → AI Classification (this package)
        → Structured ActivityCandidate
        → Post-AI Validation (firewall)
        → Validated ActivityData
        → Deterministic Carbon Engine (ecoaudit.carbon)
        → Auditable Results
"""
