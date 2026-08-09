# L021 — Symmetry and Residue-Dependence of csi (v2)

## Statement
Assume `csi` membership is defined by admissibility overlap. Then:
1) Symmetry: `β ∈ csi(α) ⇔ α ∈ csi(β)`.
2) Residue dependence: `csi(α)` varies with the residue context `R` used to evaluate windows.

## Dependencies
- Lemmas: L020 (Membership by overlap)
- Prior lemmas: none

## Proof sketch
Symmetry follows from the commutativity of set intersection: `Aα ∩ Aβ = Aβ ∩ Aα`. Residue dependence follows from the residue-conditioning of the windows `A(R)`. ∎

## Status
simulated

## Proof Type
constructive

## Supersedes / Superseded-by
Supersedes: L011

## Evidence
- **Run ID:** 2026-05-10_run07_G3_NEIGHBORHOOD
- **Result:** PASS (Stable symmetric topology across seeds)
- **Path:** results/2026-05-10_run07_G3_NEIGHBORHOOD/
