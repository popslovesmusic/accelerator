# Lemma L128 — Braid Projection Functor

## 1. Statement
The projection mapping $F_{\text{proj}}: \mathcal{E} \to \mathcal{B}$ from the category of relational graph transitions $\mathcal{E}$ to the category of topological braids $\mathcal{B}$ is a covariant functor preserving all identity morphisms and compositions:
\[
F_{\text{proj}}(\text{id}_G) = e, \quad F_{\text{proj}}(t_2 \circ t_1) = F_{\text{proj}}(t_2) \circ F_{\text{proj}}(t_1)
\]
for all graph updates $t_i$.

## 2. Dependencies
- **Overview:** [10_functorial_projection_to_braid_spaces.md](../10_functorial_projection_to_braid_spaces.md)

## 3. Proof Sketch
We verify functoriality of the mapping:
1.  **Identity Preservation:**
    Let $\text{id}_G$ be the identity transition on graph $G$ (no edge updates). The mapping $F_{\text{proj}}(\text{id}_G)$ yields a braid with parallel, non-crossing strands, which is the identity braid $e \in \mathcal{B}$.
2.  **Composition Preservation:**
    Let $t_1: G_1 \to G_2$ and $t_2: G_2 \to G_3$ be sequential graph updates containing edge crossings.
    *   The composite transition $t_2 \circ t_1$ concatenates the updates.
    *   The braid group representation of $F_{\text{proj}}(t_2 \circ t_1)$ is the concatenation of the generator words representing crossings in $t_1$ and $t_2$, which is equivalent to the multiplication of the braid elements: $F_{\text{proj}}(t_2) \circ F_{\text{proj}}(t_1)$.
Thus, the functor preserves compositions. $\blacksquare$

## 4. Status
`provisional`
