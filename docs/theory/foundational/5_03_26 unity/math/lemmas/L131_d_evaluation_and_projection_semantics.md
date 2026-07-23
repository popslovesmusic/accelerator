# Lemma L131 - Local D Evaluation and Projection Semantics

## Statement

Within a declared context `C`, `Eval_D,C(A|B)` is a partial evaluation relation over a well-typed participation expression. A positive distinction gate is represented by:

```text
Adm_|,C(A,B) := Typed_C(A) and Typed_C(B) and Eval_D,C(A|B) and D_C(A|B) > epsilon_a,C
```

The affect/effect projection is a separate typed mapping:

```text
A|E : TYPE_AFFECT_EFFECT
A|E ->p Pi_D(A|E) : TYPE_PROJECTION
Pi_D(A|E) := D(*|*)
```

`D(*|*)` is therefore a representational projection in the declared projection domain, not an independently primitive object and not an RT-complete expression by itself.

## Dependencies

- `L113` - Vertical Bar Operator: Admissible Participation Separator
- `L112` - RT Nesting, Condition Primacy, and Family Constitution
- `OBJ-AE-010` - primitive affect/effect distinction condition
- `OBJ-PID-010` - distinction projection operator
- `OBJ-DSTAR-010` - formal distinction projection
- `PATCH_PI_RT_CALCULUS_010`
- `PATCH_PI_RT_CALCULUS_020`

## Proof sketch

The typed operand conditions and the explicit context parameter prevent `D` from being interpreted as an unqualified scalar or context-free comparison. The source and target type annotations make the projection route distinct from direct substitution. Since `D(*|*)` is introduced by the binding `Pi_D(A|E) := D(*|*)`, its status is derived from the projection declaration and not primitive by stipulation of the current formal object registry. This establishes a local semantic contract, not uniqueness, injectivity, information preservation, or universal validity.

## Status

conditional

## Open obligations

1. Give `Eval_D,C` an explicit domain and codomain.
2. Define `epsilon_a,C` and its dependence on `C`.
3. Prove type preservation across `A|E ->p Pi_D(A|E)`.
4. Define and test representable-distinction preservation.
5. State a non-collapse condition and produce a counterexample when it fails.

## Supersedes / Superseded-by

None.
