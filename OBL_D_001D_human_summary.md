# OBL-D-001D: Representable Distinction Preservation Audit Summary

## Scope and Purpose
This audit analyzes the formal requirements, existing evidence, missing definitions, and counterexamples for proof obligation `OBL-D-001D` (Representable Distinction Preservation) and details its logical relationship to `OBL-D-001E` (Non-Collapse Boundary).

---

## Established Facts
- **Obligation Status**: `OBL-D-001D` is registered as `OPEN`.
- **Preceding Dependencies**: `OBL-D-001A` (domain/codomain), `OBL-D-001B` (context threshold), and `OBL-D-001C` (type-level preservation) are fully discharged within bounded type-level scope.
- **Type-Level Boundary**: `OBL-D-001C` (proved in `P126`) establishes only that projection targets map to `TYPE_PROJECTION_C`. It does not prove semantic representability or distinction preservation.
- **Falsified Proxies**: Finite-model searches (`D_REPRESENTABLE_DISTINCTION_COUNTEREXAMPLE_SEARCH_20260723` and `D_REPRESENTABLE_DISTINCTION_BROADER_SEARCH_20260723`) have falsified both projection-only and outcome-label-only representability proxies using 4 and 594 counterexamples respectively.

---

## Interpretations and Proposals
- **Representable Distinction Predicate**: It is proposed that representability in context `C` is defined by the conjectured predicate `RepDist_C(p, q, w)` which requires a valid projected pair, a typed relation witness `w`, and a compatible trace.
- **Independence of Outcome**: We interpret representability as independent of target outcome labels (such as `reconvergence` or `obstruction`). Using outcome labels as proxies is circular.
- **Preservation Concept**: Preservation `PresRep_D,C(x, y, w)` is defined as the projection of a source witness to a target witness such that the target satisfies `RepDist_C`.

---

## Unknowns
- **Universal Validity**: The behavior of representability preservation outside the finite synthetic fixture space remains unknown.
- **Formal Predicate Syntax**: The exact syntactic rules and axioms for relation witnesses and trace compatibility are not yet formalized.

---

## Relationship to OBL-D-001E
- **Implication**: `OBL-D-001D` implies `not Collapse_D,C(x)` (the non-collapse boundary `OBL-D-001E`) *only with additional premises*. Specifically, it requires the premise that admissibility requires or guarantees a representable distinction, or that every admissible source carries a required distinction.
- **Classification**: `D_IMPLIES_E_ONLY_WITH_ADDITIONAL_PREMISES`.

---

## Smallest Next Task
The exact next step is to formalize the candidate definitions of `RepDist_C`, `TypedWitness_C`, and `TraceCompatible_C` in a new foundational theory file inside `docs/theory/foundational/5_03_26 unity/math/math/` to resolve the blocker.
