from adaptive_core.v3.evidence_store import EvidenceSnapshot
from adaptive_core.v3.pipeline import run_v3_pipeline
from adaptive_core.v3.report_models import CapabilitiesV3


def test_v3_reports_do_not_embed_runtime_timestamps():
    """
    Guardrail: Determinism Guardian.
    Reports must not embed runtime timestamps that would break replay.
    """
    snap = EvidenceSnapshot(
        total_events=10,
        by_source_layer={"dqsn": 10},
        by_event_type={"reject": 10},
        by_upstream_reason_id={"SPIKE": 10},
    )
    caps = CapabilitiesV3(envelope="ABSENT", correlation="OFF", archival="OFF", telemetry="OFF")

    _, json_text, md_text, _ = run_v3_pipeline(
        report_id="AC-UR-NO-TIME-0001",
        target_layers=["DQSN"],
        snapshot=snap,
        confidence_threshold=0.0,
        capabilities=caps,
    )

    # We should NOT see 'Created' timestamps or utc_now usage in the rendered outputs.
    # (Report IDs are allowed; times are not in Step 4/5/6 reports.)
    assert "Created" not in md_text
    assert "created" not in json_text.lower()
