# D Semantics Work Package Execution Plan

1. Complete `OBL-D-001A` by writing the typed `Eval_D,C` contract.
2. In parallel, formalize `OBL-D-001B` threshold semantics and define the sensitivity test.
3. Validate the A and B deliverables through human review.
4. Execute `OBL-D-001C` typed preservation proof and mechanized fixtures.
5. Execute `OBL-D-001D` representable-distinction definition and matched countermodel search.
6. Execute `OBL-D-001E` non-collapse boundary fixtures and countermodel sweep.
7. Revalidate all upstream certificates before any downstream closure.
8. Discharge only obligations whose acceptance tests and required reviews pass.

## Escalation

Missing types or tools keep the obligation open and route to human review. A contradiction creates a preserved contradiction case. Any counterexample reopens the obligation. Any upstream dependency change invalidates dependent completion certificates.
