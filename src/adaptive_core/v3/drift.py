# src/adaptive_core/v3/drift.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .findings import FindingV3


@dataclass(frozen=True, slots=True)
class LayerContract:
    """
    Minimal contract description for a layer.

    Only include facts that are:
    - explicit
    - deterministic
    - versioned
    """
    layer: str
    assumptions: Dict[str, str]  # key -> description


def detect_contract_drift(contracts: List[LayerContract]) -> List[FindingV3]:
    """
    Detect mismatched assumptions across layers.

    Example:
      Layer A assumes `meta.canonical=true`
      Layer B allows non-canonical meta

    Output is deterministic:
    - stable ordering
    - no heuristics
    """
    findings: List[FindingV3] = []

    # Build assumption index: key -> list[(layer, value)]
    index: Dict[str, List[Tuple[str, str]]] = {}
    for c in contracts:
        for k, v in c.assumptions.items():
            index.setdefault(k, []).append((c.layer, v))

    for key in sorted(index.keys()):
        entries = index[key]
        # Compare values across layers
        values = {v for _, v in entries}
        if len(values) > 1:
            evidence = {
                "assumption_key": key,
                "layers": sorted([l for l, _ in entries]),
                "values": sorted(values),
            }
            findings.append(
                FindingV3(
                    finding_id=f"AC-DRIFT::{key}",
                    title=f"Contract drift detected for assumption '{key}'",
                    severity=0.6,
                    evidence=evidence,
                    guardrails=[
                        "AMG-001",  # deny-by-default
                        "AMG-022",  # strict canonicalization
                        "AMG-037",  # determinism guardian
                        "AMG-055",  # proof pack required
                    ],
                )
            )

    return findings
