# src/adaptive_core/v3/events.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional


@dataclass(frozen=True, slots=True)
class ObservedEventV3:
    """
    Strict v3 event shape consumed by Adaptive Core v3.

    This is intentionally stricter than v2:
    - no silent defaults
    - timestamp must be provided (ISO8601 with trailing 'Z')
    - meta must be a dict with string keys (values JSON-serializable)
    """

    source_layer: str
    event_type: str
    severity: float
    timestamp: str
    correlation_id: str
    meta: Dict[str, Any]
    reason_id: Optional[str] = None  # reason code from upstream (optional)

    def to_canonical_dict(self) -> Dict[str, Any]:
        """
        Canonical dict form used for hashing / deterministic serialization.
        Key order does not matter (hashing uses sorted keys).
        """
        d: Dict[str, Any] = {
            "source_layer": self.source_layer,
            "event_type": self.event_type,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "meta": self.meta,
        }
        if self.reason_id is not None:
            d["reason_id"] = self.reason_id
        return d

    @staticmethod
    def from_mapping(m: Mapping[str, Any]) -> "ObservedEventV3":
        # This is a thin constructor; strict validation happens in canonicalize.py
        return ObservedEventV3(
            source_layer=str(m.get("source_layer", "")),
            event_type=str(m.get("event_type", "")),
            severity=float(m.get("severity", 0.0)),
            timestamp=str(m.get("timestamp", "")),
            correlation_id=str(m.get("correlation_id", "")),
            meta=dict(m.get("meta", {})) if isinstance(m.get("meta", {}), dict) else {},
            reason_id=(None if m.get("reason_id") is None else str(m.get("reason_id"))),
        )
