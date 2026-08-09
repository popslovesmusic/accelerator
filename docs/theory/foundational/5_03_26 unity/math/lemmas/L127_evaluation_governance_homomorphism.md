# Lemma L127 — Evaluation-Governance Homomorphism

## 1. Statement
The projection mapping $f: \mathcal{E} \to \mathcal{G}$ from the category of relational admissibility transitions $\mathcal{E}$ to the category of platform governance states $\mathcal{G}$ is a covariant functor preserving all identity morphisms and compositions:
\[
f(\text{id}_A) = \text{id}_f(A), \quad f(t_2 \circ t_1) = f(t_2) \circ f(t_1)
\]
for all relational transitions $t_i$.

## 2. Dependencies
- **Overview:** [09_evaluation_architecture_and_governance.md](../09_evaluation_architecture_and_governance.md)

## 3. Proof Sketch
We establish functoriality of the mapping:
1.  **Identity Preservation:**
    Let $\text{id}_A$ be the identity transition on relational state $A$ (no change in crossings). The mapping $f(\text{id}_A)$ yields a registry state check that preserves the existing status and hashes, which is the identity transition on the validation registry.
2.  **Composition Preservation:**
    Let $t_1: A \to B$ and $t_2: B \to C$ be two sequential admissibility transitions.
    *   The composite transition $t_2 \circ t_1$ has crossings change $\Delta_{1 \circ 2} = \Delta_1 + \Delta_2$.
    *   The mapping $f(t_2 \circ t_1)$ evaluates the net crossings change and updates the registry status.
    *   This is identical to first applying $f(t_1)$ (updating registry to state $B$) and then applying $f(t_2)$ (updating registry to state $C$), confirming $f(t_2 \circ t_1) = f(t_2) \circ f(t_1)$.
Functoriality is verified. $\blacksquare$

## 4. Status
`provisional`
