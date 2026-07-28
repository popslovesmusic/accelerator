# Provisional Undefined-Orientation Policy

The approved policy is explicit partial classification:

`Excl_obs_x_partial(Omega_obs) = (Omega_x_pos, Omega_x_neg, Omega_x_undef)`

`UNDEFINED` is neither `TRUE` nor `FALSE`. It remains explicit provenance and prevents a claim of total-family closure.

Total orientation exclusion requires:

`Omega_x_pos = empty` and `Omega_x_undef = empty`

If `Omega_x_pos` is empty while `Omega_x_undef` is nonempty, the result is `INDETERMINATE_ADMISSIBILITY`, not total exclusion. By default, `RefOrient` requires total classification; a partial path requires an explicit `PARTIAL_SUFFICIENCY_WITNESS`.

No undefined result is coerced into `delta_a = FALSE`, and no canonical state is changed.
