# Candidate Contract: Representable Distinction under `Pi_D,C`

## Status

`DEFINITION_CANDIDATE`  
Epistemic status: `CONJECTURED`  
Proof status: `OBLIGATIONS_IDENTIFIED`  
Obligation: `OBL-D-001D`

Define a distinction as representable in context `C` only when the projected values and their provenance carry a typed witness for the declared relation, independently of any downstream geometry or outcome label:

```text
RepDist_C(p, q, w) iff
  type(p) = TYPE_PROJECTION_C
  and type(q) = TYPE_PROJECTION_C
  and TypedWitness_C(w)
  and Relation_C(p, q, w)
  and TraceCompatible_C(w)
```

`RepDist_C` is a semantic predicate over projected values, witness, and trace. It is not defined as `universal_reconvergence`, `obstruction`, `residue_present`, or any other outcome label.

`Pi_D,C` preserves a declared distinction only when a source witness has a corresponding projected witness:

```text
PresRep_D,C(x, y, w) iff RepDist_C(Pi_D,C(x), Pi_D,C(y), project_w(w))
```

The candidate does not assert that every source distinction has a projected witness. Missing projected witnesses are evidence for a bounded failure case, not proof of universal information loss.

## Acceptance Boundary

Matched projected-image cases with different source histories must be retained. A predicate that uses the target outcome to label representability is circular and fails review. Counterexamples remain required before discharge.

