# L002 — Empty-Neighborhood Fixed Point

## Statement
Assume `csi(α) = ∅`. If the update rule side of the core expression is evaluated/active for `α`, then `x'α = xα`.

## Dependencies
- Definitions: D2 (Projection/filter), D3 (Coupling neighborhood), D4 (Transport additive under `Σ`)
- Assumptions: A1 (Well-typedness)
- Prior lemmas: none

## Proof sketch
If `csi(α) = ∅`, then the sum is the additive identity:
`Σ_{β∈∅} transport(ωα, ωβ) = 0`.
By D2, `Π_Aα(0) = 0`. Substituting into the update rule gives:
`x'α = xα + 0 = xα`. ∎

## Status
draft

## Supersedes / Superseded-by

