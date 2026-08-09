# Lemma L125 — Orientation Selection Operator

## 1. Statement
The orientation selection operator $O^*(\Omega_a)_c$ resolves to a unique local orientation reference $-(i) \in \mathcal{O}_{\text{adm}}$ if and only if the relational asymmetry ratio breaks symmetry:
\[
\Omega_a(S_1, S_2)_c \neq 1
\]
preventing circularity and avoiding the reification of pre-existing spatial dimensions.

## 2. Dependencies
- **Overview:** [07_asymmetry_to_orientation_selection_operator.md](../07_asymmetry_to_orientation_selection_operator.md)
- **Lemmas:** [L124](L124_asymmetry_ratio.md)

## 3. Proof Sketch
We verify the existence and uniqueness of the selector:
1.  **Symmetry Case ($\Omega_a = 1$):**
    If $\Omega_a = 1$, then $D(S_1 \mid S_2)_c = D(S_2 \mid S_1)_c$. The relational pressure metric $\mu_{\text{rel}}(-(i') \cdot \Omega_a)$ is invariant under all transformations of the orientation reference $-(i')$. The minimization set $\arg\min \mu_{\text{rel}}$ contains all candidate orientations, preventing unique selection.
2.  **Asymmetry Case ($\Omega_a \neq 1$):**
    If $\Omega_a \neq 1$, the gradient $\nabla \mu_{\text{rel}}$ is non-zero. Since the space of admissible local orientations $\mathcal{O}_{\text{adm}}$ is compact, the continuous function $\mu_{\text{rel}}(-(i') \cdot \Omega_a)$ must achieve a unique global minimum on $\mathcal{O}_{\text{adm}}$.
    The selection $-(i)$ is therefore uniquely determined, breaking directional symmetry without assuming background geometry. $\blacksquare$

## 4. Status
`provisional`
