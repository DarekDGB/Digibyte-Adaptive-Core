# src/adaptive_core/v3/graph.py

from __future__ import annotations

from typing import Iterable, List

from .findings import FindingV3


def render_drift_dot(findings: Iterable[FindingV3]) -> str:
    """
    Render a deterministic DOT graph representing drift cascades.

    This is advisory-only, text-based, and reproducible.
    """
    lines: List[str] = []
    lines.append("digraph DriftRadar {")
    lines.append("  rankdir=LR;")
    lines.append("  node [shape=box];")

    for f in findings:
        if not f.finding_id.startswith("AC-DRIFT::"):
            continue
        ev = f.evidence
        key = ev.get("assumption_key")
        layers = ev.get("layers", [])
        for layer in layers:
            lines.append(f'  "{layer}" -> "{key}";')

    lines.append("}")
    return "\n".join(lines)
