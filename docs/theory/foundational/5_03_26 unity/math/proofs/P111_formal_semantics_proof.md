# Proof P111 — Semantic Closure Proof

## 1. Goal
Provide the formal verification for the semantic closure and valuation of the core biconditional under Lemma L117.

## 2. Uses
- [L117](../lemmas/L117_semantic_closure.md)

## 3. Proof
We prove that the semantic valuation function $v$ maps the core relation uniquely for any residue state $R_t \in \mathcal{R}$:
1.  **State Valuation:**
    Given the core formula:
    \[
    \phi := (\mathcal{E} \neq 0) \Leftrightarrow_R \delta(\mathcal{E} > 0)
    \]
    The valuation is:
    \[
    v(\phi \mid R_t) = 1 \iff v(\mathcal{E} \neq 0) = v(\delta(\mathcal{E} > 0) \mid R_t)
    \]
2.  **Case Analysis:**
    *   **Case 1:** $v(\mathcal{E} \neq 0) = 1$. The biconditional requires $v(\delta(\mathcal{E} > 0) \mid R_t) = 1$. This implies the admissible image is non-empty, and process continuation proceeds legally.
    *   **Case 2:** $v(\mathcal{E} \neq 0) = 0$. The biconditional requires $v(\delta(\mathcal{E} > 0) \mid R_t) = 0$. This implies the admissible image is empty, mapping to the $0$-state (collapse/decoupling).
In either case, the semantic interpretation is unique and bounded, ensuring semantic closure. $\blacksquare$

## 4. Status
`complete`
