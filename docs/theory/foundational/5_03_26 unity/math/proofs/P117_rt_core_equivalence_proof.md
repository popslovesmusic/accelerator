# Proof P117 — Relational Transition Core Equivalence Proof

## 1. Goal
Provide the formal verification for the process-equivalence between the relational transition form and the canonical core expression under Lemma L123.

## 2. Uses
- [L123](../lemmas/L123_rt_core_equivalence.md)

## 3. Proof
We establish structural equivalence by constructing a bidirectional mapping:
1.  **Forward Map ($\Phi$):**
    Map the terms of $RT$ to the core expression:
    *   $\Phi(D \neq 0) = (\mathcal{E} \neq 0)$
    *   $\Phi(\langle * \rangle_x) = \Leftrightarrow_R$
    *   $\Phi(D = 0) = \delta_a(\mathcal{E} > 0)$
    This maps the relational transition's stability conditions directly onto the core's admissibility coupling.
2.  **Inverse Map ($\Phi^{-1}$):**
    *   $\Phi^{-1}(\mathcal{E} \neq 0) = D \neq 0$
    *   $\Phi^{-1}(\Leftrightarrow_R) = \langle * \rangle_x$
    *   $\Phi^{-1}(\delta_a(\mathcal{E} > 0)) = D = 0$ (as the target state of the constraint satisfaction path).
3.  **Preservation of Invariants:**
    Under both mappings, the valuation function $v$ behaves identically for all states. Both forms collapse to the same non-distinction $0$-state when the admissibility condition fails.
Therefore, the two expressions are process-equivalent. $\blacksquare$

## 4. Status
`restricted_local_argument_only`
