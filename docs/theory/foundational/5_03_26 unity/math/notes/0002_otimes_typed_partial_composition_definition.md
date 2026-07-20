# OTIMES_TYPED_PARTIAL_COMPOSITION_DEFINITION_001 - Typed Partial Composition

## 1. Scope
This note extracts the governed meaning of `\otimes` already used by MT-OTIMES-001, L118, and P112. It is an additive clarification and does not modify or promote existing lemmas or proofs.

## 2. Definition
`\otimes` denotes a typed partial relational composition operator:

```text
X \otimes_Y Z
```

The expression is defined only when all of the following are declared:

- `Type(X)` and `Type(Z)`.
- Composition context `Y`.
- A distinction-preservation condition between the operands.
- A non-empty admissibility result for the composed expression.
- Closure-class compatibility under `Y`.

If any required field is missing or fails, the expression is undefined rather than false.

## 3. Projection-Window Specialization
The L118/P112 expression is a specialized admissibility-projection case:

```text
Pi_A \otimes_intersection Pi_B := Pi_(A intersection B)
```

This specialization is lawful because the declared context is admissibility-window intersection. Associativity in this subcase follows from associativity of set intersection, not from a global associativity rule for every `\otimes` expression.

## 4. Negative Constraints
`\otimes` is not:

- A standard tensor product by default.
- Logical AND.
- Scalar multiplication or scalar product.
- An untyped interference rule.
- A physical fusion operator.
- A rule that implies `X = Z`, `X = X \otimes_Y Z`, or `Z = X \otimes_Y Z`.

Commutativity is not assumed. Associativity is context-bound only.

## 5. Status
- **Status:** C1_DEFINED_PROVISIONAL.
- **Evidence class:** formal procedural definition with fixture/campaign support.
- **No theorem promotion:** This note does not raise L118, P112, or MT-OTIMES-001 beyond their existing governed statuses.

## 6. Evidence
- `docs/theory/foundational/5_03_26 unity/math/lemmas/L118_operator_algebra_closure.md`
- `docs/theory/foundational/5_03_26 unity/math/proofs/P112_operator_algebra_proof.md`
- `docs/theory/foundational/5_03_26 unity/math/proofs/P_OTIMES_001_non_identity_composition.md`
- `outputs/firewalls_campaign/otimes_results.json`
- `registry/operator_registry.json`
- `registry/math/operator_registry.json`
