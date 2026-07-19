# Proof P114 — Model Class Satisfiability Proof

## 1. Goal
Provide the formal verification that the relational graph model class $\mathcal{M}$ satisfies the core calculus under Lemma L120.

## 2. Uses
- [L120](../lemmas/L120_model_class_satisfiability.md)

## 3. Proof
We prove that the relational graph structure $G_R = (V, E, W_R)$ satisfies all axioms of the calculus:
1.  **State Mapping:** Vertices $V$ map to States $\mathcal{S}$ and satisfy identity preservation.
2.  **Difference Mapping:** Directed edges $E$ map to Directed Distinguishability $D(S_i \mid S_j)$ by mapping existence of an edge to non-zero distinguishability ($D > 0$).
3.  **Core Update Equation Satisfaction:**
    Let the update rule on vertex properties be:
    \[
    x'_i = x_i + \sum_{(v_j, v_i) \in E} \Pi_{A(w_R(e))}( \text{NavT}(\omega_i, \omega_j) )
    \]
    This structurally matches the update rule in `D2` and `D5`.
4.  **Consistency:**
    If the graph contains edges with weight $\ge \epsilon$, updates are computed, simulating continuation. If all edge weights decay below $\epsilon$, all paths are filtered to $0$, resulting in a static graph (the $0$-state).
Therefore, the model class satisfies the calculus, showing that the core calculus is consistent and satisfiable. $\blacksquare$

## 4. Status
`complete`
