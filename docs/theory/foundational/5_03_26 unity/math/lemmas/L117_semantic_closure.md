# Lemma L117 — Semantic Closure of the Core relation

## 1. Statement
The core relation $(\mathcal{E} \neq 0) \Leftrightarrow_R \delta(\mathcal{E} > 0)$ is semantically closed. For every valuation function $v$ and residue state $R_t \in \mathcal{R}$, there is a unique semantic interpretation mapping the expression into the distinction domain $D_{\text{domain}}$. If the residue condition fails to sustain non-zero distinction, the relation evaluates to the $0$-state symmetry limit, preserving semantic consistency.

## 2. Dependencies
- **Overview:** [04_syntax_and_semantic_closure_of_core_calculus.md](../04_syntax_and_semantic_closure_of_core_calculus.md)
- **Definitions:** `D5` (Residue-gated biconditional)
- **Lemmas:** [L116](L116_syntax_closure.md)

## 3. Proof Sketch
We establish semantic closure by defining the valuation semantics of $\Leftrightarrow_R$:
1.  **Valuation Function:** Let $v$ map relations to $\{0, 1\}$. By definition:
    \[
    v((\mathcal{E} \neq 0) \Leftrightarrow_R \delta(\mathcal{E} > 0)) = 1 \iff \text{val}(\delta(\mathcal{E} > 0) \mid R_t) = \text{val}(\mathcal{E} \neq 0)
    \]
2.  **Uniqueness:** Since $R_t \in \mathcal{R}$ is historically determined at step $t$, the admissibility filter $\delta(x; c, R_t, -(i))$ yields a unique admissible image.
3.  **Failure Boundary (0-state):** If the admissible image is empty, the right side evaluates to $0$. The biconditional requires that the left side ($\mathcal{E} \neq 0$) also evaluates to $0$. This implies $\mathcal{E} = 0$, which corresponds to the $0$-state symmetry limit.
Since the $0$-state is defined as $0\text{-state} \notin D_{\text{domain}}$, any transition mapping to it represents a decoupling event, bounding the distinction domain. Thus, the core relation has closed semantics. $\blacksquare$

## 4. Status
`complete`
