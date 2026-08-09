# Lemma L113 — Vertical Bar Operator: Admissible Participation Separator

## 1. Statement
Within these models:
1. **Primitive Role:** The vertical bar operator $|$ is the primitive admissible participation separator. It does not by itself assert equality, division, opposition, or object-boundary separation. It establishes the structured interface through which distinction can be evaluated.
2. **Valid and Invalid Operands:** Valid operands include primitive distinction candidates, already-admissible distinction expressions, grouped participation expressions, or typed projections. Invalid operands include untyped raw objects, unverified state labels, pure scalars without participation type, and semantic placeholders. Operand requirement: Each operand must either carry an admissibility trace or be explicitly marked as awaiting admissibility qualification.
3. **Orientation Sensitivity:** The expression $A | B$ is order-sensitive ($A | B \not\equiv B | A$) because the participation interface carries orientation. Symmetrical equivalence ($A | B \equiv B | A$) holds only under an explicitly proven admissible reversal condition. Symmetry is not assumed by default.
4. **Local Closure and Admissibility Gate:** A bar expression is locally closed when both operands are admissibly typed and the interface relation is legally evaluable under $D$. The inequality $D(A | B) > \epsilon_a$ is the minimal positive admissibility gate. Grouped bar expressions (e.g., $A|B|C$) require separate group-closure rules and are not automatically reducible to binary closure.
5. **Relationship to D:** The expression $A|B$ alone is a participation expression, not yet a realized distinction unless placed inside $D(*|*)$ or another registered distinction-evaluating context. Here $D(*|*)$ names the registered distinction-evaluating context rather than a primitive-form ancestor.

## 2. Dependencies
- Definitions: `vertical_bar_operator`
- Prior lemmas: L043 (Tertiary Node Structure), L044 (Operator Notation Topology), L107 (Abstraction Meta-Level Stack)

## 3. Proof Sketch
The vertical bar $|$ serves as a non-reified syntactic and topological separator that enables the representation of distinction interfaces. To prevent collapse into generic set division or logical operators, the operands must carry admissibility traces, and the interface is defined as order-sensitive. The evaluation of distinction is deferred to the operator $D$, meaning $A|B$ serves as the domain of participation rather than the evaluated distinction itself. Local closure is established through type checks on the operands, preventing the propagation of raw objects.

## 4. Status
provisional

## 5. Supersedes / Superseded-by
None.
