# Structured Projection and History-Linkage Model

## Status

`DEFINITION_CANDIDATE`

- Governing obligation: `OBL-D-001D`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Scope: finite synthetic model extending 0018 without changing its artifacts.

## Structured projection

For a declared context `C`, the model constructs a projected value:

```text
project_v(x,C) = {
  context: C,
  source_id: id(x),
  value: p_id(x),
  type: TYPE_PROJECTION
}
```

only when `x` is typed, admissible, and the projection route is defined. The construction is undefined otherwise.

## Structured witness

Given projected source and target values, the model constructs:

```text
project_w(w,v_x,v_y,C) = {
  witness_id: id(w),
  context: C,
  source: v_x.value,
  target: v_y.value,
  relation: RELATION_C,
  type: TYPE_RELATION_WITNESS_C
}
```

only when the source witness is bound and the projected values share the declared context.

## Linked history

`HistorySufficient_C(h,w,v_x,v_y)` requires, in order:

1. `projection_invoked` records the context and source/target projected values;
2. `witness_bound` records the same context and the constructed witness identifier;
3. both records refer to the same projected values and witness.

The model therefore tests ordering, payload linkage, and witness identity linkage rather than event presence alone.

## Limits

This is a finite candidate model. It does not establish universal projection semantics, injectivity, reversibility, complete history, or OBL-D-001E closure.
