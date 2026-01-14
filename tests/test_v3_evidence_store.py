from __future__ import annotations

import pytest

from adaptive_core.v3.evidence_store import EvidenceStoreV3
from adaptive_core.v3.canonicalize import CanonicalizeResult
from adaptive_core.v3.events import ObservedEventV3


def _item(
    *,
    source_layer: str,
    event_type: str,
    reason_id: str | None = None,
    ctx: str = "ctx",
) -> CanonicalizeResult:
    ev = ObservedEventV3(
        source_layer=source_layer,
        event_type=event_type,
        severity=0.5,
        timestamp="2026-01-14T00:00:00Z",
        correlation_id="cid-1",
        meta={"k": "v"},
        reason_id=reason_id,
    )
    return CanonicalizeResult(event=ev, context_hash=ctx)


def test_store_init_rejects_non_positive_max_events():
    with pytest.raises(ValueError):
        EvidenceStoreV3(max_events=0)

    with pytest.raises(ValueError):
        EvidenceStoreV3(max_events=-1)


def test_max_events_property_exposes_config():
    s = EvidenceStoreV3(max_events=2)
    assert s.max_events == 2


def test_add_snapshot_and_iter_window_order_and_reason_counting():
    s = EvidenceStoreV3(max_events=10)
    a = _item(source_layer="A", event_type="t1", reason_id="R1", ctx="a")
    b = _item(source_layer="B", event_type="t2", reason_id=None, ctx="b")

    s.add(a)
    s.add(b)

    snap = s.snapshot()
    assert snap.total_events == 2
    assert snap.by_source_layer == {"A": 1, "B": 1}
    assert snap.by_event_type == {"t1": 1, "t2": 1}
    assert snap.by_upstream_reason_id == {"R1": 1}  # reason_id counted only when present

    # iter_window is stable oldest->newest and returns a list copy
    w = list(s.iter_window())
    assert [x.context_hash for x in w] == ["a", "b"]


def test_eviction_decrements_and_deletes_zero_keys():
    # This test targets the delete-on-zero branches in _decrement()
    s = EvidenceStoreV3(max_events=2)

    first = _item(source_layer="A", event_type="t1", reason_id="R1", ctx="first")
    second = _item(source_layer="B", event_type="t2", reason_id=None, ctx="second")
    third = _item(source_layer="B", event_type="t2", reason_id=None, ctx="third")

    s.add(first)
    s.add(second)

    # Adding third evicts first (A/t1/R1) and should remove those keys entirely
    s.add(third)

    snap = s.snapshot()
    assert snap.total_events == 2
    assert snap.by_source_layer == {"B": 2}
    assert snap.by_event_type == {"t2": 2}
    assert snap.by_upstream_reason_id == {}  # R1 removed after eviction/decrement to zero

    # Window order should now be [second, third]
    w = list(s.iter_window())
    assert [x.context_hash for x in w] == ["second", "third"]
