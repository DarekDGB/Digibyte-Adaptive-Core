# src/adaptive_core/v3/node_summary.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Mapping

from .context_hash import compute_context_hash
from .reason_ids import ReasonId


@dataclass(frozen=True, slots=True)
class NodeSummaryEventV3:
    """
    Strict cross-node summary event.

    This is intentionally minimal and privacy-preserving:
    - node_id is a pseudonymous identifier (no IPs, no secrets)
    - window_start/window_end are ISO8601 with trailing Z
    - counters are aggregated counts only (no raw data)
    """
    node_id: str
    window_start: str
    window_end: str
    total_events: int
    by_upstream_reason_id: Dict[str, int]

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "total_events": self.total_events,
            "by_upstream_reason_id": self.by_upstream_reason_id,
        }


def _require_nonempty_str(m: Mapping[str, Any], key: str) -> str:
    if key not in m:
        raise ValueError(f"{ReasonId.AC_V3_MISSING_FIELD.value}: missing {key!r}")
    v = m[key]
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: {key!r} must be non-empty str")
    return v.strip()


def _require_iso_z(m: Mapping[str, Any], key: str) -> str:
    ts = _require_nonempty_str(m, key)
    if not ts.endswith("Z"):
        raise ValueError(f"{ReasonId.AC_V3_TIMESTAMP_INVALID.value}: {key} must end with 'Z'")
    try:
        datetime.fromisoformat(ts[:-1])
    except ValueError as e:
        raise ValueError(f"{ReasonId.AC_V3_TIMESTAMP_INVALID.value}: invalid ISO8601 for {key}") from e
    return ts


def _require_int_ge0(m: Mapping[str, Any], key: str) -> int:
    if key not in m:
        raise ValueError(f"{ReasonId.AC_V3_MISSING_FIELD.value}: missing {key!r}")
    v = m[key]
    if isinstance(v, bool):
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: {key!r} must be int")
    try:
        n = int(v)
    except Exception as e:
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: {key!r} must be int") from e
    if n < 0:
        raise ValueError(f"{ReasonId.AC_V3_NON_CANONICAL.value}: {key!r} must be >= 0")
    return n


def _require_reason_counter(m: Mapping[str, Any], key: str) -> Dict[str, int]:
    if key not in m:
        raise ValueError(f"{ReasonId.AC_V3_MISSING_FIELD.value}: missing {key!r}")
    v = m[key]
    if not isinstance(v, dict):
        raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: {key!r} must be dict")
    out: Dict[str, int] = {}
    for rk, rv in v.items():
        if not isinstance(rk, str) or not rk.strip():
            raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: reason_id key must be non-empty str")
        if isinstance(rv, bool):
            raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: reason_id count must be int")
        try:
            c = int(rv)
        except Exception as e:
            raise ValueError(f"{ReasonId.AC_V3_TYPE_INVALID.value}: reason_id count must be int") from e
        if c < 0:
            raise ValueError(f"{ReasonId.AC_V3_NON_CANONICAL.value}: reason_id count must be >= 0")
        out[rk.strip()] = c
    return out


def canonicalize_node_summary(raw: Mapping[str, Any]) -> tuple[NodeSummaryEventV3, str]:
    """
    Canonicalize a raw mapping into NodeSummaryEventV3 + deterministic context_hash.
    """
    if not isinstance(raw, Mapping):
        raise ValueError(f"{ReasonId.AC_V3_INVALID_EVENT.value}: raw must be a mapping")

    node_id = _require_nonempty_str(raw, "node_id")
    window_start = _require_iso_z(raw, "window_start")
    window_end = _require_iso_z(raw, "window_end")
    total_events = _require_int_ge0(raw, "total_events")
    by_reason = _require_reason_counter(raw, "by_upstream_reason_id")

    ev = NodeSummaryEventV3(
        node_id=node_id,
        window_start=window_start,
        window_end=window_end,
        total_events=total_events,
        by_upstream_reason_id=by_reason,
    )
    ctx = compute_context_hash(ev.to_canonical_dict())
    return ev, ctx
