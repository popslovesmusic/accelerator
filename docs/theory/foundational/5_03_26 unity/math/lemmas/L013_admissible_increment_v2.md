# L013 — Admissible Increment (v2)

## Statement
For any process index `α`, define the update increment `Δxα := x'α − xα`. If the update rule side of the core expression holds, then `Δxα ∈ Aα`.

## Dependencies
- Definitions: D1 (Admissibility window), D2 (Projection/filter), D3–D4 (well-typed sum/transport)
- Assumptions: A1 (Well-typedness)
- Prior lemmas: none

## Proof sketch
From the update rule,
`Δxα = Π_Aα( Σ_{β∈csi(α)} transport(ωα, ωβ) )`.
By D2 (filter property), `Π_Aα(v) ∈ Aα` for all admissible inputs `v` (and by A1 the argument is well-typed). Therefore `Δxα ∈ Aα`. ∎

## Status
simulated

## Supersedes / Superseded-by
Supersedes: L001

## Evidence
- **Run ID:** 2026-05-10_run03_MSI_L001_L002
- **Result:** PASS (1.0 admissibility stability)
- **Path:** results/2026-05-10_run03_MSI_L001_L002/
