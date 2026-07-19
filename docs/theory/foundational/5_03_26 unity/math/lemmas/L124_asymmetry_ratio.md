# Lemma L124 — Bounded Asymmetry Ratio

## 1. Statement
Under the context floor constraint $D \ge \epsilon_a > 0$ for all admissible distinctions, the asymmetry ratio $\Omega_a(S_1, S_2)_c = \frac{D(S_1 \mid S_2)_c}{D(S_2 \mid S_1)_c}$ is bounded within the range:
\[
\Omega_a \in [\epsilon_a D_{\max}^{-1}, \epsilon_a^{-1} D_{\max}]
\]
where $D_{\max}$ is the finite maximum distinction bounded by the context capacity.

## 2. Dependencies
- **Overview:** [07_asymmetry_to_orientation_selection_operator.md](../07_asymmetry_to_orientation_selection_operator.md)

## 3. Proof Sketch
We verify the bounds by substitution:
1.  **Lower Bound:** Let $D(S_1 \mid S_2)_c$ be minimized ($D(S_1 \mid S_2)_c = \epsilon_a$) and $D(S_2 \mid S_1)_c$ be maximized ($D(S_2 \mid S_1)_c = D_{\max}$). The ratio evaluates to:
    \[
    \Omega_{a,\min} = \frac{\epsilon_a}{D_{\max}} > 0
    \]
2.  **Upper Bound:** Let $D(S_1 \mid S_2)_c$ be maximized ($D(S_1 \mid S_2)_c = D_{\max}$) and $D(S_2 \mid S_1)_c$ be minimized ($D(S_2 \mid S_1)_c = \epsilon_a$). The ratio evaluates to:
    \[
    \Omega_{a,\max} = \frac{D_{\max}}{\epsilon_a} < \infty
    \]
Since both $D_{\max} < \infty$ and $\epsilon_a > 0$, the ratio $\Omega_a$ is strictly bounded and cannot diverge. $\blacksquare$

## 4. Status
`provisional`
