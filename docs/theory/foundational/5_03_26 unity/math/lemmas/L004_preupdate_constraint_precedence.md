# L004 — Pre-Update Constraint Precedence (Admissibility First)

## Statement
Assume admissibility filtering is enforced **before** state update addition (i.e., the update uses `x'α = xα + Π_Aα(…)`). Then any inadmissible components of the candidate increment do not appear in the applied update increment `Δxα`.

## Dependencies
- Definitions: D2 (Projection/filter)
- Assumptions: A2 (Admissibility enforced pre-update), A1 (Well-typedness)
- Prior lemmas: none

## Proof sketch
Let `v` denote the pre-projection candidate increment (here `v := Σ_{β∈csi(α)} transport(ωα, ωβ)`).
By A2, the applied increment is `Δxα = Π_Aα(v)`. By D2, the output of `Π_Aα` lies in `Aα` (and thus excludes components that are outside `Aα`, i.e. inadmissible under the window definition). Therefore inadmissible components of `v` are not carried into `Δxα`. ∎

## Status
draft

## Supersedes / Superseded-by

