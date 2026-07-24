# D-Semantics Representability and Witness Recovery Summary

## Scope and Purpose
This document summarizes the recovered semantics of `RepDist_C` and `TypedWitness_C` from repository notes, candidates, and notebooks, incorporating the resolved human decision surface.

---

## Established Facts
- **Obligation Status**: `OBL-D-001D` remains `OPEN`.
- **Scope Limit**: `OBL-D-001C` (proved in `P126`) establishes type-preservation only. It does not establish semantic representability.
- **Proxy Failures**: Projection-only and outcome-label-only representability proxies are falsified by 4 and 594 counterexamples respectively in finite-model tests.

---

## Resolved Human Decisions
- **Nature of TypedWitness_C (DEC-SEM-001)**: Resolved to Refine Option A. `TypedWitness_C` is formally defined as a semantic witness abstraction. Trace certificates, Lean proof terms, and executable artifacts are representations of that witness rather than the witness itself.
- **Trace Compatibility Indexation (DEC-SEM-002)**: Resolved to Accept Option A. `TraceCompatible_C` is explicitly indexed by context `C`.

---

## Constrained Inferences
- **No Circularity**: We infer that the relationship between `TypedWitness_C` and `RepDist_C` is hierarchical and non-circular. The witness `w` is a parameter passed to the representability predicate.
- **Outcome Independence**: We infer that representability is independent of the target outcome label. A transition can fail to reconverge but still carry a representable distinction.

---

## Proposals
- **Candidate RepDist_C Predicate**: We propose defining `RepDist_C(p, q, w) iff type(p) = TYPE_PROJECTION_C and type(q) = TYPE_PROJECTION_C and TypedWitness_C(w) and Relation_C(p, q, w) and TraceCompatible_C(w)`.
- **Candidate TypedWitness_C Predicate**: We propose representing the witness `w` as a typed relational provenance token mapping source to target.

---

## Unknowns
- **Witness Structure**: The formal algebraic type structure of `TYPE_WITNESS_C` is not yet defined in the registry.
- **Relational Mapping**: The exact axioms for `Relation_C` remain undefined in the proof registry.

---

## Smallest Next Task
The exact next task is to write a new foundational theory document formalizing `TYPE_WITNESS_C` structure and the `Relation_C` axioms in context `C` to fully discharge `OBL-D-001D` blockers.
