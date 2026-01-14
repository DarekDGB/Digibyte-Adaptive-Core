# src/adaptive_core/v3/envelope.py

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Literal

from .reason_ids import ReasonId
from .report_models import UpgradeReportV3


SignatureStatus = Literal["ABSENT", "PRESENT", "UNSUPPORTED"]


@dataclass(frozen=True, slots=True)
class ReportEnvelopeV3:
    """
    Integrity envelope for UpgradeReportV3.

    - Deterministic hash of report JSON
    - Explicit signature status (no silent fallback)
    - No execution authority
    """

    report_hash: str
    canonical_json: str

    classical_signature: SignatureStatus
    pqc_signature: SignatureStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_hash": self.report_hash,
            "classical_signature": self.classical_signature,
            "pqc_signature": self.pqc_signature,
        }


def _stable_hash(payload: str) -> str:
    """
    Deterministic SHA-256 hash of canonical JSON string.
    """
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def create_report_envelope(
    *,
    report: UpgradeReportV3,
    canonical_json: str,
    classical_signature: SignatureStatus = "ABSENT",
    pqc_signature: SignatureStatus = "ABSENT",
) -> ReportEnvelopeV3:
    """
    Create a deterministic integrity envelope for a report.

    Guardrails:
    - canonical_json MUST be stable (sorted keys, no randomness)
    - signature status must be explicit
    """
    if not canonical_json or not isinstance(canonical_json, str):
        raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: canonical_json")

    for status in (classical_signature, pqc_signature):
        if status not in ("ABSENT", "PRESENT", "UNSUPPORTED"):
            raise ValueError(f"{ReasonId.AC_V3_REPORT_INVALID.value}: invalid signature status")

    report_hash = _stable_hash(canonical_json)

    return ReportEnvelopeV3(
        report_hash=report_hash,
        canonical_json=canonical_json,
        classical_signature=classical_signature,
        pqc_signature=pqc_signature,
    )
