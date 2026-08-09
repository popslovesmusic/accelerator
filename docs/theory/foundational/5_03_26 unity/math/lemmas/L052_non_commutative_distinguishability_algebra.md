# L052 — Non-Commutative Distinguishability Algebra

## Statement
Within this framework, directional distinguishability $d_{ij} = D(S_i \mid S_j)$ constitutes a non-commutative algebraic structure. The composition of distinguishability measures along a process path, defined as the **Distinguishability Product** ($D(A|B) \cdot D(B|C)$), is path-dependent. This structure resembles a **groupoid**, where orientation-conditioned composition rules determine the algebraic closure of a process sequence.

## Dependencies
- Definitions: `directional_distinguishability`, `distinguishability_product`
- Lemma L042 (Directional Distinguishability Asymmetry)
- Lemma L044 (Operator Notation Topology)

## Proof Sketch (Model-Relative)
1. Let $d_{12}$ and $d_{23}$ be directional distinguishability measures between nodes $(1,2)$ and $(2,3)$ respectively.
2. Per L042, $d_{ij} \neq d_{ji}$, establishing the primitive asymmetry of the components.
3. The composition of these measures $d_{12} \cdot d_{23}$ requires the parallel transport of the orientation reference $-(i)$ from the first transition to the second.
4. Because the process is residue-conditioned, the residue written during $1 \to 2$ deforms the admissibility window for $2 \to 3$.
5. Swapping the sequence ($3 \to 2 \to 1$) encounters a different sequence of window deformations.
6. Therefore, the resulting distinguishability product is non-commutative: $d_{12} \cdot d_{23} \neq d_{32} \cdot d_{21}$.
7. This non-commutativity provides the algebraic basis for the "Flavor" or "Particle Type" (L041) defined as the continuation ordering.

## Non-Proof and Limits
This does not establish a universal physical law. It is an internal formalization of how the framework models path-dependent process transitions. The comparison to groupoid theory is analogical and used to ensure the internal consistency of the algebraic trace.

## Status
draft

## Supersedes / Superseded-by
None.
