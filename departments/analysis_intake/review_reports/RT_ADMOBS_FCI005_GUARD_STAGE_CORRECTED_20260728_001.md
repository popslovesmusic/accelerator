# Corrected FCI-005 Binary Guard Candidate

The public candidate is now:

`BCon_FCI005Distinction_x(o_i, o_j; epsilon_x, B_x, D_rel, R) : Prop`

Source witnesses `X`, `Z`, and `Y` are hidden existential bridge witnesses. They are not public binary-constraint parameters.

The candidate requires `DistinctionThresholdBridge_x`, preserving the source condition `D(X|Z) > epsilon_x` rather than silently replacing it with `d_obs(o_i,o_j) > epsilon_x`.

`FCI005-G04B` is normalized to `DELTA_A_DEPENDENT` when realized membership is required. `OrientCarrierBridge_x` is the consistent bridge symbol.

All five bridge tests remain pending. `BCon_x` is not bound, and `H_x` remains undeclared.
