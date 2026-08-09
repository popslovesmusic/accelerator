# Proof P125 - D Typed Projection Transition Obligations

## Goal

Record the bounded proof target for the typed transition:

```text
A|E ->p Pi_D(A|E) -> D(*|*)
```

under a declared context `C`.

## Uses

- `L131` - Local D Evaluation and Projection Semantics
- `L113` - Vertical Bar Operator: Admissible Participation Separator
- `OBJ-PID-010` - distinction projection operator
- `OBJ-DSTAR-010` - formal distinction projection

## Proof

The source expression is admitted only when its operands satisfy the declared affect/effect typing rule. The first arrow is licensed only by explicit invocation of `Pi_D`; no direct rewrite from `A|E` to `D(*|*)` is allowed. The second arrow is a representational binding within `TYPE_PROJECTION`. Therefore the route is well-formed as a typed transition schema if the following premises are supplied:

```text
Typed_AE(A|E)
Defined(Pi_D,C)
Codomain(Pi_D,C) = TYPE_PROJECTION
Binding(Pi_D(A|E), D(*|*))
```

The premises establish syntactic and type-level admissibility only. They do not establish semantic injectivity, complete information preservation, reversibility, or uniqueness of `Pi_D`.

## Status

scaffold_pending_discharge

## Falsification vectors

- A well-typed source maps outside `TYPE_PROJECTION`.
- A direct substitution is accepted without `Pi_D`.
- Two declared contexts produce incompatible projection bindings without a context-indexed distinction.
- A claimed preservation property fails on a declared representable distinction.
