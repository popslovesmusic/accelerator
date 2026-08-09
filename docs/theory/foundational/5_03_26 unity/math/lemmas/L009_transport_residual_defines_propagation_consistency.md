# L009 — Transport Residual Defines Propagation Consistency (G2, conditional)

## Statement
Assume a transport residual observable `δ_T(α,β,γ)` is defined to measure failure of chain composition, e.g.:

`δ_T(α,β,γ) := dist( transport(ωα, ωγ), transport(ωα, ωβ) ∘ transport(ωβ, ωγ) )`

for a discrepancy functional `dist(·,·)` with `dist(u,u)=0`.

Then `δ_T(α,β,γ)=0` is a sufficient criterion for propagation consistency through the intermediate index `β`, i.e.:

`transport(ωα, ωγ) = transport(ωα, ωβ) ∘ transport(ωβ, ωγ)`.

This provides an operational "propagation identity" check once `transport`, `∘`, and `dist` are explicitly defined (G2 closure condition).

## Dependencies
- Lemmas: `L008` (composition + identity scaffold)
- Source alignment:
  - `paper4_deriving_local_reference_minus_i_from_admissible_mismatch_minimizing_selection.md` (uses `δ_T` as a transport residual observable)
- Assumptions:
  - `dist(u,u)=0` and equality meaningfully defined for the transport objects

## Proof sketch
By the definition of `δ_T`, if `δ_T(α,β,γ)=0` then the two arguments of `dist` coincide, yielding the stated equality. ∎

## Status
draft

## Supersedes / Superseded-by

