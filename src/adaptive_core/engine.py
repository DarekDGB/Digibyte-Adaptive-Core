# src/adaptive_core/engine.py

from __future__ import annotations

from typing import Dict, Iterable

from .models import (
    RiskEvent,
    FeedbackType,
    AdaptiveState,
    AdaptiveUpdateResult,
    LayerAdjustment,
)
from .memory import InMemoryAdaptiveStore


class AdaptiveEngine:
    """
    Reinforcement-style adaptive core for the DigiByte Quantum Shield.

    Very simple v0.1 logic:

      - TRUE_POSITIVE:
          * increase weight of the reporting layer
          * slightly tighten global threshold
      - FALSE_POSITIVE:
          * decrease weight of the reporting layer
          * slightly relax global threshold
      - MISSED_ATTACK:
          * increase all layer weights a bit
          * tighten global threshold more

    All changes are small and bounded, to avoid oscillations.
    """

    def __init__(
        self,
        store: InMemoryAdaptiveStore | None = None,
        initial_state: AdaptiveState | None = None,
    ) -> None:
        self.store = store or InMemoryAdaptiveStore()
        self.state = initial_state or AdaptiveState(layer_weights={})

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #

    def record_events(self, events: Iterable[RiskEvent]) -> None:
        for e in events:
            self.store.add_event(e)
            if e.layer not in self.state.layer_weights:
                # start with neutral weight
                self.state.layer_weights[e.layer] = 1.0

    def apply_learning(self, events: Iterable[RiskEvent]) -> AdaptiveUpdateResult:
        per_layer: Dict[str, LayerAdjustment] = {
            layer: LayerAdjustment() for layer in self.state.layer_weights
        }

        for event in events:
            self._apply_single_event(event, per_layer)

        # clamp values
        self._clamp_state()

        result = AdaptiveUpdateResult(
            state=self.state,
            per_layer=per_layer,
            processed_events=[e.event_id for e in events],
        )
        return result

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #

    def _apply_single_event(
        self,
        event: RiskEvent,
        per_layer: Dict[str, LayerAdjustment],
    ) -> None:
        layer = event.layer
        if layer not in self.state.layer_weights:
            self.state.layer_weights[layer] = 1.0
            per_layer[layer] = LayerAdjustment()

        adj = per_layer[layer]

        if event.feedback == FeedbackType.TRUE_POSITIVE:
            self.state.layer_weights[layer] += 0.05
            self.state.global_threshold += 0.01
            adj.weight_delta += 0.05
            adj.threshold_shift += 0.01

        elif event.feedback == FeedbackType.FALSE_POSITIVE:
            self.state.layer_weights[layer] -= 0.05
            self.state.global_threshold -= 0.01
            adj.weight_delta -= 0.05
            adj.threshold_shift -= 0.01

        elif event.feedback == FeedbackType.MISSED_ATTACK:
            # all layers need to become more sensitive
            for l in self.state.layer_weights:
                self.state.layer_weights[l] += 0.02
                per_layer.setdefault(l, LayerAdjustment()).weight_delta += 0.02
            self.state.global_threshold += 0.02

        # UNKNOWN feedback → no learning

    def _clamp_state(self) -> None:
        # keep weights within [0.1, 5.0]
        for layer, w in list(self.state.layer_weights.items()):
            self.state.layer_weights[layer] = max(0.1, min(5.0, w))

        # keep threshold within [0.1, 0.9]
        self.state.global_threshold = max(0.1, min(0.9, self.state.global_threshold))
