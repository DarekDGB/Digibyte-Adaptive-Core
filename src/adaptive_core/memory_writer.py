"""
Adaptive Memory Writer

This module is the small bridge that takes AdaptiveEvent objects
(or raw dict payloads) and stores them in a simple event sink.

Right now it uses an in-memory list so the integration stays
lightweight. Later, DigiByte nodes / wallets can swap this out
for a DB, file, or remote collector – without changing Sentinel.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Protocol, List, Optional, Any

from .models import AdaptiveEvent


class EventSink(Protocol):
    """
    Minimal protocol for anything that can store AdaptiveEvent objects.
    This keeps the writer generic and easy to replace later.
    """

    def store_event(self, event: AdaptiveEvent) -> None:  # pragma: no cover - protocol
        ...


class InMemoryEventSink:
    """
    Default sink used in v2: just keeps events in a Python list.

    This is enough for:
      - unit tests
      - local simulations
      - early-node prototypes

    A future v3 implementation can replace this with:
      - persistent DB
      - time-series store
      - message queue, etc.
    """

    def __init__(self) -> None:
        self._events: List[AdaptiveEvent] = []

    def store_event(self, event: AdaptiveEvent) -> None:
        self._events.append(event)

    @property
    def events(self) -> List[AdaptiveEvent]:
        """Return all stored events (read-only list reference)."""
        return self._events


class AdaptiveMemoryWriter:
    """
    High-level helper that receives AdaptiveEvent payloads and
    forwards them into the configured sink.

    Sentinel AI v2 (and later layers) only need to talk to this
    class – they don't care how the data is stored underneath.
    """

    def __init__(self, sink: Optional[EventSink] = None) -> None:
        self._sink: EventSink = sink or InMemoryEventSink()

    @property
    def sink(self) -> EventSink:
        return self._sink

    def write_event(self, event: AdaptiveEvent) -> AdaptiveEvent:
        """
        Store an already-constructed AdaptiveEvent instance.
        """
        self._sink.store_event(event)
        return event

    def write_from_dict(self, payload: dict[str, Any]) -> AdaptiveEvent:
        """
        Convenience method for JSON / dict payloads.

        Example:
            writer.write_from_dict({
                "layer": "sentinel",
                "anomaly_type": "entropy_drop",
                ...
            })
        """
        event = AdaptiveEvent(**payload)
        self._sink.store_event(event)
        return event
