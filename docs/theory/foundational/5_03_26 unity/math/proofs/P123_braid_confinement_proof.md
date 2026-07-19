# Proof P123 — Braid Confinement Proof

## 1. Goal
Provide the formal verification for the stability of braid closures representing persistent basins under Lemma L129.

## 2. Uses
- [L129](../lemmas/L129_braid_confinement_stability.md)

## 3. Proof
We formalize the conservation of braid invariants:
1.  **Topological classification:**
    A closed braid $B$ is classified by its knot polynomials (e.g. Jones polynomial or Alexander polynomial $A(B)$).
2.  **Isotopy preservation:**
    Admissible graph updates represent Reidemeister moves that do not alter the linking configuration.
    Suppose a transition attempt $t$ would break an edge in the cycle $K$. The resulting graph has a disconnected component, mapping to a non-closed braid (an open strand).
    The Alexander polynomial of an open strand is $0$.
    Since the admissibility filter requires the retention of triadic crossings ($\delta_a = 0$ for collapsing transitions), the update is blocked, preserving the non-zero polynomial $A(B) \neq 0$.
Therefore, the knot class is conserved, stabilizing the confinement regime. $\blacksquare$

## 4. Status
`restricted_local_argument_only`
