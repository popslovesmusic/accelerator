# D/E Metamorphic Relation and Declarative Oracle Formalization Note

Status: `C1_DEFINED_PROVISIONAL` — additive formalization note; no existing lemma or proof is modified.

## Scope

This note formalizes the testing vocabulary used by Notebook 24. It does not define new D semantics, discharge OBL-D-001D/E, or promote a theorem.

## Definitions

Let `R` be a bounded typed record in the declared P127/P128 subject domain, let `S(R)` be the pair of candidate classifications produced by the frozen subject predicates, and let `T_i` be a declared record transformation.

1. A `metamorphic_relation` is a tuple `M_i = (D_i, T_i, E_i)` where `D_i` is the transformation domain, `T_i : D_i -> D_i` is a bounded transformation, and `E_i(R, S(R), S(T_i(R)))` is an expected relation between subject outputs before and after transformation.
2. A `declarative_oracle` is a separately expressed finite decision function `O(R)` that maps the declared record fields to expected categorical outcomes. It is an analysis comparator, not an authority source and not an external semantic truth function.
3. Subject/oracle agreement is the bounded predicate `A(R) := [S(R) = O(R)]`.
4. Metamorphic agreement is `M_i(R) := E_i(R, S(R), S(T_i(R)))`.
5. A finite consistency observation is `C(D, T, O) := forall R in D, A(R) and forall i, M_i(R)`, with the explicit limitation that `D`, `T`, and `O` are finite and declared.

## Assumptions exposed

- The record schema and categorical labels are fixed before execution.
- The oracle’s requirements are independently written and do not silently import the subject implementation’s control flow.
- Each transformation changes only the declared field family except where its relation explicitly permits a coupled change.
- Replay normalization is a serialization control, not a proof of semantic identity.

## Falsification conditions

The bounded candidate is reopened by any subject/oracle disagreement, transformation contradiction, order-dependent replay digest, schema/hash mismatch, or adversarial record outside the declared assumptions that invalidates an expected relation.

## Boundary

`C(D, T, O)` is not a universal invariant, proof of preservation, proof of non-collapse, injectivity, reversibility, theorem closure, or external physical claim. Independent formal review and broader counterexample search remain required.
