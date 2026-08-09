# L006 — Oriented Admissibility Window from Valve Inequality (G1 scaffold)

## Statement
Assume the admissibility window `Aα` is specified by a scalar "valve" inequality of the form

`Aα := { δ : gα(δ) ≥ 0 }`

with `gα` differentiable on the boundary `∂Aα := {δ : gα(δ)=0}` and `∇gα(δ) ≠ 0` on `∂Aα`.

Then `Aα` carries an **oriented boundary structure** via the boundary normal field `nα(δ) := ∇gα(δ)` (or its unit normalization). In particular, the window is not merely a set; it has a canonical local orientation notion at each boundary point.

## Dependencies
- Definitions: D1 (Admissibility window), plus a concrete valve/inequality definition of `Aα` as used in:
  - `TN_Admissibility_Window_and_Local_R.txt` (window defined by local admissibility constraints)
  - `TN_MLaw_Derivation_v01.extracted.txt` (candidate inequality form; "Gap 1 — Aα Orientation")
- Assumptions:
  - A1 (Well-typedness)
  - Aα is representable as `{δ : gα(δ) ≥ 0}` with the regularity stated above
- Prior lemmas: none

## Proof sketch
This is a standard regular-boundary construction: if `gα` is differentiable and its gradient is nonzero on the boundary, then `∂Aα` is locally a codimension-1 surface and `∇gα(δ)` provides a non-vanishing normal direction, hence an orientation choice (up to sign convention). ∎

## Status
draft

## Supersedes / Superseded-by

