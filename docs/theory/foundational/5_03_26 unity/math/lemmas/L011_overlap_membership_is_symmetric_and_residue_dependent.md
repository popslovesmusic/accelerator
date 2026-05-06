# L011 — Overlap Membership is Symmetric and Residue-Dependent (G3 consequences)

## Statement
Assume `csi` membership is defined by admissibility overlap as in Lemma `L010`:

`β ∈ csi(α)  ⇔  Aα ∩ Aβ ≠ ∅` (under a fixed residue context).

Then:

1) **Symmetry:** `β ∈ csi(α) ⇔ α ∈ csi(β)`.
2) **Residue dependence:** if windows are residue-conditioned (`Aα = A(εα, ρα, Rα)`), then `csi(α)` is residue-conditioned as well.

## Dependencies
- Lemmas: `L010`
- Assumptions:
  - overlap is evaluated under a fixed residue evaluation context
  - (for part 2) windows depend on residue/history `Rα`
- Prior lemmas: none

## Proof sketch
1) Symmetry: set intersection is symmetric, so `Aα ∩ Aβ ≠ ∅ ⇔ Aβ ∩ Aα ≠ ∅`, hence membership is symmetric by the defining equivalence. ∎

2) Residue dependence: if `Aα` varies with `Rα`, then the truth value of `Aα ∩ Aβ ≠ ∅` can vary with residue, hence membership varies with residue. ∎

## Status
draft

## Supersedes / Superseded-by

