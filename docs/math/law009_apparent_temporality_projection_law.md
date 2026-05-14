# LAW-009: Apparent Temporality Projection Law

## Status
- **ID:** LAW-009
- **Level:** candidate_law_form
- **Basis:** LAW-006, LAW-007, LAW-008

## 1. Informal Statement
Temporal appearance arises when local reconciliation events are projected into an ordered count or density measure. Dense reconciliation regions produce high update-density projections; sparse regions produce low update-density projections.

## 2. Formal Definitions

### 2.1 Reconciliation Event Set
For a region `U`, the set of ordered reconciliation events `O_U` is defined as:
`O_U := { R_α : α ∈ U and R_α participates in local ⇔_R-mediated ordering }`

### 2.2 Recursion Density
The recursion density `D_R(U)` in region `U` is defined as the measure of ordered reconciliation events over the admissibility window volume:
`D_R(U) := |O_U| / μ_A(U)`, when `μ_A(U)` is defined and nonzero.

### 2.3 Apparent Temporal Projection
Apparent time `T_app(U)` is a bookkeeping projection over the ordered reconciliation structure:
`T_app(U) := Proj_time(O_U, D_R(U), ≺_U)`

## 3. Law Statements
- **No Primitive Time:** `T_app` is a projection from ordered reconciliation structure, not an independent primitive parameter.
- **Relational Derivation:** Temporality is local to region `U` and depends on the density of admissible reconciliation events `R_α` across the orientation array `{-(i)_α}`.

## 4. Governance Constraints
- **No Physics Claim:** This law defines mathematical apparent temporality bookkeeping and does not claim to describe physical time or cosmology.
- **No Time Dilation:** This law does not claim physical time dilation or relativistic effects; it describes variable update density in a formal process.
- **No Global Temporal Order:** Temporal ordering is defined by local partial ordering `≺`, not by a global total order or universal clock.
- **No Absolute Time:** Time is not a primitive background coordinate.

## 5. Failure Modes to Preserve
- Reintroducing absolute or primitive time.
- Assuming a hidden global clock.
- Overclaiming global total temporal order.
- Leakage of time dilation or cosmological physics claims.
- Treating the projection `T_app` as a primitive parameter.
- Overinterpreting recursion density as physical density or mass.
- Collapse of array-topology distinctions.
