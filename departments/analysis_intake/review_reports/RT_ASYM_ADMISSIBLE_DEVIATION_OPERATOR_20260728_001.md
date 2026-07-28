# Provisional `DevAdm_x` Definition

## Symbol

Use `DevAdm_x` / `\operatorname{DevAdm}_x` for “admissible deviation at scope x.” It is intentionally distinct from the existing `delta_a`, `delta_alpha`, and `epsilon_a` surfaces.

## Signature

`DevAdm_x : BoundaryInteraction × ObservationOrientation × RelationalDomain -> AdmissibilityResult`

The result is `ADMISSIBLE`, `INADMISSIBLE`, or `UNDEFINED`.

## Role

`DevAdm_x` evaluates whether a candidate observation orientation remains admissible after boundary conditioning. `Excl_obs_x` can retain orientations returning `ADMISSIBLE`, but `DevAdm_x` does not select a dominant orientation, create `[Asym]`, or produce `<S>` directly.

If every candidate is inadmissible, the admissible orientation family is empty. That is a local bounded-realization failure, not symmetry destruction or an ontological zero-state.

`delta_alpha`, `delta_a`, and `epsilon_a` remain unchanged.
