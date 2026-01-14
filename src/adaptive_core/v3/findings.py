# src/adaptive_core/v3/findings.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True, slots=True)
class FindingV3:
    """
    A deterministic finding produced by Adaptive Core v3 analysis.

    Findings are advisory-only and must be reproducible.
    """
    finding_id: str
    title: str
    severity: float  # 0.0–1.0 (advisory score)
    evidence: Dict[str, object]
    guardrails: List[str]  # AMG IDs referenced
