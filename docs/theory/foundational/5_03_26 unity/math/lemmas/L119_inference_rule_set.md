# Lemma L119 — Inference Rules of \(\mathcal{L}_{COD}\)

## 1. Statement
The core calculus $\mathcal{L}_{COD}$ admits a sound natural deduction inference system with rules for admissibility filter introduction and elimination:
-   **$\delta_a$-Introduction:** If a candidate increment $v$ satisfies all constraint families in $P_{\text{adm}}$, then $v \in \delta_a(x; c)$.
-   **$\delta_a$-Elimination:** If $v \in \delta_a(x; c)$, then $v$ satisfies all constraint families in $P_{\text{adm}}$.
-   **Substitution:** Equivalent projection operators may be substituted salva veritate.

## 2. Dependencies
- **Overview:** [04_syntax_and_semantic_closure_of_core_calculus.md](../04_syntax_and_semantic_closure_of_core_calculus.md)
- **Lemmas:** [L116](L116_syntax_closure.md), [L117](L117_semantic_closure.md)

## 3. Proof Sketch
We establish the soundness of the inference rules:
1.  **$\delta_a$-Introduction & Elimination:**
    Recall the definition of the admissibility filter:
    \[
    \delta_a(x; c, R, -(i)) = \{ x' \in \mathcal{X} \mid P_{\text{adm}}(x', c, R, -(i)) = 1 \}
    \]
    The set-builder definition guarantees that $v \in \delta_a(x; c) \iff P_{\text{adm}}(v, c, R, -(i)) = 1$. The introduction and elimination rules map directly to the bi-implication of set membership. Soundness is preserved by the truth conditions of the predicate.
2.  **Substitution:**
    If $\Pi_{A_1}$ and $\Pi_{A_2}$ are equivalent projections under process equivalence $\simeq_O$, their valuations satisfy:
    \[
    v(\Pi_{A_1}(x)) = v(\Pi_{A_2}(x)) \quad \forall x \in \mathcal{X}
    \]
    Thus, substituting $\Pi_{A_1}$ for $\Pi_{A_2}$ in any WFF preserves the valuation, ensuring the soundness of substitution. $\blacksquare$

## 4. Status
`complete`
