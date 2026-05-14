# LAW-002: Pi_A Admissibility Projection Law

## Candidate Law Statement
### Informal
Given a candidate update $y_\alpha$, $\Pi_A$ maps $y_\alpha$ into the admissible continuation window $A_\alpha$ when possible, while preserving boundary cases and failure modes when projection is undefined, multi-valued, or unstable.

### Symbolic Candidate
$$\Pi_{A_\alpha}(y_\alpha) := \{ z_\alpha \in A_\alpha : d_A(z_\alpha, y_\alpha) = \inf_{u \in A_\alpha} d_A(u, y_\alpha) \}$$

### Idempotence Candidate
$$\Pi_{A_\alpha}(\Pi_{A_\alpha}(y_\alpha)) = \Pi_{A_\alpha}(y_\alpha), \text{ when } \Pi_{A_\alpha}(y_\alpha) \text{ is defined and stable}$$

### Boundary Form
$$\partial A_\alpha := \{ z : \text{admissibility\_margin}_A(z) = 0 \}$$

### Continuation Embedding
$$x'_\alpha \in x_\alpha + \Pi_{A_\alpha}(\sum_{\beta \in CSI(\alpha)} NavT(\omega_\alpha, \omega_\beta))$$

## Context & Objectives
$\Pi_A$ is the foundational constraint operator of the framework. It defines how non-local transport influences are projected onto the local admissibility manifold. Following LAW-001, which established the functional form of $\delta$, this law defines the internal mechanics of the projection itself.

The primary objectives are:
- **Membership:** Ensure all projected results are valid members of the admissibility window $A$.
- **Idempotence:** Formalize the requirement that once a candidate is projected into $A$, subsequent projection has no effect (under stable conditions).
- **Boundary Preservation:** Explicitly recognize the singular behavior at the admissibility boundary $\partial A$.
- **Ambiguity Preservation:** Reject forced uniqueness; if multiple points in $A$ are equidistant from the candidate, the projection remains multi-valued.

## Law Conditions
1. **Admissibility window A explicit:** The target region A_alpha must be well-defined.
2. **Projection domain explicit:** The domain of candidates $y_\alpha$ must be specified.
3. **Projection image subset condition present:** $\Pi_A(y) \subseteq A$.
4. **Idempotence condition bounded:** Identity behavior is restricted to defined and stable projection events.
5. **Boundary cases preserved:** Behavior at $\partial A$ is a structural feature, not a failure. Explicitly, margin_A is zero.
6. **Multi-valued projection allowed:** Equidistant candidate sets are preserved.
7. **Undefined projection cases preserved:** Failure to find an infimum is a valid process state.
8. **No global projection closure claim:** No assumption that $\Pi_A$ is defined for all possible inputs.

## Failure Modes to Preserve
- **Projection Nonexistence:** Cases where $A$ is empty or the infimum is not reached.
- **Projection Nonuniqueness:** Multiple equidistant points in $A$.
- **Boundary Instability:** Numerical or formal oscillation at $\partial A$.
- **Window Collapse:** Singularities where $A$ vanishes.
- **Branch Overcollapse:** Incorrectly pruning multi-valued projections.
- **False Idempotence Overclaim:** Assuming idempotence holds across unstable or shifting boundaries.
- **Global Closure Leakage:** Assuming the operator is mathematically closed everywhere.
- **Physics Claim Leakage:** Treating this candidate form as an established physical law.

## Next Steps
With the projection mechanics defined, the law program will proceed to define the explicit behavior of the NavT transport operator (LAW-003).
