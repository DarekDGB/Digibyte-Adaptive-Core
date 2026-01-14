# src/adaptive_core/v3/canonicalize.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Mapping, Tuple

from .context_hash import compute_context_hash
from .events import ObservedEventV3
from .reason_ids import ReasonId


@dataclass(frozen=True, slots=True)
class CanonicalizeResult:
    event: ObservedEventV3
    context_hash: str


def _require_str(m: Mapping[str, Any], key: str) -> str:
    if key not in m:
        raise ValueError(f"{ReasonId.AC_V3_MISSING_FIELD.value}: missing {key!r}")
    v = m[key]
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: {key!r} must be non-empty str")
    return v


def _require_float_0_1(m: Mapping[str, Any], key: str) -> float:
    if key not in m:
        raise ValueError(f"{ReasonId.AC_V3_MISSING_FIELD.value}: missing {key!r}")
    v = m[key]
    try:
        f = float(v)
    except Exception as e:
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: {key!r} must be float") from e
    if f < 0.0 or f > 1.0:
        raise ValueError(f"{ReasonId.AC_V3_NON_CANONICAL.value}: {key!r} must be in [0.0, 1.0]")
    return f


def _require_timestamp_z(m: Mapping[str, Any], key: str) -> str:
    ts = _require_str(m, key)
    # v3 requires explicit timestamp, ISO8601, with trailing 'Z'
    if not ts.endswith("Z"):
        raise ValueError(f"{ReasonId.AC_V3_TIMESTAMP_INVALID.value}: timestamp must end with 'Z'")
    try:
        # fromisoformat does not accept trailing Z; strip it for parsing
        datetime.fromisoformat(ts[:-1])
    except ValueError as e:
        raise ValueError(f"{ReasonId.AC_V3_TIMESTAMP_INVALID.value}: invalid ISO8601 timestamp") from e
    return ts


def _require_meta(m: Mapping[str, Any], key: str) -> Dict[str, Any]:
    if key not in m:
        raise ValueError(f"{ReasonId.AC_V3_MISSING_FIELD.value}: missing {key!r}")
    meta = m[key]
    if not isinstance(meta, dict):
        raise ValueError(f"{ReasonId.AC_V3_META_INVALID.value}: meta must be dict")
    # enforce string keys (canonical)
    for k in meta.keys():
        if not isinstance(k, str):
            raise ValueError(f"{ReasonId.AC_V3_META_INVALID.value}: meta keys must be str")
    return dict(meta)


def canonicalize_event(raw: Mapping[str, Any]) -> CanonicalizeResult:
    """
    Canonicalize a raw mapping into a strict ObservedEventV3 + deterministic context_hash.

    Fail-closed:
    - missing fields => error with reason id
    - type mismatch => error with reason id
    - no silent defaults
    """
    if not isinstance(raw, Mapping):
        raise ValueError(f"{ReasonId.AC_V3_INVALID_EVENT.value}: raw must be a mapping")

    source_layer = _require_str(raw, "source_layer")
    event_type = _require_str(raw, "event_type")
    severity = _require_float_0_1(raw, "severity")
    timestamp = _require_timestamp_z(raw, "timestamp")
    correlation_id = _require_str(raw, "correlation_id")
    meta = _require_meta(raw, "meta")

    reason_id = raw.get("reason_id")
    if reason_id is not None and (not isinstance(reason_id, str) or not reason_id.strip()):
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: 'reason_id' must be str or None")

    ev = ObservedEventV3(
        source_layer=source_layer,
        event_type=event_type,
        severity=severity,
        timestamp=timestamp,
        correlation_id=correlation_id,
        meta=meta,
        reason_id=reason_id,
    )

    canonical = ev.to_canonical_dict()
    ctx = compute_context_hash(canonical)
    return CanonicalizeResult(event=ev, context_hash=ctx)
