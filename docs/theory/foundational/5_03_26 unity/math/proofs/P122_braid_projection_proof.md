# Proof P122 — Braid Projection Proof

## 1. Goal
Provide the formal verification for the functorial mapping of relational graph updates to braid generators under Lemma L128.

## 2. Uses
- [L128](../lemmas/L128_braid_projection_functor.md)

## 3. Proof
We formalize the correspondence of graph updates to braid words:
1.  **Functor construction:**
    Let $G$ be a co-participation graph. Vertex labels $V = \{v_1, ..., v_N\}$ map to strands $\{s_1, ..., s_N\}$.
    Let a graph transition morphism $t_k: G_k \to G_{k+1}$ update the adjacency relationship between $v_i$ and $v_{i+1}$. This maps to the generator $\sigma_i$ representing the crossing of strand $s_i$ over $s_{i+1}$.
2.  **Morphism identity preservation:**
    An identity transition $\text{id}_G$ updates no edges, mapping to parallel strands $\sigma_0 = e$, preserving identity.
3.  **Morphism composition preservation:**
    Composition of updates $t_2 \circ t_1$ concatenates the edge updates sequentially. Under $F_{\text{proj}}$, this translates to concatenating the braid segments along the strand parameter axis, yielding the product of the braid words: $F_{\text{proj}}(t_2) \circ F_{\text{proj}}(t_1)$.
Thus, functoriality is verified. $\blacksquare$

## 4. Status
`restricted_local_argument_only`
