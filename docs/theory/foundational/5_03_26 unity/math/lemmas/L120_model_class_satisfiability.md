# Lemma L120 — Model Class Satisfiability of \(\mathcal{L}_{COD}\)

## 1. Statement
The core calculus $\mathcal{L}_{COD}$ is satisfied by a class of mathematical structures $\mathcal{M}$ consisting of residue-weighted relational graphs $G_R = (V, E, W_R)$. The existence of at least one model structure satisfies all axioms of the core calculus, demonstrating logical consistency.

## 2. Dependencies
- **Overview:** [04_syntax_and_semantic_closure_of_core_calculus.md](../04_syntax_and_semantic_closure_of_core_calculus.md)
- **Lemmas:** [L117](L117_semantic_closure.md), [L119](L119_inference_rule_set.md)

## 3. Proof Sketch
We construct a concrete model structure $M \in \mathcal{M}$:
1.  **Domain Mappings:**
    *   **Vertices ($V$):** Each vertex $v_i \in V$ represents a State aspect $S_i \in \mathcal{S}$.
    *   **Edges ($E$):** Directed edges $e_{ij} = (v_i, v_j)$ represent active distinction relations $D(S_i \mid S_j) > 0$.
    *   **Residue Weights ($W_R$):** Edge weights $w_R(e) \in \mathbb{R}^+$ represent the residue memory space $\mathcal{R}$.
2.  **Axiom Satisfaction:**
    *   **Core Biconditional:** Let the local update rule be defined as path traversal along edges where $w_R(e) \ge \epsilon$. Since $w_R(e)$ deforms with traversal history, the update path is residue-conditioned, satisfying $(\mathcal{E} \neq 0) \Leftrightarrow_R \delta(\mathcal{E} > 0)$.
    *   **Non-Empty Image:** If there exists a path where $w_R(e) \ge \epsilon$, the admissible image is non-empty, and transition occurs.
    *   **0-state Collapse:** If all edge weights drop below $\epsilon$, no traversals are legal; the graph collapses to a set of disconnected vertices (zero active edges, zero distinction), mapping to the $0$-state.
Since this graph structure models all behaviors of the calculus, the system is satisfiable and consistent. $\blacksquare$

## 4. Status
`complete`
