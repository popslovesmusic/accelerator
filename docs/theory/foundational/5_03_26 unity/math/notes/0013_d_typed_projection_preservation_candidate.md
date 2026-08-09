# Candidate Derivation: Typed `Pi_D,C` Projection Preservation

## Status

`THEOREM_CANDIDATE`  
Epistemic status: `FORMALLY_DERIVED` within the declared type rules  
Proof status: `COMPLETE_ARGUMENT_UNVERIFIED`  
Obligation: `OBL-D-001C`

## Candidate Statement

Given a declared context `C`, a well-typed affect/effect expression `x : TYPE_AFFECT_EFFECT`, and an explicitly invoked projection operator with declared codomain:

```text
Typed_AE(x)
Defined(Pi_D,C(x))
Codomain(Pi_D,C) = TYPE_PROJECTION_C
```

then:

```text
type(Pi_D,C(x)) = TYPE_PROJECTION_C
```

and the representational binding may be written:

```text
Pi_D,C(A|E) := D(*|*)
```

where `type(D(*|*)) = TYPE_PROJECTION_C`.

## Derivation

1. `OBL-D-001A` supplies the typed source participation and explicit defined/undefined boundary.
2. `PATCH_PI_RT_CALCULUS_020` requires explicit invocation of `Pi_D` for the domain transition.
3. The same rule declares the target of `Pi_D` and `D(*|*)` as `TYPE_PROJECTION`.
4. Therefore the conclusion is a type-preservation consequence of the declared operator signature and transition rule.
5. The derivation says nothing about injectivity, reversibility, semantic information preservation, or representable-distinction preservation.

## Negative Boundary

The candidate rejects direct substitution:

```text
A|E !:= D(*|*)
```

and rejects any projection whose declared codomain is not `TYPE_PROJECTION_C`.

## Acceptance Boundary

The candidate requires positive and negative typed fixtures, an independent review of the premise-to-conclusion steps, and confirmation that no semantic preservation property has been smuggled into the type judgment. `OBL-D-001C` remains open until those checks and human review pass.

