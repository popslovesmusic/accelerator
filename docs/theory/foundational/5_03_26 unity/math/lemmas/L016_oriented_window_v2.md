# L016 — Oriented Admissibility Window (v2)

## Statement
Assume the admissibility window `Aα` is specified by a scalar "valve" inequality of the form
`Aα := { δ : gα(δ) ≥ 0 }`
with `gα` differentiable on the boundary `∂Aα := {δ : gα(δ)=0}` and `∇gα(δ) ≠ 0` on `∂Aα`.

Then `Aα` carries an **oriented boundary structure** via the boundary normal field `nα(δ) := ∇gα(δ)`. This allows for local orientation selection at each boundary point.

## Dependencies
- Definitions: D1 (Admissibility window)
- Specification: `# Formal Specification of ⇔(_R).txt`
- Prior lemmas: none

## Proof sketch
Standard manifold construction: if the gradient is non-vanishing, the level set `gα=0` is a smooth oriented hypersurface. ∎

## Status
simulated

## Proof Type
constructive

## Supersedes / Superseded-by
Supersedes: L006

## Evidence
- **Run ID:** 2026-05-10_run05_G1_ORIENTATION
- **Result:** PASS (Residue accumulation sensitivity to window boundary)
- **Path:** results/2026-05-10_run05_G1_ORIENTATION/
