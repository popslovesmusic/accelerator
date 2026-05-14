# LAW-008: Array Topology and Accessibility Law

## Status
- **ID:** LAW-008
- **Level:** candidate_law_form
- **Basis:** LAW-006, LAW-007, LAW-003, LAW-004

## 1. Informal Statement
Accessibility between loci is determined by relational topology in the distributed orientation array, including admissibility compatibility, transport weight, orientation relation, and finite-flux constraints.

## 2. Formal Definitions

### 2.1 Orientation Array
The orientation array is defined as the set of distributed orientation operators:
`{-(i)_α}` where `α` indexes the loci of the process.

### 2.2 Accessibility Relation
Locus `β` is admissibly reachable from locus `α` (denoted `α ~_A β`) if and only if there exists a valid transport path in the orientation-array topology such that the contribution from `NavT(ω_α, ω_β)` is finite and consistent with the admissibility constraints defined in LAW-002 and LAW-003.

### 2.3 CSI (Coupling/Reach/Interaction Domain)
The coupling domain `CSI(α)` for a locus `α` is the set of all loci `β` that are admissibly reachable from `α` with finite transport contribution:
`CSI(α) := { β : α ~_A β and ||NavT(ω_α, ω_β)|| is finite under LAW-004 weighting }`

### 2.4 Local Ordering Neighborhood
The ordering neighborhood `N_ord(α)` is the subset of `CSI(α)` where the residue `R_β` participates in a local mutual ordering with `R_α` (denoted `R_α ⇔_R R_β`):
`N_ord(α) := { β ∈ CSI(α) : R_β participates in local ⇔_R-mediated ordering with R_α }`

### 2.5 Reachability Condition
A locus `β` is reachable from `α` (`Reach(α, β)`) if:
1. Admissibility compatibility is satisfied.
2. Transport contribution is finite (`||NavT|| < ∞`).
3. The projection into the local admissibility window `A_α` is non-collapsed.

## 3. Governance Constraints
- **No Physics Claim:** This law defines mathematical accessibility topology and does not claim to describe physical space or distance.
- **No Spacetime Metric:** This law does not assume or imply a primitive spacetime metric or absolute distance.
- **No Global Accessibility:** Reachability is local and relational; this law does not claim global causal reach or universal accessibility.
- **Relational Topology:** Neighborhoods are defined by orientation and transport, not by simple distance balls.

## 4. Failure Modes to Preserve
- Reintroducing spacetime metric assumptions.
- Overclaiming global accessibility.
- Treating CSI as a simple Euclidean distance ball.
- Unbounded reachability without finite flux limits.
- Transport without satisfying admissibility conditions.
- Collapse of array topology into a single local operator.
- Assumption of a hidden global causal order.
- Leakage of physics-level validation claims into the math program.
