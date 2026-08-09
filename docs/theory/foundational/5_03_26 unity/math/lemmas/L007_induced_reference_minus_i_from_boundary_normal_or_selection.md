# L007 — Induced Local Reference `-(i)α` from Oriented Window + Selection (G1 closure, conditional)

## Statement
Assume:

1) `Aα` has an oriented boundary structure as in Lemma `L006` (i.e., `Aα = {δ : gα(δ) ≥ 0}` with `∇gα ≠ 0` on `∂Aα`), and
2) there exists a mismatch objective `μ_rel(δ; εα)` and an admissible mismatch-minimizing selection `δ*α ∈ argmin_{δ∈Aα} μ_rel(δ; εα)`.

Then a local reference/orientation object `-(i)α` can be defined as a **derived** quantity from the selection outcome, for example:

- if `δ*α ≠ 0`, `-(i)α := δ*α / ||δ*α||` (direction of the selected admissible increment), or
- if selection lands on the boundary, `-(i)α := nα(δ*α) / ||nα(δ*α)||` where `nα = ∇gα` (boundary normal at the selected point).

In either case, `-(i)α` is induced by admissibility + mismatch selection and is not introduced as a primitive.

## Dependencies
- Lemmas: `L006` (oriented window scaffold)
- Concept alignment: `TN_Admissibility_Window_and_Local_R.txt` (separation of roles `Aα`, `Π_Aα`, selection `O*`, induced `-(i)α`)
- Assumptions:
  - Existence of minimizers (non-empty argmin; degeneracy allowed / set-valued `δ*α`)
  - A1 (Well-typedness)

## Proof sketch
By assumption, a minimizer `δ*α` exists inside `Aα`. The definition of `-(i)α` is then a mapping `Ref(·)` applied to the selection output (either direction of `δ*α` or the oriented boundary normal at `δ*α`). Because `Ref` depends only on the selection output, and the selection output depends only on `Aα` and mismatch data `(μ_rel, εα)`, the reference `-(i)α` is derived rather than primitive. ∎

## Status
draft

## Supersedes / Superseded-by

