# Bounded D/E Formal Modeling Package

## Status

`CANDIDATE_REVIEW_REQUIRED`

- Epistemic status: `CONJECTURED`
- Proof status: `OBLIGATIONS_IDENTIFIED`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Governing obligations: `OBL-D-001D`, `OBL-D-001E`
- Canonical promotion: prohibited

## Objective

Make the unresolved semantic dependencies explicit in a finite model: witness provenance, history sufficiency, and the definedness/preservation route for `Pi_D,C`.

## Typed model

For a declared context `C`, define finite records:

```text
Witness_C = (id, context, source, target, provenance)
History_C = ordered events
Projection_C = (input, output, context, defined)
```

`Witness_C` is admissible only when its provenance names the source relation and the context. `History_C` is sufficient for this model only when it contains ordered `projection_invoked` and `witness_bound` events whose payloads agree on context, projected source/target values, and witness identifier.

The model route is:

```text
x,y admissible
  -> Pi_D,C(x), Pi_D,C(y) defined
  -> witness_projected(w,x,y,C) defined
  -> Relation_C(Pi_D,C(x), Pi_D,C(y), witness_projected)
  -> TraceCompatible_C
  -> HistorySufficient_C
```

`PresRepModel_C(x,y,w,t,h)` is true only when every arrow is defined and the final conjunction holds. Any missing provenance, mismatched payload, unordered history, undefined projection, or incompatible trace is a model failure.

## D/E boundary

The model tests preservation of declared representable distinctions in a finite synthetic domain. It does not derive a universal `Pi_D,C`, prove injectivity, reversibility, complete information preservation, or derive `epsilon_a,C`. The E-side non-collapse threshold is supplied as a finite model input and is not promoted to a universal law.

## Acceptance tests

1. Valid source/target/context/witness/history fixture passes.
2. Missing witness provenance fails.
3. History with presence but no ordered linkage fails.
4. Context or projected-value mismatch fails.
5. Undefined projection fails without being classified as universal information loss.
6. Subthreshold and zero distinctions fail the E boundary; minimum positive distinction passes only within the supplied threshold model.

## Required independent review

Review must determine whether provenance and history predicates are semantically adequate, whether the model is circular, and whether the finite fixtures actually instantiate `Pi_D,C` rather than labels. Review must not change canonical obligation status without a separately authorized registry action.
