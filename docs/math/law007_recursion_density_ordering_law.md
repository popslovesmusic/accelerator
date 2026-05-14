# LAW-007: Recursion Density and Ordering Law

## Candidate Law Statement
### Informal
Local continuation events are ordered by reconciliation structure across the orientation array. Regions of high reconciliation density exhibit tighter update ordering; regions of low reconciliation density exhibit sparser update ordering.

### Orientation Array
$$\{-(i)_\alpha\}$$

### Local Reconciliation Event
$$R_\alpha := \text{admissible update/reconciliation event at locus } \alpha$$

### Recursion Density Candidate
$$D_R(U) := \frac{\# \text{ of admissible reconciliation events in region } U}{\mu_A(U)}$$

### Ordering Relation Candidate
$$R_\alpha \prec R_\beta \iff R_\alpha \text{ is admissibility-preconditioned for } R_\beta \text{ under } \Leftrightarrow_R\text{-mediated continuation dependency}$$

### Apparent Temporality Clause
Apparent time is treated as a projection of ordered reconciliation density, not a primitive coordinate.


## Context & Objectives
This law addresses the emergence of ordering structure within the Mono-Process Framework. It defines how distributed reconciliation density across the orientation array $\{-(i)_\alpha\}$ generates sequential dependencies without relying on absolute or primitive time.

The primary objectives are:
- **Time-as-Projection:** Formally treat temporality as a derived property of reconciliation density.
- **Ordering Genesis:** Establish the ordering relation $\prec$ based on admissibility preconditioning.
- **Density-Ordering Link:** Connect the density of reconciliation events $D_R$ to the "tightness" of the ordering structure.
- **Non-Primitive Temporality:** Ensure that no absolute time or global clock is reintroduced.

## Law Conditions
1. **Orientation array dependency explicit:** Ordering is formally tied to the distributed orientation array $\{-(i)_\alpha\}$.
2. **Local reconciliation event explicit:** The reconciliation event $R_\alpha$ is defined as the unit of ordering.
3. **Recursion density candidate explicit:** $D_R(U)$ is defined as a measurable density of events.
4. **Ordering relation candidate explicit:** The partial order $\prec$ is defined through admissibility preconditioning.
5. **Absolute time not primitive:** No primitive temporal coordinate is assumed or used.
6. **Apparent temporality as projection:** Temporality is explicitly marked as an emergent projection.
7. **Local ordering not global total order:** The framework preserves local partial ordering without forcing a universal total order.
8. **No physics validation claim:** Rejects physical time dilation or cosmological claims from the math program.

## Failure Modes to Preserve
- **Absolute Time Reintroduction:** Accidental leakage of primitive time coordinates into the math.
- **Global Total Order Overclaim:** Assuming a single universal sequence of events.
- **Physics Time Dilation Claim Leakage:** Treating density-ordering as verified physical relativity.
- **Array Topology Collapse:** Losing the distributed nature of ordering by collapsing it back to local points.
- **Recursion Density Overgeneralization:** Assuming density is constant or universally smooth.
- **Causality Overclaim:** Mistaking logical/admissibility ordering for physical causality.
- **Ordering Relation Circularity:** Dependencies that lead back to their own preconditions.
- **Hidden Global Clock:** Implicit synchronization mechanisms that bypass the array topology.

## Next Steps
Following the formalization of recursion density and ordering, the law program will address how the orientation-array topology determines CSI accessibility and transport reachability (LAW-008).
