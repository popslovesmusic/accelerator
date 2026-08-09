# Constructed `Pi_D,C` Model and History-Sufficiency Contract

## Status

`DEFINITION_CANDIDATE`

- Epistemic status: `CONJECTURED`
- Proof status: `OBLIGATIONS_IDENTIFIED`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Governing obligation: `OBL-D-001D`
- Scope: finite constructed model only.

## Constructed projection route

For a declared context `C`, the finite model defines:

```text
Pi_D,C(x) = p_x
```

only when `x` is typed, admissible, and the declared projection route is defined. Otherwise `Pi_D,C(x)` is undefined.

The projected witness constructor is:

```text
project_w(w,x,y,C) = w'
```

where `w'` has type `TYPE_RELATION_WITNESS_C`, context `C`, source value `Pi_D,C(x)`, target value `Pi_D,C(y)`, a declared relation, and a stable witness identifier. If the source witness is absent, mistyped, or not bound to `x,y,C`, `project_w` is undefined.

## History sufficiency

Within this finite model:

```text
HistorySufficient_C(h) iff
  h.context = C
  and h.required = true
  and {projection_invoked, witness_bound} ⊆ h.events
```

Presence alone is insufficient. The history must record both the projection invocation and witness binding events. This is a model contract, not a universal definition of history.

## Constructed preservation condition

```text
PresRep_D,C(x,y,w,t,h) iff
  Pi_D,C(x) and Pi_D,C(y) are defined
  and project_w(w,x,y,C) is defined
  and TypedWitness_C(project_w(w,x,y,C))
  and Relation_C(Pi_D,C(x), Pi_D,C(y), project_w(w,x,y,C))
  and TraceCompatible_C(t, project_w(w,x,y,C))
  and HistorySufficient_C(h)
```

The finite checker constructs projected values and witnesses rather than treating those outputs as fixture labels.

## Limits

The model does not establish that every domain has this projection route, that `Pi_D,C` is injective or reversible, or that the finite history event set is complete. OBL-D-001D and OBL-D-001E remain open.
