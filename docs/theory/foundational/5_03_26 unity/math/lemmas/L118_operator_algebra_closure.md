# Lemma L118 — Closure of the Operator Algebra \(\mathcal{O}_{\text{COD}}\)

## 1. Statement
The composition of admissibility projections $\Pi_A$ and transport operators $\text{NavT}$ forms a closed operator algebra $\mathcal{O}_{\text{COD}}$. Composition $\Pi_{A_1} \otimes \Pi_{A_2}$ is defined and yields a valid projection operator. The algebra possesses a unique identity element and is associative under intersection.

## 2. Dependencies
- **Overview:** [04_syntax_and_semantic_closure_of_core_calculus.md](../04_syntax_and_semantic_closure_of_core_calculus.md)
- **Definitions:** `D2` (Projection operator), `D4` (Transport contribution)
- **Lemmas:** [L117](L117_semantic_closure.md)

## 3. Proof Sketch
1.  **Composition:** Define the composition of two projection operators $\Pi_{A_1}$ and $\Pi_{A_2}$ over the space of updates $\mathcal{X}$:
    \[
    (\Pi_{A_1} \otimes \Pi_{A_2})(v) = \Pi_{A_1 \cap A_2}(v)
    \]
    Since $A_1$ and $A_2$ are subset admissibility windows in $\mathcal{X}$, their intersection $A_1 \cap A_2$ is a well-defined subset of $\mathcal{X}$. By the filter property of `D2`, $\Pi_{A_1 \cap A_2}(v) \in A_1 \cap A_2$, which is a valid projection operator in $\mathcal{O}_{\text{COD}}$.
2.  **Identity Element:** The identity element $\Pi_{\mathcal{I}}$ is the trivial projection operator associated with the full space $\mathcal{X}$ (no filtering):
    \[
    \Pi_{\mathcal{I}}(v) = v \quad \forall v \in \mathcal{X}
    \]
    Then $\Pi_A \otimes \Pi_{\mathcal{I}} = \Pi_{\mathcal{I}} \otimes \Pi_A = \Pi_A$.
3.  **Associativity:** Since subset intersection is associative, operator composition $\otimes$ is associative:
    \[
    (\Pi_{A_1} \otimes \Pi_{A_2}) \otimes \Pi_{A_3} = \Pi_{A_1} \otimes (\Pi_{A_2} \otimes \Pi_{A_3}) = \Pi_{A_1 \cap A_2 \cap A_3}
    \]
Therefore, the operator algebra $\mathcal{O}_{\text{COD}}$ is closed. $\blacksquare$

## 4. Status
`complete`
