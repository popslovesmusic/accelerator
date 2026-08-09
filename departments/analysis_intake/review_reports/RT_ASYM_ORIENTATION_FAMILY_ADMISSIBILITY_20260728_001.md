# Provisional Orientation-Family and Admissibility Definition

## Representation

`Omega_obs` is represented as a typed relational family, not automatically as a metric space, geometric set, observer collection, or unique choice. Its membership relation is:

`MemberOrient(omega, Omega_obs, >S<, D_rel)`

## Admissibility

`AdmObs_x(B_x, omega, D_rel)` evaluates whether a candidate observation orientation remains admissible under the boundary interaction and relational domain.

The conditioned family is:

`Omega_x_adm = {omega in Omega_obs | AdmObs_x(B_x, omega, D_rel) = true}`

This filters orientations only. It does not filter or negate `>S<`.

## Cardinality guard

An empty family means no bounded realization under the current interaction and domain. Multiple members remain a family and require a separate selection, ranking, quotient, or equivalence rule before defining `o_x`.

`delta_alpha` remains outside this specification.

This is a non-canonical C1 provisional artifact requiring human review.
