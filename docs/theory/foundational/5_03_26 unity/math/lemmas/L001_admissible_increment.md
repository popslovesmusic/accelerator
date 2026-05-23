# L001 — Admissible Increment

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
draft

## Supersedes / Superseded-by

## Metadata (Migrated from LAW-001)
- **Law Conditions:**
  - delta_defined_only_for_non_null_participation
  - epsilon_null_threshold_explicit
  - admissibility_window_projection_explicit
  - NavT_transport_input_explicit
  - CSI_domain_explicit
  - multi_valued_continuation_preserved
  - selection_not_forced_unique
  - noninvertibility_preserved
- **Failure Modes:**
  - deterministic_delta_collapse
  - unique_continuation_overclaim
  - global_operator_closure_overclaim
  - implicit_invertibility
  - epsilon_null_boundary_ambiguity
  - empty_continuation_image
  - unbounded_CSI_sum
  - physics_claim_leakage

