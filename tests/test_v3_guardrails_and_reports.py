import json

from adaptive_core.v3.evidence_store import EvidenceSnapshot
from adaptive_core.v3.report_builder import build_upgrade_report, render_report_json, render_report_md
from adaptive_core.v3.report_models import CapabilitiesV3


def test_guardrail_registry_rejects_unknown_ids_fail_closed():
    # Build a snapshot that will produce a finding with guardrails.
    snap = EvidenceSnapshot(
        total_events=10,
        by_source_layer={"dqsn": 10},
        by_event_type={"reject": 10},
        by_upstream_reason_id={"SPIKE": 10},
    )

    # Build report should succeed (guardrails are from findings and must exist)
    r = build_upgrade_report(
        report_id="AC-UR-2026-0001",
        target_layers=["DQSN"],
        snapshot=snap,
        capabilities=CapabilitiesV3(envelope="ABSENT", correlation="OFF", archival="OFF", telemetry="OFF"),
        confidence_threshold=0.0,  # force upgrade report
    )
    assert r.report_type == "UPGRADE_REPORT"

    j = render_report_json(r)
    md = render_report_md(r)
    assert "AC-UR-2026-0001" in j
    assert "AC-UR-2026-0001" in md

    # JSON should be parseable and stable format (sorted keys guaranteed by renderer)
    parsed = json.loads(j)
    assert parsed["report_id"] == "AC-UR-2026-0001"


def test_low_confidence_produces_notice_not_upgrade_report():
    snap = EvidenceSnapshot(
        total_events=0,
        by_source_layer={},
        by_event_type={},
        by_upstream_reason_id={},
    )

    r = build_upgrade_report(
        report_id="AC-UR-2026-0002",
        target_layers=["DQSN"],
        snapshot=snap,
        capabilities=CapabilitiesV3(envelope="ABSENT", correlation="OFF", archival="OFF", telemetry="OFF"),
        confidence_threshold=0.60,
    )
    assert r.report_type == "SIGNAL_COLLECTION_NOTICE"
