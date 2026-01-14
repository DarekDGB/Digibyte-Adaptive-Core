from adaptive_core.v3.evidence_store import EvidenceSnapshot
from adaptive_core.v3.pipeline import run_v3_pipeline
from adaptive_core.v3.report_models import CapabilitiesV3


def test_v3_pipeline_is_replay_deterministic_byte_for_byte():
    """
    Determinism Guardian:
    Same input -> same JSON -> same hash, across multiple runs.
    """
    snap = EvidenceSnapshot(
        total_events=10,
        by_source_layer={"dqsn": 10},
        by_event_type={"reject": 10},
        by_upstream_reason_id={"SPIKE": 10},
    )

    caps = CapabilitiesV3(envelope="ABSENT", correlation="OFF", archival="OFF", telemetry="OFF")

    r1, j1, m1, e1 = run_v3_pipeline(
        report_id="AC-UR-REPLAY-0001",
        target_layers=["DQSN"],
        snapshot=snap,
        confidence_threshold=0.0,  # force UPGRADE_REPORT
        capabilities=caps,
    )
    r2, j2, m2, e2 = run_v3_pipeline(
        report_id="AC-UR-REPLAY-0001",
        target_layers=["DQSN"],
        snapshot=snap,
        confidence_threshold=0.0,
        capabilities=caps,
    )

    assert j1 == j2
    assert m1 == m2
    assert e1.report_hash == e2.report_hash

    # sanity: report id stable
    assert "AC-UR-REPLAY-0001" in j1
    assert "AC-UR-REPLAY-0001" in m1


def test_v3_low_confidence_is_still_deterministic():
    snap = EvidenceSnapshot(
        total_events=0,
        by_source_layer={},
        by_event_type={},
        by_upstream_reason_id={},
    )
    caps = CapabilitiesV3(envelope="ABSENT", correlation="OFF", archival="OFF", telemetry="OFF")

    r1, j1, m1, e1 = run_v3_pipeline(
        report_id="AC-UR-REPLAY-0002",
        target_layers=["DQSN"],
        snapshot=snap,
        confidence_threshold=0.60,  # likely notice
        capabilities=caps,
    )
    r2, j2, m2, e2 = run_v3_pipeline(
        report_id="AC-UR-REPLAY-0002",
        target_layers=["DQSN"],
        snapshot=snap,
        confidence_threshold=0.60,
        capabilities=caps,
    )

    assert j1 == j2
    assert m1 == m2
    assert e1.report_hash == e2.report_hash
    assert r1.report_type == r2.report_type
