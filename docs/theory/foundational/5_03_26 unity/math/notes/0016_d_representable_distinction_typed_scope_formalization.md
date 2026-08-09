# Typed Scope Formalization for Representable Distinction

## Status

`DEFINITION_CANDIDATE`

- Epistemic status: `CONJECTURED`
- Proof status: `OBLIGATIONS_IDENTIFIED`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Governing obligation: `OBL-D-001D`
- Supersession policy: additive clarification; prior candidate notes remain historical source material.

## Scoped definition

For a declared context `C`, define:

```text
RepDist_C(p,q,w,t,h) iff
  Type_C(p) = TYPE_PROJECTION_C
  and Type_C(q) = TYPE_PROJECTION_C
  and TypedWitness_C(w)
  and Relation_C(p,q,w)
  and TraceCompatible_C(t,w)
  and HistoryPresent_C(h)
```

The predicate is intentionally conjunctive. It does not use an outcome label, projected image alone, residue presence, reconvergence, obstruction, or partial reconvergence as a proxy for representability.

The corresponding projection-preservation candidate is:

```text
PresRep_D,C(x,y,w,t,h) iff
  RepDist_C(Pi_D,C(x), Pi_D,C(y), project_w(w), t, h)
```

This is a candidate scope relation, not a universal preservation theorem. `project_w` is not assumed defined for every source witness, and no injectivity, reversibility, complete information preservation, or external physical validity follows.

## Boundary behavior

Missing witness, wrong projected type, incompatible trace, or omitted required history yields `NOT_REPRESENTABLE` within this declared predicate. Outcome labels are ignored by the predicate. A finite matched-image history contrast is therefore admissible as a negative control against projection-only proxies.

## Evidence and limits

The 2026-07-25 typed representability campaign reports 8/8 passing hand-authored fixtures, including positive, negative, boundary, and matched-image history cases. That result supports bounded candidate validation only. Independent formal acceptance of the component predicates and general preservation under `Pi_D,C` remain open.

## Promotion boundary

This note does not discharge `OBL-D-001D`, does not address the downstream non-collapse obligation `OBL-D-001E`, and does not authorize theorem, axiom, lexicon, or physical-bridge promotion.
