from adaptive_core.v3.correlation import aggregate_node_summaries
from adaptive_core.v3.evidence_store import EvidenceSnapshot
from adaptive_core.v3.node_summary import canonicalize_node_summary
from adaptive_core.v3.pipeline import run_v3_pipeline
from adaptive_core.v3.report_models import CapabilitiesV3


def _summary(node_id: str) -> dict:
    return {
        "node_id": node_id,
        "window_start": "2026-01-14T00:00:00Z",
        "window_end": "2026-01-14T01:00:00Z",
        "total_events": 100,
        "by_upstream_reason_id": {"WIDESPREAD": 3},
    }


def test_pipeline_includes_correlation_findings_when_enabled():
    e1, _ = canonicalize_node_summary(_summary("n1"))
    e2, _ = canonicalize_node_summary(_summary("n2"))
    e3, _ = canonicalize_node_summary(_summary("n3"))
    e4, _ = canonicalize_node_summary({"node_id": "n4", "window_start": "2026-01-14T00:00:00Z",
                                       "window_end": "2026-01-14T01:00:00Z", "total_events": 100,
                                       "by_upstream_reason_id": {"OTHER": 1}})

    corr = aggregate_node_summaries([e1, e2, e3, e4])

    snap = EvidenceSnapshot(
        total_events=10,
        by_source_layer={"dqsn": 10},
        by_event_type={"reject": 10},
        by_upstream_reason_id={"SPIKE": 10},
    )

    caps = CapabilitiesV3(envelope="ABSENT", correlation="ON", archival="OFF", telemetry="OFF")

    _, json_text, md_text, _ = run_v3_pipeline(
        report_id="AC-UR-STEP10-0001",
        target_layers=["DQSN"],
        snapshot=snap,
        confidence_threshold=0.0,
        capabilities=caps,
        correlation_snapshot=corr,
        include_correlation=True,
    )

    assert "AC-CORR::REASON-WIDESPREAD::WIDESPREAD" in json_text
