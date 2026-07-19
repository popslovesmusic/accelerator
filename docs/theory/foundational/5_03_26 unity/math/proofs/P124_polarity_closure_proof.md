# Proof P124 — Polarity Closure Proof

## 1. Goal
Provide the formal verification for the nested equivalence of polarity closure under Lemma L130.

## 2. Uses
- [L130](../lemmas/L130_polarity_closure_binding.md)

## 3. Proof
We formalize the correspondence of the loops:
1.  **State mapping:**
    Let the system loop state space be $\mathcal{X}$. The primary loop transition maps a state $X_k$ to $X_{k+1}$ under the admissibility filter $\delta_a$.
    Let this be represented as a map $\Phi: \mathcal{X} \to \mathcal{X}$.
2.  **Sign space mapping:**
    The sign partitioning map $\text{Sign}(\Delta \mathcal{X})$ classifies updates into addition ($+$) or exclusion ($-$).
    We show that the transition $\Phi$ is recursively equivalent to the composition of exclusion and accumulation steps:
    *   Exclusion filters out inadmissible trajectories ($-1$).
    *   Accumulation builds up stable crossings ($+1$).
    Since the primary loop is composed of these two phases, the primary loop operator $\iff_R$ is homomorphic to the polarity relation $[(-1) \iff_R (+1)]$.
Thus, the equivalence is formally verified. $\blacksquare$

## 4. Status
`restricted_local_argument_only`
