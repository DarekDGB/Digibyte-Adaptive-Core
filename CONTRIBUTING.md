# Contributing to Adaptive Core (v3)

**Adaptive Core v3** is the **Upgrade Oracle** of the DigiByte Quantum Shield.

It is a **read-only, deterministic, fail-closed intelligence layer** that:
- consumes strict, canonicalized security observations
- aggregates deterministic evidence
- produces explainable findings and upgrade reports
- provides *advisory output only* (no execution authority)

Adaptive Core v3 is **not AI**, **not autonomous**, and **not self-modifying**.

It exists to help *humans* and *higher layers* make informed security decisions.

---

## ⚖️ Core Contribution Philosophy

All contributions MUST preserve these invariants:

- **Determinism** — same input → same output
- **Explainability** — every finding must be human-readable
- **Fail-closed behavior** — malformed or ambiguous input is rejected
- **No authority** — Adaptive Core never executes actions
- **Bounded logic** — no unbounded learning or autonomous evolution

If a contribution violates *any* of these, it will not be accepted.

---

## ✅ What Contributions Are Welcome

### ✔️ 1. Canonicalization & Validation
Improvements to:
- strict schema validation
- canonical ordering
- rejection of malformed inputs
- reason-code accuracy

Files typically involved:
- `adaptive_core/v3/canonicalize.py`
- `adaptive_core/v3/events.py`
- `adaptive_core/v3/reason_ids.py`

---

### ✔️ 2. Evidence Aggregation
Enhancements to:
- deterministic counters
- bounded window behavior
- eviction correctness
- snapshot integrity

Files:
- `adaptive_core/v3/evidence_store.py`

---

### ✔️ 3. Findings & Analysis
Improvements to:
- drift detection logic
- trend interpretation
- rule-based findings
- guardrail-backed reasoning

Files:
- `adaptive_core/v3/analyze.py`
- `adaptive_core/v3/findings.py`
- `adaptive_core/v3/drift.py`

---

### ✔️ 4. Guardrails & Contracts
Clarifications or extensions to:
- guardrail registry
- invariant enforcement
- contract documentation

Files:
- `adaptive_core/v3/guardrails/registry.py`
- `docs/reports/v3/GUARDRAILS.md`
- `docs/reports/v3/CONTRACT.md`

---

### ✔️ 5. Reports & Envelopes
Work on:
- deterministic report rendering
- envelope integrity
- signature metadata handling
- format stability

Files:
- `adaptive_core/v3/report_builder.py`
- `adaptive_core/v3/envelope.py`
- `docs/reports/v3/REPORT_FORMAT.md`

---

### ✔️ 6. Tests
Highly encouraged:
- negative tests
- malformed input tests
- invariant enforcement tests
- regression locks

Coverage **must not decrease**.

---

### ✔️ 7. Documentation
Clarifications to:
- authority boundaries
- pipeline usage
- reasoning models
- security philosophy

Docs live under: docs/reports/v3/

---

## ❌ What Will NOT Be Accepted

### 🚫 1. Autonomous or Self-Modifying Logic
Adaptive Core v3 must **never**:
- tune itself
- rewrite its own rules
- apply upgrades automatically

---

### 🚫 2. Black-Box or ML Models
No:
- neural networks
- probabilistic AI
- opaque scoring
- hidden heuristics

All logic must be **explicit, inspectable, and deterministic**.

---

### 🚫 3. Execution Authority
Adaptive Core must not:
- execute transactions
- change wallet state
- block or allow operations
- modify node behavior

---

### 🚫 4. Identity or Personal Data
No:
- user identifiers
- behavioral tracking tied to identity
- persistent personal data

All inputs must be **anonymous and aggregate-safe**.

---

### 🚫 5. Silent Fallbacks
No:
- auto-defaults
- silent corrections
- guessing missing fields

Invalid input → **reject with reason ID**.

---

## 🧱 Design Principles (Non-Negotiable)

1. **Read-Only Oracle**
2. **Human-Reviewed Output**
3. **Fail-Closed by Default**
4. **Deterministic Everywhere**
5. **Bounded State**
6. **Minimal Attack Surface**
7. **Contracts Over Assumptions**

---

## 🔄 Pull Request Requirements

A valid PR must include:
- clear explanation of intent
- explicit invariants preserved
- tests covering new behavior
- no reduction in determinism
- no authority expansion

The repository architect (**@DarekDGB**) validates **architecture & direction**.  
Contributors validate **implementation correctness**.

---

## 📝 License

By contributing, you agree that your contributions are licensed under the MIT License.

© 2025 **DarekDGB**
