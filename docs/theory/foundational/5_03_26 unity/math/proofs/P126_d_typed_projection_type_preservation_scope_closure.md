# Proof P126 - D Typed Projection Type Preservation Scope Closure

## Goal

Record the bounded type-level closure currently available for `OBL-D-001C` under a declared context `C`.

## Uses

- `L131` - Local D Evaluation and Projection Semantics
- `L113` - Vertical Bar Operator: Admissible Participation Separator
- `P125` - D Typed Projection Transition Obligations
- `OBL-D-001A_completion_certificate.json`
- `0013_d_typed_projection_preservation_candidate.md`
- `D_TYPED_PROJECTION_PRESERVATION_FIXTURE_CHECK_20260723`
- `D_TYPED_PROJECTION_INDEPENDENT_REVIEW_20260723`

## Statement

Given a declared context `C` and a source expression `x` such that:

```text
Typed_AE(x)
Defined(Pi_D,C(x))
Codomain(Pi_D,C) = TYPE_PROJECTION_C
```

the typed transition conclusion supported by the currently declared route is:

```text
type(Pi_D,C(x)) = TYPE_PROJECTION_C
```

If the representational binding is also declared,

```text
Binding(Pi_D,C(x), D(*|*))
```

then the bound target remains in the same projection layer:

```text
type(D(*|*)) = TYPE_PROJECTION_C
```

## Derivation

1. `OBL-D-001A` makes the source participation typing and defined/undefined boundary explicit enough to prevent an implicit source-domain jump.
2. `PATCH_PI_RT_CALCULUS_020` licenses the route `A|E ->p Pi_D(A|E)` only through explicit invocation of `Pi_D` and fixes the target layer as `TYPE_PROJECTION`.
3. `0013_d_typed_projection_preservation_candidate.md` states the candidate implication from typed source plus declared codomain to typed projection result.
4. The bounded fixture set rejects the three negative cases that would otherwise smuggle in a stronger conclusion: wrong codomain, direct substitution, and untyped source.
5. The Friday, July 24, 2026 scope-corrected reading is therefore a type-level closure only.

## Scope Boundary

This proof does not establish:

- semantic representable-distinction preservation,
- injectivity,
- reversibility,
- complete information preservation,
- uniqueness of `Pi_D`,
- theorem promotion.

Those questions remain downstream of `OBL-D-001D` and `OBL-D-001E`.

## Status

`restricted_local_argument_only`

Human review status: pending.

## Falsification vectors

- A declared well-typed source maps outside `TYPE_PROJECTION`.
- A direct substitution from `A|E` to `D(*|*)` is accepted without `Pi_D`.
- An untyped source is accepted as if it were affect/effect typed.
- A semantic preservation statement is inferred from the type judgment alone.

## Supersession note

This additive proof supplements `P125` and narrows downstream use of the typed projection route to its currently supported type-level scope. It does not supersede `OBL-D-001D` or `OBL-D-001E`.
