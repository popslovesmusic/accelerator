# Proof P119 — Orientation Selection Proof

## 1. Goal
Provide the formal verification for the uniqueness of the selection operator under Lemma L125.

## 2. Uses
- [L125](../lemmas/L125_orientation_selection_operator.md)

## 3. Proof
We establish that asymmetry breaks symmetry, resolving to a unique local minimum:
1.  **Relational friction potential:**
    Let $\mu_{\text{rel}}(-(i') \cdot \Omega_a)$ be a continuous, strictly convex function on the orientation manifold $\mathcal{O}_{\text{adm}}$.
2.  **Symmetry limit:**
    If $\Omega_a = 1$, then $x = z$. The function $\mu_{\text{rel}}$ simplifies to a flat potential where all orientations have equal cost:
    \[
    \nabla_{-(i')} \mu_{\text{rel}} = 0
    \]
    Thus, there is no unique minimum, and selection is undefined.
3.  **Symmetry breaking:**
    If $\Omega_a \neq 1$, then $x \neq z$. The gradient of the relational potential is non-zero:
    \[
    \nabla_{-(i')} \mu_{\text{rel}} \neq 0
    \]
    Since $\mu_{\text{rel}}$ is strictly convex on the compact space of admissible local orientations, there exists a unique global minimum:
    \[
    -(i) = \arg\min_{-(i')} \mu_{\text{rel}}(-(i') \cdot \Omega_a)
    \]
Therefore, the selection operator resolves uniquely, breaking directional symmetry without pre-defining coordinates. $\blacksquare$

## 4. Status
`restricted_local_argument_only`
