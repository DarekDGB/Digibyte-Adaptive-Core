from __future__ import annotations

import pytest

from adaptive_core.v3.envelope import _stable_hash, create_report_envelope
from adaptive_core.v3.report_models import CapabilitiesV3, UpgradeReportV3


def _dummy_report() -> UpgradeReportV3:
    return UpgradeReportV3(
        report_id="r-1",
        report_type="UPGRADE_REPORT",
        target_layers=["sentinel_ai_v3"],
        evidence={
            "total_events": 1,
            "by_source_layer": {"sentinel_ai_v3": 1},
            "by_event_type": {"x": 1},
            "by_upstream_reason_id": {"R": 1},
            "drift_contracts_provided": 0,
            "drift_findings": 0,
        },
        findings=[],
        guardrails=[],
        guardrail_titles={},
        confidence=0.99,
        confidence_breakdown={"recurrence_ratio": 0.0, "max_severity": 0.0, "reproducibility": 0.0, "cross_layer_impact": 0.0},
        capabilities=CapabilitiesV3(envelope=True, correlation=False, archival=False, telemetry=False),
        drift_dot=None,
        recommended_actions=[],
        required_tests=[],
        exit_criteria=[],
        forbidden_actions=[],
    )


def test_stable_hash_is_deterministic_and_sha256_length():
    h1 = _stable_hash('{"a":1}')
    h2 = _stable_hash('{"a":1}')
    h3 = _stable_hash('{"a":2}')
    assert h1 == h2
    assert h1 != h3
    assert isinstance(h1, str)
    assert len(h1) == 64


def test_create_report_envelope_happy_path_and_to_dict():
    report = _dummy_report()
    canonical_json = '{"a":1}'
    env = create_report_envelope(
        report=report,
        canonical_json=canonical_json,
        classical_signature="ABSENT",
        pqc_signature="UNSUPPORTED",
    )

    assert env.canonical_json == canonical_json
    assert env.report_hash == _stable_hash(canonical_json)
    assert env.classical_signature == "ABSENT"
    assert env.pqc_signature == "UNSUPPORTED"

    d = env.to_dict()
    assert d["report_hash"] == env.report_hash
    assert d["classical_signature"] == "ABSENT"
    assert d["pqc_signature"] == "UNSUPPORTED"


def test_create_report_envelope_rejects_bad_canonical_json():
    report = _dummy_report()

    with pytest.raises(ValueError) as e:
        create_report_envelope(report=report, canonical_json="")  # empty
    assert "AC_V3_REPORT_INVALID" in str(e.value)

    with pytest.raises(ValueError) as e2:
        create_report_envelope(report=report, canonical_json=None)  # type: ignore[arg-type]
    assert "AC_V3_REPORT_INVALID" in str(e2.value)


def test_create_report_envelope_rejects_bad_signature_status():
    report = _dummy_report()
    with pytest.raises(ValueError) as e:
        create_report_envelope(
            report=report,
            canonical_json='{"a":1}',
            classical_signature="NOPE",  # type: ignore[arg-type]
            pqc_signature="ABSENT",
        )
    assert "AC_V3_REPORT_INVALID" in str(e.value)
