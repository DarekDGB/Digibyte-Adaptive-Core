from adaptive_core.v3.canonicalize import canonicalize_event


def test_v3_context_hash_is_deterministic_and_meta_order_independent():
    raw1 = {
        "source_layer": "dqsn",
        "event_type": "reject",
        "severity": 0.5,
        "timestamp": "2026-01-14T00:00:00Z",
        "correlation_id": "c-123",
        "meta": {"b": 2, "a": 1},
        "reason_id": "DQSN_META_AMBIGUOUS",
    }
    raw2 = {
        "source_layer": "dqsn",
        "event_type": "reject",
        "severity": 0.5,
        "timestamp": "2026-01-14T00:00:00Z",
        "correlation_id": "c-123",
        "meta": {"a": 1, "b": 2},  # different key order
        "reason_id": "DQSN_META_AMBIGUOUS",
    }

    r1 = canonicalize_event(raw1)
    r2 = canonicalize_event(raw2)

    assert r1.context_hash == r2.context_hash
    assert r1.event == r2.event


def test_v3_missing_required_field_fails_closed():
    raw = {
        "source_layer": "dqsn",
        "event_type": "reject",
        "severity": 0.5,
        "timestamp": "2026-01-14T00:00:00Z",
        "correlation_id": "c-123",
        # missing meta
    }
    try:
        canonicalize_event(raw)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "AC_V3_MISSING_FIELD" in str(e)


def test_v3_timestamp_requires_trailing_z():
    raw = {
        "source_layer": "dqsn",
        "event_type": "reject",
        "severity": 0.5,
        "timestamp": "2026-01-14T00:00:00",  # missing Z
        "correlation_id": "c-123",
        "meta": {},
    }
    try:
        canonicalize_event(raw)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "AC_V3_TIMESTAMP_INVALID" in str(e)
