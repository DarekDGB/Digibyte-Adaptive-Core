# src/adaptive_core/v3/analyze.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .evidence_store import EvidenceSnapshot
from .findings import FindingV3


@dataclass(frozen=True, slots=True)
class AnalyzeConfig:
    """
    Deterministic analysis thresholds.
    Kept minimal in Step 3.
    """
    reason_spike_min_count: int = 5
    reason_spike_min_ratio: float = 0.10  # 10%


def generate_findings(snapshot: EvidenceSnapshot, cfg: AnalyzeConfig = AnalyzeConfig()) -> List[FindingV3]:
    """
    Generate deterministic advisory findings from evidence counters.
    """
    findings: List[FindingV3] = []

    total = snapshot.total_events
    if total <= 0:
        return findings

    # Finding: upstream reason_id spike (repeated fail-closed reasons)
    for reason_id, count in sorted(snapshot.by_upstream_reason_id.items()):
        ratio = count / total
        if count >= cfg.reason_spike_min_count and ratio >= cfg.reason_spike_min_ratio:
            findings.append(
                FindingV3(
                    finding_id=f"AC-FIND-REASON-SPIKE::{reason_id}",
                    title=f"Repeated upstream reason_id spike: {reason_id}",
                    severity=min(1.0, 0.2 + ratio),  # deterministic advisory scoring
                    evidence={
                        "reason_id": reason_id,
                        "count": count,
                        "total_events": total,
                        "ratio": round(ratio, 6),
                    },
                    guardrails=[
                        # minimal set for this finding type
                        "AMG-001",  # deny-by-default
                        "AMG-014",  # no silent fallback
                        "AMG-051",  # no fix without test
                    ],
                )
            )

    return findings
