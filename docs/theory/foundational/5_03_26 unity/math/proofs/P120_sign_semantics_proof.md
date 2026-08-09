# Proof P120 — Sign Semantics Proof

## 1. Goal
Provide the formal verification for the mapping of sign states to pathway dynamics under Lemma L126.

## 2. Uses
- [L126](../lemmas/L126_sign_as_generative_pathway.md)

## 3. Proof
We formalize the correspondence of sign composition to pathway dynamics:
1.  **Pathway dynamics representation:**
    Let $P_1$ and $P_2$ be two pathway transitions with crossing changes $\Delta_1$ and $\Delta_2$.
    The composition of these transitions yields a net crossing change:
    \[
    \Delta_{1 \circ 2} = \Delta_1 + \Delta_2
    \]
2.  **Product composition (parity preservation):**
    Let an exclusion transition step $P_1$ act as a toggle on another transition $P_2$.
    *   If $P_2$ is an accumulation ($+$), excluding the accumulation ($+$) results in a net exclusion ($-$).
    *   If $P_2$ is an exclusion ($-$), excluding the exclusion ($-$) yields a net accumulation ($+$) because the exclusion constraint is ablated, allowing crossings to recover.
    This isomorphic mapping confirms that parity multiplication rules are process-congruent. $\blacksquare$

## 4. Status
`restricted_local_argument_only`
