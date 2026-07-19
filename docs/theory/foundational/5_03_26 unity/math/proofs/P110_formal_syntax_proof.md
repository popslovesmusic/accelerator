# Proof P110 — Syntactic Closure Proof

## 1. Goal
Provide the formal verification for the syntactic closure and term legality of the language $\mathcal{L}_{COD}$ under Lemma L116.

## 2. Uses
- [L116](../lemmas/L116_syntax_closure.md)

## 3. Proof
We formalize the induction steps outlined in Lemma L116:
1.  **Syntactic Mapping function $\mathcal{T}_{\text{type}}$:** Let $\mathcal{T}_{\text{type}}$ map any term or formula to its formal type class.
2.  **Base Cases:**
    *   $\mathcal{T}_{\text{type}}(S_i) = \text{State}$
    *   $\mathcal{T}_{\text{type}}(R_j) = \text{Residue}$
    *   $\mathcal{T}_{\text{type}}(c_k) = \text{Context}$
3.  **Well-formedness Inductive Proof:**
    Let $T_1$ and $T_2$ be terms.
    *   If $\mathcal{T}_{\text{type}}(T_1) = \text{State}$ and $\mathcal{T}_{\text{type}}(T_2) = \text{State}$, the function $D(T_1 \mid T_2)_c$ maps to type $\text{Relation}$ since the domain of $D$ is $\mathcal{S} \times \mathcal{S} \times \mathcal{C}$ and its codomain is $\mathcal{V}$ (Relational Value).
    *   Since all operations evaluate to disjoint target types, no cross-type leakage is possible.
Therefore, the syntax is closed. $\blacksquare$

## 4. Status
`complete`
