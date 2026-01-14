# src/adaptive_core/v3/pipeline.py

from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Literal, Tuple

from .evidence_store import EvidenceSnapshot
from .envelope import ReportEnvelopeV3, create_report_envelope
from .report_builder import build_upgrade_report, render_report_json, render_report_md
from .report_models import CapabilitiesV3, UpgradeReportV3


def run_v3_pipeline(
    *,
    report_id: str,
    target_layers: list[str],
    snapshot: EvidenceSnapshot,
    confidence_threshold: float,
    capabilities: CapabilitiesV3,
) -> Tuple[UpgradeReportV3, str, str, ReportEnvelopeV3]:
    """
    Deterministic v3 pipeline runner.

    Returns:
    - report object
    - canonical JSON (stable renderer)
    - markdown (stable renderer)
    - envelope (hash + signature status)
    """
    report = build_upgrade_report(
        report_id=report_id,
        target_layers=target_layers,
        snapshot=snapshot,
        capabilities=capabilities,
        confidence_threshold=confidence_threshold,
    )

    canonical_json = render_report_json(report)
    markdown = render_report_md(report)

    # Envelope is created explicitly (no hidden authority)
    envelope = create_report_envelope(
        report=report,
        canonical_json=canonical_json,
        classical_signature="ABSENT",
        pqc_signature="ABSENT",
    )

    return report, canonical_json, markdown, envelope
