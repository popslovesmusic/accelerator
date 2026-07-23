# Candidate Contract: Non-Collapse Boundary for `Pi_D,C`

## Status

`DEFINITION_CANDIDATE`  
Epistemic status: `CONJECTURED`  
Proof status: `OBLIGATIONS_IDENTIFIED`  
Obligation: `OBL-D-001E`

Define typed collapse separately from ordinary residue:

```text
Collapse_D,C(x) iff
  x is well-typed and admissible
  and Pi_D,C(x) is undefined
  or RequiredRep_C(x) has no projected witness.
```

An evaluation with a defined projected value and non-empty `Residue_D,C` is not collapse by that fact alone. Collapse is a failure of required representability or defined projection, not a post-hoc label for an undesirable outcome.

The boundary has three declared cases:

1. `DEFINED_REPRESENTABLE`: projected value and required witness exist;
2. `DEFINED_RESIDUAL`: projected value exists and residue is non-empty, while representability remains explicit;
3. `COLLAPSED`: projection or required witness is undefined.

The candidate is scoped to the declared context and finite fixture space. It does not claim that every collapse mode has been enumerated.

