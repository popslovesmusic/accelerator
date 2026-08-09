# Provisional `Excl_obs_x` Operator Specification

## Definition

`Excl_obs_x` is a partial operator that filters inadmissible observation orientations under a declared boundary interaction and relational domain:

`Excl_obs_x : BoundaryInteraction × OrientationFamily × RelationalDomain ⇀ AdmissibleOrientationFamily`

The operator does not act on, remove, negate, or destroy the symmetry whole `>S<`.

## Failure behavior

If no observation orientation remains admissible, the operator returns a diagnostic empty-family failure. It does not produce `<S>_x`, but this means only that bounded realization fails under the current interaction and domain. It does not imply symmetry absence or ontological nothingness.

## Downstream separation

`Excl_obs_x` filters orientations. A separate `DomOrient_x` operation must determine whether a dominant orientation is selected, ranked, quotient-valued, or represented by an equivalence class. `[Asym]_x` and `<S>_x` remain downstream.

## Open work

The next human review must choose the formal representation of `Omega_obs`, define `AdmObs_x`, specify exclusion residue, map the operator against existing pruning/reorientation surfaces, and keep `delta_alpha` unresolved.

This is a non-canonical C1 provisional artifact. It authorizes no registry or textbook change.
