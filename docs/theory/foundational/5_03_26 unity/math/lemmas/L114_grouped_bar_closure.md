# Lemma L114 — Grouped Bar Closure and Triadic Participation

## 1. Statement
Within these models:
1. **Binary Non-Reduction:** Binary closure of $A|B$ does not automatically define closure for grouped participation expressions such as $A|B|C$, $(A|B)|C$, $A|(B|C)$, or $A_1 | A_2 | \dots | A_n$. Grouped expressions denote a structured participation field and are not reducible to a simple list or unordered set.
2. **Associativity and Permutation Default:** Grouped bar expressions are non-associative ($(A|B)|C \not\equiv A|(B|C)$) and non-permutable ($A|B|C \not\equiv B|A|C$) by default. Regrouping or permutation is admissible only under an explicitly proven orientation-preserving equivalence. Order and grouping structure are first-class topological properties.
3. **Triadic Closure Special Case:** A triadic bar expression $A|B|C$ is a three-part participation field where the middle term $B$ functions as mediator, operator, comparison interface, or co-generator depending on typed role. Role declarations are mandatory for middle participants.
4. **Grouped Admissibility Gate:** A grouped bar expression is admissibly closed under $Adm_{|}^{G}(A_1, \dots, A_n; G)$ if and only if all typed participants are admissible, all adjacent/declared interfaces satisfy local bar admissibility ($Adm_{|}(A_i, A_j)$), and the whole grouping preserves orientation-consistent participation structure $Preserve\_O(G)$ and gates distinction $D_G(G) > \epsilon_a$.
5. **Orientation Dependency:** Grouped closure requires orientation compatibility, meaning final validation of grouped closure remains dependent on the formal specification of the Orientation Space $O$.

## 2. Dependencies
- Definitions: `grouped_bar_closure`
- Prior lemmas: L113 (Vertical Bar Operator: Admissible Participation Separator)

## 3. Proof Sketch
Grouped participation structures represent multi-operand interfaces. Since the interface $A|B$ carries orientation and order sensitivity, multiplying interfaces introduces complex topological graphs $G$ rather than simple binary relations. Associativity and commutativity cannot be assumed because they correspond to swapping active boundaries and orientation trajectories. Triadic structures represent the minimal non-trivial graph closure ($N \ge 3$), requiring role differentiation to prevent internal circulation collapse.

## 4. Status
provisional

## 5. Supersedes / Superseded-by
None.
