# Provisional `DevAdm_x` to `AdmObs_x` Mapping

The approved distinction is:

`DevAdm_x != AdmObs_x != delta_a`

`DevAdm_x` evaluates deviation admissibility for one candidate observation orientation. `AdmObs_x` exposes that result as the orientation predicate consumed by `Excl_obs_x`. `delta_a` remains the whole-continuation filter over `Gamma_E`, `Gamma_R`, `Gamma_T`, and `Gamma_O`.

The authorized chain is:

`B_x -> DevAdm_x -> AdmObs_x -> Excl_obs_x -> Omega_x_adm -> RefOrient -> [Asym]_x -> <S>_x`

Undefined mappings produce `UNDEFINED_INVOCATION`; they are not coerced to false and are not repaired. No canonical state is changed.
