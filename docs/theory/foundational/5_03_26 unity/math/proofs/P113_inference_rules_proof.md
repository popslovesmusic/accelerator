# Proof P113 — Inference Rules Soundness Proof

## 1. Goal
Provide the formal verification for the soundness of the natural deduction inference rules under Lemma L119.

## 2. Uses
- [L119](../lemmas/L119_inference_rule_set.md)

## 3. Proof
We prove that the rules of introduction and elimination preserve truth value under the valuation $v$:
1.  **$\delta_a$-Introduction Soundness:**
    Assume $P_{\text{adm}}(v, c, R, -(i)) = 1$.
    By definition of set-builder:
    \[
    \delta_a(x; c, R, -(i)) = \{ x' \in \mathcal{X} \mid P_{\text{adm}}(x', c, R, -(i)) = 1 \}
    \]
    Since $P_{\text{adm}}(v, c, R, -(i)) = 1$, we must have $v \in \delta_a(x; c)$, preserving truth.
2.  **$\delta_a$-Elimination Soundness:**
    Assume $v \in \delta_a(x; c)$.
    By set-builder definition, this requires $P_{\text{adm}}(v, c, R, -(i)) = 1$, preserving truth.
3.  **Substitution Soundness:**
    If $\Pi_{A_1} \simeq_O \Pi_{A_2}$, then their outputs are equal on all inputs. Replacing one with the other in any well-formed formula preserves its semantic valuation.
Thus, the inference system is sound. $\blacksquare$

## 4. Status
`complete`
