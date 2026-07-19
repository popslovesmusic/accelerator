# Lemma L130 — Polarity Closure Binding

## 1. Statement
The nested relational mapping:
\[
(\mathcal{E} \neq 0) \iff_R \delta_a(\mathcal{E} > 0) \iff_R [(-1) \iff_R (+1)]
\]
is a well-formed, non-separable equivalence relation on the aspectual state space, binding the realization of constraint systems to the generative tension of directed pathways.

## 2. Dependencies
- **Overview:** [11_nested_relation_semantics_and_polarity_closure.md](../11_nested_relation_semantics_and_polarity_closure.md)

## 3. Proof Sketch
We verify the consistency of the mapping:
1.  **Isomorphic state-space mapping:**
    The left-hand side $(\mathcal{E} \neq 0) \iff_R \delta_a(\mathcal{E} > 0)$ partitions transitions into $\{ \text{admissible}, \text{inadmissible} \}$.
    The right-hand side $[-1] \iff_R [+1]$ partitions transitions into directed pathways: exclusion ($-1$) and accumulation ($+1$).
    Under L126, sign values correspond to pathway accumulation/filtration. The boundary where admissibility changes ($\delta_a$) corresponds precisely to the exclusion/addition threshold.
2.  **Transitivity & Closure:**
    The feedback cycle is driven by the interaction: exclusion of non-admissible candidate steps stabilizes the accumulation of invariants. This circular dependence guarantees that the loop cannot be separated into independent variables.
Therefore, the nested equivalence is validated. $\blacksquare$

## 4. Status
`provisional`
