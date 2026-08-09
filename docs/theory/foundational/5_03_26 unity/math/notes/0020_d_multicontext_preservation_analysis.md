# Multi-Context Preservation Analysis

## Status

`ANALYSIS_CANDIDATE`

- Governing obligation: `OBL-D-001D`
- Claim ceiling: `C1_DEFINED_PROVISIONAL`
- Scope: bounded finite contexts and explicit context-isolation checks.

## Analysis condition

For each declared context `C`, the structured model constructs `project_v(x,C)` and `project_w(w,v_x,v_y,C)` only within `C`. A preservation result requires:

```text
PresRep_D,C iff
  source and target are typed/admissible
  and the route is defined in C
  and the witness is bound in C
  and history payloads identify C and the same projected values/witness
  and the trace is compatible
```

The analysis treats context as part of the constructed values and history payloads. A witness or history record from another context is therefore not silently reusable.

## Bounded contexts

The fixtures use two independently named defined contexts and one context with no defined route. They test positive preservation in each defined context, cross-context history mismatch, cross-context witness mismatch, undefined route, inadmissible source, and incompatible trace.

## Limits

This does not establish preservation over all domains or contexts, does not prove injectivity or reversibility, and does not discharge OBL-D-001E.
