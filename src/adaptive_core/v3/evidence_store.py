# src/adaptive_core/v3/evidence_store.py

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, List, Optional, Tuple

from .canonicalize import CanonicalizeResult


@dataclass(frozen=True, slots=True)
class EvidenceSnapshot:
    """
    Deterministic snapshot of evidence counters.
    """
    total_events: int
    by_source_layer: Dict[str, int]
    by_event_type: Dict[str, int]
    by_upstream_reason_id: Dict[str, int]


class EvidenceStoreV3:
    """
    Deterministic hot-window evidence store.

    - bounded memory (maxlen)
    - deterministic counters
    - no persistence in Step 3 (future step can add archival)
    """

    def __init__(self, max_events: int = 1000) -> None:
        if max_events <= 0:
            raise ValueError("max_events must be > 0")
        self._max_events = max_events
        self._window: Deque[CanonicalizeResult] = deque(maxlen=max_events)

        self._by_source_layer: Counter[str] = Counter()
        self._by_event_type: Counter[str] = Counter()
        self._by_upstream_reason_id: Counter[str] = Counter()

    @property
    def max_events(self) -> int:
        return self._max_events

    def add(self, item: CanonicalizeResult) -> None:
        """
        Add a canonicalized event into the hot window.

        If the deque is full, the oldest item is evicted and counters are updated.
        """
        # If eviction will occur, remove counts for the evicted record first.
        if len(self._window) == self._window.maxlen:
            evicted = self._window[0]
            self._decrement(evicted)

        self._window.append(item)
        self._increment(item)

    def _increment(self, item: CanonicalizeResult) -> None:
        ev = item.event
        self._by_source_layer[ev.source_layer] += 1
        self._by_event_type[ev.event_type] += 1
        if ev.reason_id:
            self._by_upstream_reason_id[ev.reason_id] += 1

    def _decrement(self, item: CanonicalizeResult) -> None:
        ev = item.event
        self._by_source_layer[ev.source_layer] -= 1
        if self._by_source_layer[ev.source_layer] <= 0:
            del self._by_source_layer[ev.source_layer]

        self._by_event_type[ev.event_type] -= 1
        if self._by_event_type[ev.event_type] <= 0:
            del self._by_event_type[ev.event_type]

        if ev.reason_id:
            self._by_upstream_reason_id[ev.reason_id] -= 1
            if self._by_upstream_reason_id[ev.reason_id] <= 0:
                del self._by_upstream_reason_id[ev.reason_id]

    def snapshot(self) -> EvidenceSnapshot:
        return EvidenceSnapshot(
            total_events=len(self._window),
            by_source_layer=dict(self._by_source_layer),
            by_event_type=dict(self._by_event_type),
            by_upstream_reason_id=dict(self._by_upstream_reason_id),
        )

    def iter_window(self) -> Iterable[CanonicalizeResult]:
        # stable iteration order: deque order (oldest->newest)
        return list(self._window)
