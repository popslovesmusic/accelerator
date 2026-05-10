# L020 — csi(α) Membership by Admissibility Overlap (v2)

## Statement
Assume coupling neighborhood membership is defined by mutual admissibility overlap: `β ∈ csi(α) ⇔ Aα ∩ Aβ ≠ ∅`. Then `csi(α)` is a derived object determined by window geometry and residue context.

## Dependencies
- Specification: `# Formal Specification of ⇔(_R).txt`
- Prior lemmas: none

## Proof sketch
Membership is a function of the set intersection of admissibility windows. Since windows are state/residue dependent, the topology is dynamically induced. ∎

## Status
simulated

## Proof Type
constructive

## Supersedes / Superseded-by
Supersedes: L010

## Evidence
- **Run ID:** 2026-05-10_run07_G3_NEIGHBORHOOD
- **Result:** PASS (Interaction topology sensitivity to admissibility threshold)
- **Path:** results/2026-05-10_run07_G3_NEIGHBORHOOD/
