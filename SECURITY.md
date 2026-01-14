# Security Policy — Adaptive Core v3

## Scope

This repository implements **Adaptive Core v3**, the **read-only Upgrade Oracle**
of the DigiByte Quantum Shield.

Adaptive Core v3:
- observes canonicalized security signals
- aggregates deterministic evidence
- produces advisory findings and upgrade reports

It does **not**:
- execute transactions
- modify wallet or node state
- hold or manage keys
- auto-apply upgrades
- exercise any on-chain or off-chain authority

---

## Threat Model

Adaptive Core v3 is designed under the assumption that:
- all inputs may be malformed or adversarial
- upstream layers may be compromised
- downstream consumers may misinterpret output

Core defenses:
- strict canonicalization (fail-closed)
- deterministic processing only
- bounded memory and windows
- no silent defaults
- explicit reason codes for all rejections

---

## In-Scope Issues

We consider the following **in scope** for security review:

- Canonicalization bypasses
- Non-deterministic behavior
- State leakage across runs
- Counter overflow or underflow
- Incorrect rejection / acceptance of malformed input
- Violations of documented authority boundaries
- Any path that could lead to implicit execution authority

---

## Out-of-Scope Issues

The following are **out of scope** by design:

- UI / UX issues
- Performance tuning
- Denial-of-service outside defined bounds
- Upstream signal correctness
- Downstream consumer misuse
- Cryptographic primitive selection (handled by other layers)

---

## Reporting a Vulnerability

If you discover a security issue:

1. **Do not open a public issue**
2. Contact the maintainer privately via GitHub
3. Provide:
   - minimal reproduction
   - expected vs actual behavior
   - affected version / commit

All valid reports will be:
- acknowledged
- reproduced
- fixed with a regression test
- documented in commit history

---

## Fix Policy

- No security fix without a test
- No silent behavior change
- No backward-incompatible change without version bump
- Determinism is non-negotiable

---

## Governance

Adaptive Core v3 is governed by:
- documented contracts
- enforced guardrails
- test coverage thresholds
- explicit authority boundaries

If code, tests, and documentation disagree:
**tests and contracts win**.
