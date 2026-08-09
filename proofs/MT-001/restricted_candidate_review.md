# MT-001: Projection Idempotence Restricted Candidate Review

## 1. Candidate Theorem
**Target**: $\Pi_A \circ \Pi_A \sim \Pi_A$.
**Statement**: In a stable local neighborhood $Neighborhood_\alpha$, the application of the admissibility projection operator $\Pi_A$ to an already projected admissible state $x' \in Im_A$ yields a state equivalent to $x'$ under `projection_equivalence`.

## 2. Formal Dependencies (FSUB)
- **Operator**: $\Pi_A: X_\alpha \times A_\alpha \to Im_A$
- **Equivalence**: `projection_equivalence`
- **Admissibility Set**: $A_\alpha$
- **State Space**: $X_\alpha$

## 3. Assumptions
- **A1**: The admissibility set $A_\alpha$ is non-empty and bounded.
- **A2**: The residue-conditioning $\mathcal{R}$ is constant over the projection interval.
- **A3**: The neighborhood $Neighborhood_\alpha$ satisfies local convergence criteria (no `recursive_divergence`).

## 4. Derived Constraints
- $\Pi_A(x, A)$ must satisfy post-projection admissibility.
- The mapping is strictly directional ($X_\alpha \to Im_A$).

## 5. Failure Modes & Counterexamples
- **Counterexample 1**: Neighborhood instability leading to `projection_non_idempotence`.
- **Counterexample 2**: Domain mismatch where output of $\Pi_A$ falls outside $X_\alpha$.

## 6. Review Result
**Status**: `CANDIDATE_SUPPORTED_UNDER_ASSUMPTIONS`

## 7. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Master Index](../../docs/math/codex_master_index.md)
