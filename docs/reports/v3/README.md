# Adaptive Core v3 — Upgrade Oracle

Adaptive Core v3 is the **read-only Upgrade Oracle** of the DigiByte Quantum Shield.

It consumes **strict v3-shaped observations**, aggregates deterministic evidence,
and produces **human-reviewed upgrade reports**.  
It has **no execution authority** and **cannot modify wallet, node, or network state**.

---

## Core Properties

- **Deterministic** — same inputs → same outputs
- **Fail-closed** — malformed or unknown data is rejected
- **Read-only** — advisory output only
- **Human-reviewed** — no auto-application of changes
- **Privacy-preserving** — no raw cross-node data sharing

---

## What v3 Does

- Canonicalizes observations (strict schema + reason IDs)
- Maintains bounded hot-window evidence counters
- Produces deterministic findings and drift indicators
- Builds signed, hash-stable reports (JSON + Markdown)
- Emits **advisory-only** upgrade recommendations

---

## What v3 Does NOT Do

- Execute transactions
- Hold private keys
- Modify wallet or node state
- Change consensus or networking rules
- Auto-apply upgrades or patches
- Guess or infer missing data

---

## Architecture & Diagrams

- **Architecture Diagrams**: `ADAPTIVE_CORE_V3_ARCHITECTURE_DIAGRAMS.md`
- **Authority Boundaries**: `AUTHORITY_BOUNDARIES.md`
- **Formal Contract**: `CONTRACT.md`

---

## Documentation Index

All authoritative documentation for v3 lives in this folder:

- `INDEX.md` — documentation map (start here)
- `AUTHORITY_BOUNDARIES.md`
- `CONTRACT.md`
- `GUARDRAILS.md`
- `REASON_IDS.md`
- `SECURITY.md`
- `EVIDENCE_STORE.md`
- `CONFIDENCE_MODEL.md`
- `DRIFT_RADAR.md`
- `CORRELATION.md`
- `NODE_SUMMARY.md`
- `REPORT_FORMAT.md`
- `PIPELINE_USAGE.md`

---

## Source of Truth

If documentation and implementation ever diverge:

**Code + CONTRACT.md always win.**

---

© 2025 DarekDGB
