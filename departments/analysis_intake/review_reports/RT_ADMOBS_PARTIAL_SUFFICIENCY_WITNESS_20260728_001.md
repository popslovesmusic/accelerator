# Revised Provisional Partial Sufficiency Witness

The revised witness is:

`PartialSufficiencyWitness_x(P_x, H_x, B_x, D_rel, R, RefRule_x, o_x) : Prop`

The partial partition is explicit:

`PartialPartition_x := (Omega_obs, Omega_x_pos, Omega_x_neg, Omega_x_undef, provenance)`

`PermittedResolution_x` supplies total completions that preserve all established positive and negative classifications, assign only `TRUE` or `FALSE` to unresolved orientations, satisfy `PointwiseResolutionCompatible_x`, and satisfy `GlobalJointCoherence_x` across the completed family. `RefDetermines_x` explicitly retains `B_x`, `D_rel`, and `R` at each use site.

`PointwiseResolutionCompatible_x` protects established classifications and checks local boundary, domain, and residue compatibility. `GlobalJointCoherence_x` delegates family-level consistency to `JointlyCompatible_x`, preventing individually permitted assignments from forming a jointly impossible orientation family.

`OrientationFamily_x` and `AdmissibleOrientationFamily_x` now distinguish the family structure from individual orientations. `JointlyCompatible_x` is deliberately family-level. `JointConstraint_x` is provisionally defined as:

`PairwiseCompatible_x AND HigherOrderCompatible_x`

Pairwise checks alone are not assumed sufficient for higher-order joint consistency. The empty-family case is guarded against vacuous acceptance.

`CompletedOrientationFamily_x` represents the total assignment produced by a resolution, while `H_x` is the provisional `FamilyConstraintSet_x` governing higher-order constraints. `O_adm` and `W_adm` may supply typed source data when contexts align, but neither is rebound as a completed family, resolution, or constraint set. `C_orient` may rank permitted resolutions but cannot decide compatibility without a separate bridge theorem.

The witness requires a positive orientation, retained provenance, a nonempty permitted-resolution space, and reference-determining invariance. Preservation of the positive admissibility result is structural because permitted completions cannot revise `Omega_x_pos`.

A provisional reference orientation may enter `delta_a` evaluation only with the tag `PARTIAL_REFERENCE_CONDITIONAL`. It cannot produce realized positive admission by itself. Closure may occur through either a totality bridge or a separate `ResolutionInvariantAdmission_x` proving `Gamma_E`, `Gamma_R`, `Gamma_T`, and `Gamma_O` across every permitted resolution.

The domain conditions for `HigherOrderCompatible_x` and any theorem that pairwise compatibility suffices remain open. This is provisionally active but non-canonical at the C1 model-relative ceiling. Canonical registries, textbook content, `delta_a`, and D-semantics obligations are unchanged.

## Bounded compatibility test

For `F = {o_1, o_2, o_3}` with all three orientations assigned `TRUE`, suppose every pair is compatible but the declared family constraint permits at most two simultaneously true orientations. Then `PairwiseCompatible_x = TRUE`, `HigherOrderCompatible_x = FALSE`, and therefore `JointConstraint_x = FALSE`.

This is a definitional test schema, not empirical evidence. It shows why pairwise compatibility cannot be promoted to sufficiency without a separate domain result.

## Repository reconciliation

Read-only inspection found related structures:

- `O_adm`: an existing admissible orientation family;
- `W_adm`: an admissible orientation window over context;
- `C_orient`: a candidate coherence metric over admissible orientation assignments.

None is directly typed as `JointlyCompatible_x`. `C_orient` may be supporting evidence or a future measure, but it is not itself a compatibility predicate. No automatic binding was made, so higher-order compatibility remains open.
