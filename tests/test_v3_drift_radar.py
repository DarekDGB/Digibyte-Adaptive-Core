from adaptive_core.v3.drift import LayerContract, detect_contract_drift
from adaptive_core.v3.graph import render_drift_dot


def test_detect_contract_drift_simple_mismatch():
    contracts = [
        LayerContract(
            layer="Sentinel",
            assumptions={"meta.canonical": "true"},
        ),
        LayerContract(
            layer="DQSN",
            assumptions={"meta.canonical": "false"},
        ),
    ]

    findings = detect_contract_drift(contracts)
    assert len(findings) == 1

    f = findings[0]
    assert f.finding_id == "AC-DRIFT::meta.canonical"
    assert "Sentinel" in f.evidence["layers"]
    assert "DQSN" in f.evidence["layers"]


def test_render_drift_dot_is_deterministic():
    contracts = [
        LayerContract(
            layer="A",
            assumptions={"x": "1"},
        ),
        LayerContract(
            layer="B",
            assumptions={"x": "2"},
        ),
    ]
    findings = detect_contract_drift(contracts)
    dot1 = render_drift_dot(findings)
    dot2 = render_drift_dot(findings)

    assert dot1 == dot2
    assert "digraph DriftRadar" in dot1
