# Candidate Contract: `Eval_D,C` Domain and Codomain

## Status

`CANDIDATE_FORMAL_SPECIFICATION`  
Epistemic status: `CONJECTURED`  
Proof status: `OBLIGATIONS_IDENTIFIED`  
Obligation: `OBL-D-001A`

This is an additive candidate contract. It does not promote `Eval_D,C`, `Pi_D,C`, or `D(*|*)`, and it does not establish uniqueness, injectivity, reversibility, complete information preservation, or external validity.

## Declared Types

For a declared context `C`, define the following local types:

```text
Context_C := a declared context containing operand typing,
             admissibility, and projection-domain bindings.

Participation_C := { A|B : Typed_C(A) and Typed_C(B) }.

DistinctionValue_C := a context-local evaluated distinction value.

Residue_D,C := a typed remainder produced together with a defined evaluation.

DefinedResult_D,C := DistinctionValue_C x Residue_D,C.

UndefinedReason_D,C := {
  UNDEFINED_INCOMPLETE_CONTEXT,
  UNDEFINED_INADMISSIBLE,
  UNDEFINED_PROJECTION_FAILURE
}.

EvalResult_D,C := Defined(DefinedResult_D,C)
                  | Undefined(UndefinedReason_D,C).
```

An untyped expression is outside `Participation_C`; it is rejected before evaluation and must not be silently coerced into the domain.

## Candidate Evaluation Contract

The operationally explicit form is a partial relation with a total diagnostic wrapper:

```text
Eval_D,C : Participation_C ⇀ DefinedResult_D,C

Eval_D,C^? : Expr x Context_C -> EvalResult_D,C
```

For `x in Participation_C`, `Eval_D,C^?(x,C)` returns `Defined(v,r)` only when the context is complete, the expression is admissible under the context-local gate, and the projection result is defined. Otherwise it returns exactly one declared `Undefined(reason)` value. The wrapper does not imply that the partial relation is single-valued unless a later obligation supplies that property.

The admissibility gate remains context-indexed and intentionally unresolved until `OBL-D-001B` is discharged:

```text
admissible_D,C(x) := D_C(x) > epsilon_a,C
```

## Undefined-Result Boundary

- `UNDEFINED_INCOMPLETE_CONTEXT`: `C` lacks a required typing, admissibility, or projection binding.
- `UNDEFINED_INADMISSIBLE`: the source is well-typed but fails the declared context-local admissibility gate.
- `UNDEFINED_PROJECTION_FAILURE`: the source is admissible, but no result in the declared target projection domain is produced.

These cases are distinct from a defined result whose residue is non-empty. A non-empty residue is not, by itself, collapse or undefinedness.

## Projection Compatibility

The candidate projection remains separately typed:

```text
Pi_D,C : TYPE_AFFECT_EFFECT x Context_C ⇀ TYPE_PROJECTION_C x Residue_D,C
type(D(*|*)) = TYPE_PROJECTION_C
```

No direct substitution from `A|E` to `D(*|*)` is admitted. The projection route remains:

```text
A|E ->p Pi_D,C(A|E) -> D(*|*)
```

## Acceptance Tests

The candidate is ready for review only when the fixture set demonstrates that:

1. valid typed inputs produce `Defined` results;
2. incomplete contexts produce `UNDEFINED_INCOMPLETE_CONTEXT`;
3. typed but inadmissible inputs produce `UNDEFINED_INADMISSIBLE`;
4. projection failure produces `UNDEFINED_PROJECTION_FAILURE`;
5. untyped inputs are rejected before domain admission;
6. no fixture requires injectivity, reversibility, or complete information preservation.

Until these tests and human review pass, `OBL-D-001A` remains `OPEN` and the D package remains `C1_DEFINED_PROVISIONAL`.

