# D-Obligations Bounded Formalization Consolidation

## Status

`FORMALIZATION_CANDIDATE`

- Obligations: `OBL-D-001D`, `OBL-D-001E`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Source relation: `L131` and the additive notes `0016`–`0028`
- Promotion status: blocked; this note does not discharge either obligation.

## Typed domain

Let `C` be a declared context, `x,y` typed admissible source values, and `w` a source relation witness. `Pi_D,C` is defined only when its declared route and codomain are available. The projected values are written `p = Pi_D,C(x)` and `q = Pi_D,C(y)`.

## Representable distinction preservation (`OBL-D-001D`)

Define the bounded predicate:

```text
RepDist_C(p,q,w_C,t,h) iff
  Type_C(p) = TYPE_PROJECTION_C
  and Type_C(q) = TYPE_PROJECTION_C
  and TypedWitness_C(w_C)
  and Relation_C(p,q,w_C)
  and TraceCompatible_C(t,w_C)
  and HistoryPresent_C(h)
```

The bounded preservation condition is:

```text
PresRep_D,C(x,y,w,t,h) iff
  Defined(Pi_D,C(x))
  and Defined(Pi_D,C(y))
  and project_w,C(w) = w_C
  and RepDist_C(Pi_D,C(x), Pi_D,C(y), w_C, t, h)
```

The context identifier is part of the witness and history payload. A witness, trace, or history record from another context is rejected rather than silently reused.

## Non-collapse boundary (`OBL-D-001E`)

For a declared finite threshold profile `(A_C, epsilon_C)`, define the bounded admissibility predicate:

```text
NonCollapse_C(p,q) iff
  epsilon_C > 0
  and A_C is nonempty
  and p != q
  and distinction_C(p,q) >= epsilon_C
```

Zero and subthreshold distinctions are rejected as inadmissible in this bounded model. Equality at the positive threshold is accepted only when participant distinction remains explicit. The profile is input data; this note does not derive `epsilon_C` for every domain or context.

## Proof obligations retained

1. Prove or independently check that every admitted `project_w,C(w)` satisfies the required witness typing and binding conditions.
2. Establish the sufficiency of `h` and `t` for the declared bounded relation, without inferring injectivity or reversibility.
3. Derive or separately validate the threshold profile used by `NonCollapse_C`.
4. Search for counterexamples involving missing routes, cross-context payloads, zero distinction, subthreshold distinction, and mismatched exact-minimum profiles.

## Evidence interpretation

Existing finite fixtures and independent reviews support the internal consistency of the declared predicates and their rejection boundaries. They support only bounded, model-relative C1 language. They do not establish universal preservation, injectivity, reversibility, complete information preservation, theorem closure, or external physical validity.

## Falsification conditions

- A typed, admissible, same-context input satisfying all declared premises produces a projected relation that fails `RepDist_C`.
- A zero or subthreshold distinction is accepted by an implementation that claims the stated `NonCollapse_C` boundary.
- Two contexts with incompatible validated profiles are treated as equal without an explicit equality premise.
- A cross-context witness or history payload is accepted as valid transport.

## Governance disposition

This is an additive formalization candidate. `OBL-D-001D` and `OBL-D-001E` remain `OPEN`; no registry promotion, theorem promotion, or claim elevation follows from this note.
