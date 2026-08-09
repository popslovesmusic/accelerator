# Lemma L129 — Braid Confinement Stability

## 1. Statement
Topological braid closures (knots or links) under the projection functor $F_{\text{proj}}$ correspond to persistent relational basins under the admissibility filter $\delta_a$, preserving their topological knot invariants over sequence updates.

## 2. Dependencies
- **Overview:** [10_functorial_projection_to_braid_spaces.md](../10_functorial_projection_to_braid_spaces.md)
- **Lemmas:** [L128](L128_braid_projection_functor.md)

## 3. Proof Sketch
We verify the preservation of braid invariants:
1.  **Invariance under Reidemeister moves:**
    A deformation of the relational graph corresponds to Reidemeister moves on the projected braid. If the updates preserve the connectivity of the cycle, they represent topological isotopy.
2.  **Admissibility constraints:**
    The admissibility filter $\delta_a$ forbids any step that reduces crossings below the context threshold or breaks the triadic closure cycle $K$ (3-Peak Rule). This constraint prevents Reidemeister moves that would split or untie the knot (which would map to the $0$-state collapse).
Therefore, the knot invariants are conserved, guaranteeing the long-term structural stability of the confinement basin. $\blacksquare$

## 4. Status
`provisional`
