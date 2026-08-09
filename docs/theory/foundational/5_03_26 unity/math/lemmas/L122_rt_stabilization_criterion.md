# Lemma L122 — Relational Transition Stabilization Criterion

## 1. Statement
A precursor distinction $D(S_1 \mid S_2)_c$ stabilizes into a recursively coupled Relational Transition ($RT$) if and only if it satisfies the admissibility condition $\mathcal{A}(D)$:
\[
\mathcal{A}(D) \iff D(S_1 \mid S_2)_c \ge \epsilon_a \wedge \exists S_3 \in \mathcal{S} \text{ such that } \{S_1, S_2, S_3\} \text{ forms a stable Triad } K
\]
preventing decay to the $0$-state symmetry limit.

## 2. Dependencies
- **Overview:** [06_relational_transition_and_core_equivalence.md](../06_relational_transition_and_core_equivalence.md)
- **Theorems:** `T001` (3-Peak Rule)

## 3. Proof Sketch
We establish the necessity of the conditions:
1.  **Floor Boundary Necessity:** If $D(S_1 \mid S_2)_c < \epsilon_a$, then by definition of the context floor, the distinction is filtered out as noise, mapping to the $0$-state (collapse). Thus, $D \ge \epsilon_a$ is necessary.
2.  **Triadic Closure Necessity:**
    Assume a binary distinction exists in isolation. Under local update deformation, the aspects adjust toward distinction minimization. Without an independent reference aspect to anchor the relation, the update equation converges to $D \to 0$ (collapse).
    By introducing a third aspect $S_3$ forming a cycle $\{S_1, S_2, S_3\}$, the 3-Peak Rule ($N \ge 3$ relational crossings) prevents simultaneous collapse across all edges. This sustains non-zero distinction, stabilizing the relation as an active Relational Transition. $\blacksquare$

## 4. Status
`provisional`
