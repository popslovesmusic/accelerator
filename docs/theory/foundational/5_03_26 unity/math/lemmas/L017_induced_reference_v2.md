# L017 — Induced Local Reference `-(i)α` (v2)

## Statement
Assume `Aα` has an oriented boundary structure (L016). If there exists a mismatch-minimizing selection `δ*α ∈ argmin_{δ∈Aα} μ_rel(δ; εα)`, then a local reference object `-(i)α` is **induced** as a derived quantity (e.g., direction of `δ*α` or boundary normal at `δ*α`).

## Dependencies
- Lemmas: L016 (Oriented window)
- Specification: `# Formal Specification of ⇔(_R).txt`
- Prior lemmas: none

## Proof sketch
`-(i)α` is defined as a mapping `Ref(δ*α)`. Since `δ*α` is determined by `Aα` and `εα`, the reference is a derived property of the process state and window geometry. ∎

## Status
simulated

## Proof Type
constructive

## Supersedes / Superseded-by
Supersedes: L007

## Evidence
- **Run ID:** 2026-05-10_run05_G1_ORIENTATION
- **Result:** PASS (Stable order parameter from selection-driven alignment)
- **Path:** results/2026-05-10_run05_G1_ORIENTATION/
