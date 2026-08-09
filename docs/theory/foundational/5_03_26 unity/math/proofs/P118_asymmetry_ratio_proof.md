# Proof P118 — Bounded Asymmetry Ratio Proof

## 1. Goal
Provide the formal verification for the bounds of the asymmetry ratio under Lemma L124.

## 2. Uses
- [L124](../lemmas/L124_asymmetry_ratio.md)

## 3. Proof
We prove that the asymmetry ratio cannot blow up to infinity or collapse to zero:
1.  **Lower limit bound:** Let $x = D(S_1 \mid S_2)_c$ and $z = D(S_2 \mid S_1)_c$. By the distinguishability floor constraint:
    \[
    x \ge \epsilon_a, \quad z \ge \epsilon_a
    \]
    The maximum capacity of the context limits the maximum distinction value:
    \[
    x \le D_{\max}, \quad z \le D_{\max}
    \]
2.  **Ratio bounds:** Since both $x$ and $z$ are positive values:
    \[
    \Omega_a = \frac{x}{z} \ge \frac{\epsilon_a}{D_{\max}}
    \]
    Similarly, the upper bound is:
    \[
    \Omega_a = \frac{x}{z} \le \frac{D_{\max}}{\epsilon_a}
    \]
    Since $D_{\max} < \infty$ and $\epsilon_a > 0$, the ratio $\Omega_a$ is strictly bounded within a closed, positive interval. $\blacksquare$

## 4. Status
`restricted_local_argument_only`
