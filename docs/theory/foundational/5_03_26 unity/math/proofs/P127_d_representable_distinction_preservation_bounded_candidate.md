# Proof P127 — D Representable-Distinction Preservation Bounded Candidate

## Goal

Provide an explicit, bounded derivation for `OBL-D-001D` under declared same-context premises.

## Uses

- `L131` - Local D Evaluation and Projection Semantics
- `P125` - D Typed Projection Transition Obligations
- `P126` - D Typed Projection Type Preservation Scope Closure
- `0030_d_kernel_internalization_bounded_rules.md`
- `0031_d_independent_adversarial_review_report.json`

## Statement

For a declared context `C`, source values `x,y`, witness `w`, trace `t`, and history `h`, assume:

```text
Typed_AE_C(x) and Typed_AE_C(y)
Defined(Pi_D,C(x)) and Defined(Pi_D,C(y))
project_w,C(w) = w_C
TypedWitness_C(w_C)
TraceCompatible_C(t,w_C)
HistoryPresent_C(h)
Relation_C(Pi_D,C(x), Pi_D,C(y), w_C)
```

Then the bounded conclusion follows by the declared predicate definition:

```text
RepDist_C(Pi_D,C(x), Pi_D,C(y), w_C,t,h)
```

and therefore `PresRep_D,C(x,y,w,t,h)` holds for this declared instance.

## Derivation

1. `P126` supplies the type-level conclusion that each defined projection has type `TYPE_PROJECTION_C`.
2. The witness projection is accepted only when its context identifier equals `C`; the independent cross-context fixture rejects otherwise.
3. The witness, trace, history, and relation premises are exactly the conjuncts of `RepDist_C` in note `0030`.
4. Conjunction introduction yields `RepDist_C` for the admitted instance.
5. The bounded preservation predicate is defined as defined projections plus the admitted `RepDist_C` predicate, so `PresRep_D,C` follows for the instance.

## Scope boundary

This is a conditional instance derivation. It does not prove that the premises hold for every source, context, witness, or relation. It does not establish injectivity, reversibility, complete information preservation, or universal preservation.

## Status

`restricted_local_argument_only`

Human review status: pending. `OBL-D-001D` remains `OPEN`.

## Falsification vectors

- A same-context, fully typed instance satisfying every listed premise fails `RepDist_C`.
- `P126` permits a projection outside `TYPE_PROJECTION_C`.
- A cross-context witness is accepted as if it were local to `C`.
- The relation, trace, or history conjunct is absent while the conclusion is still asserted.
