# R08/R11 Projection Selection and Executable Totality Reassessment

Runtime snapshot: `FRESH / ALLOW`.  
Statuses: `AX-R08 PARTIALLY_RESOLVED_BLOCKED`; `AX-R11 FORMALIZED_WITH_TOTALITY_BLOCKED`.

Validation determinism is established for source resolution, syntax, typing, well-formedness, and malformed diagnostics. Semantic-result uniqueness, projection-selection determinism, and complete executable determinism remain blocked by `OBL-R08-CANONICAL-PROJECTION-SELECTION` and incomplete executable semantics.

The ordered input domain for `|` is recorded, and domain membership gates are defined. This does not establish a total executable result for every legal operand pair.

Downstream impact remains on `dominant_domain_projection` and `executable_semantics`. Required evidence is a separately governed canonical selector, typed executable procedure, tie-breaking/canonical-normal-form rule, and totality validation. No selector or executable semantics were invented.
