# Component Semantics and Bounded `Pi_D,C` Preservation Test

## Status

`DEFINITION_CANDIDATE`

- Epistemic status: `CONJECTURED`
- Proof status: `OBLIGATIONS_IDENTIFIED`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Governing obligation: `OBL-D-001D`
- Relation to `0016`: additive component semantics and finite preservation test; no prior note is modified.

## Component definitions

For declared context `C`:

```text
TypedWitness_C(w) iff
  w is present
  and w.type = TYPE_RELATION_WITNESS_C
  and w.context = C
```

```text
Relation_C(p,q,w) iff
  TypedWitness_C(w)
  and w.source_value = p
  and w.target_value = q
  and w.relation_declared = true
```

```text
TraceCompatible_C(t,w) iff
  t is present
  and t.compatibility = COMPATIBLE
  and t.witness_id = w.id
```

```text
HistoryPresent_C(h) iff
  h is present
  and h.context = C
  and h.required = true
```

The bounded representability predicate is the conjunction:

```text
RepDist_C(p,q,w,t,h) iff
  Type_C(p) = TYPE_PROJECTION_C
  and Type_C(q) = TYPE_PROJECTION_C
  and TypedWitness_C(w)
  and Relation_C(p,q,w)
  and TraceCompatible_C(t,w)
  and HistoryPresent_C(h)
```

## Bounded preservation test

For a declared projection route `Pi_D,C`, the tested preservation condition is:

```text
PresRep_D,C(x,y,w,t,h) iff
  project_w(w) is defined
  and RepDist_C(Pi_D,C(x), Pi_D,C(y), project_w(w), t, h)
```

The fixture set varies projection definedness, witness projection, projected types, trace compatibility, and history independently. A passing fixture supports only the declared finite route. It does not establish preservation for all `x`, `y`, contexts, or projections.

## Failure and non-claims

An undefined projected witness, wrong projected type, incompatible trace, or omitted required history is a failed preservation case, not evidence of universal information loss. No injectivity, reversibility, complete information preservation, or external physical validity is inferred.

## Promotion boundary

The bounded checker may support a scoped preservation result, but OBL-D-001D remains open until the component semantics and projection route receive independent formal review. OBL-D-001E remains downstream and open.
