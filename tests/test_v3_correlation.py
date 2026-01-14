from adaptive_core.v3.correlation import aggregate_node_summaries, generate_correlation_findings
from adaptive_core.v3.node_summary import canonicalize_node_summary


def _summary(node_id: str, reason_id: str, count: int) -> dict:
    return {
        "node_id": node_id,
        "window_start": "2026-01-14T00:00:00Z",
        "window_end": "2026-01-14T01:00:00Z",
        "total_events": 100,
        "by_upstream_reason_id": {reason_id: count},
    }


def test_correlation_finding_widespread_reason_id():
    # 4 nodes, 3 report same reason -> should trigger (min_nodes=3, min_nodes_ratio=0.50)
    e1, _ = canonicalize_node_summary(_summary("n1", "RISK", 5))
    e2, _ = canonicalize_node_summary(_summary("n2", "RISK", 1))
    e3, _ = canonicalize_node_summary(_summary("n3", "RISK", 2))
    e4, _ = canonicalize_node_summary(_summary("n4", "OTHER", 9))

    snap = aggregate_node_summaries([e1, e2, e3, e4])
    findings = generate_correlation_findings(snap, min_nodes=3, min_nodes_ratio=0.50)

    assert any(f.finding_id == "AC-CORR::REASON-WIDESPREAD::RISK" for f in findings)
