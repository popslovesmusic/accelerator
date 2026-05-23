# LAW-009: Apparent Temporality Projection Law

## 1. Purpose
This document establishes **LAW-009** (Apparent Temporality Projection Law).
- **Source Relation**: $(E \neq 0) \iff_R \delta(E > 0)$
- **Non-Separability Acknowledged**: True.

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

### 2.3 Apparent Temporal\_app Projection
Apparent time (**time\_app(U)**) is a bookkeeping projection over the ordered reconciliation structure:
`time\_app(U) \approx Proj_{time}(O_U, D_R(U), \prec_U)`

## 3. Law Statements
- **No Primitive Time\_app:** `time\_app` is a projection from ordered reconciliation structure, not an independent primitive parameter.
- **Relational Derivation:** Temporality\_app is local to region `U` and depends on the density of admissible reconciliation events `R_α` across the orientation array `{-(i)_α}`.

## 4. Governance Constraints
- **No Physics Claim:** This law defines mathematical temporality\_app bookkeeping and does not claim to describe physical\_time\_app or cosmology\_app.
- **No Time\_dilation\_analog:** This law does not claim physical\_time\_dilation\_analog or relativistic effects; it describes variable update density in a formal process.
- **No Global Temporal\_app Order:** Temporal\_app ordering is defined by local partial ordering `≺`, not by a global total order or universal clock.
- **No Absolute Time\_app:** Time\_app is not a primitive background coordinate.

## 5. Failure Modes to Preserve
- Reintroducing absolute or primitive time\_app.
- Assuming a hidden global clock.
- Overclaiming global total temporal\_app order.
- Leakage of time\_dilation\_analog or cosmological\_app physics claims.
- Treating the projection `time\_app` as a primitive parameter.
- Overinterpreting recursion density as physical density or mass\_obs.
- Collapse of array-topology distinctions.
