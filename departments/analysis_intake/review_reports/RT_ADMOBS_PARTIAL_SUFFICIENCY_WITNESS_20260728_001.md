# Revised Provisional Partial Sufficiency Witness

The revised witness is:

`PartialSufficiencyWitness_x(P_x, B_x, D_rel, R, RefRule_x, o_x) : Prop`

The partial partition is explicit:

`PartialPartition_x := (Omega_obs, Omega_x_pos, Omega_x_neg, Omega_x_undef, provenance)`

`PermittedResolution_x` supplies total completions that preserve all established positive and negative classifications, assign only `TRUE` or `FALSE` to unresolved orientations, satisfy `PointwiseResolutionCompatible_x`, and satisfy `GlobalJointCoherence_x` across the completed family. `RefDetermines_x` explicitly retains `B_x`, `D_rel`, and `R` at each use site.

`PointwiseResolutionCompatible_x` protects established classifications and checks local boundary, domain, and residue compatibility. `GlobalJointCoherence_x` delegates family-level consistency to `JointlyCompatible_x`, preventing individually permitted assignments from forming a jointly impossible orientation family.

`JointlyCompatible_x` is deliberately family-level. Pairwise compatibility may be required as a subcondition, but pairwise checks alone are not assumed sufficient for higher-order joint consistency.

The witness requires a positive orientation, retained provenance, a nonempty permitted-resolution space, and reference-determining invariance. Preservation of the positive admissibility result is structural because permitted completions cannot revise `Omega_x_pos`.

A provisional reference orientation may enter `delta_a` evaluation only with the tag `PARTIAL_REFERENCE_CONDITIONAL`. It cannot produce realized positive admission by itself. Closure may occur through either a totality bridge or a separate `ResolutionInvariantAdmission_x` proving `Gamma_E`, `Gamma_R`, `Gamma_T`, and `Gamma_O` across every permitted resolution.

The admissible family structure and any higher-order constraints for `JointlyCompatible_x` remain open. This is provisionally active but non-canonical at the C1 model-relative ceiling. Canonical registries, textbook content, `delta_a`, and D-semantics obligations are unchanged.
