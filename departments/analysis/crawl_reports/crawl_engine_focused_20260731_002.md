# Governed Crawl Report

## Repository Snapshot

Commit: `0f73a8c853517eadcef0fa2efced226bffe8e667`
Snapshot hash: `4B117A6DB5E4556959234DF8C501232FF0F51C67C0AB91CBC35253041686F9E1`
Dirty state: `True`

## Scope

Focused crawl: `SymmetryConditionRelation` (`|`).

## Objects Analyzed

- `bounded_symmetry` — `PRIMITIVE_DEFINITION` / `PROVISIONALLY_DEFINED` / notation `<S>`
- `distinction_permitting_symmetry_condition` — `NOTATION_ALIAS` / `BLOCKED` / notation `(*|*)`
- `dominant_domain_projection` — `DERIVED_DEFINITION` / `BLOCKED` / notation `Π_(D,A_D)`
- `symmetry_condition` — `DERIVED_DEFINITION` / `PROVISIONALLY_DEFINED` / notation `S`
- `symmetry_condition_relation` — `DERIVED_DEFINITION` / `PROVISIONALLY_DEFINED` / notation `|`
- `unbounded_symmetry` — `PRIMITIVE_DEFINITION` / `PROVISIONALLY_DEFINED` / notation `>S<`

## Dependency Summary

Nodes: 8; edges: 8; cycles: 0

- `distinction_permitting_symmetry_condition` --ALIASES--> `symmetry_condition`
- `dominant_domain_projection` --BLOCKED_BY--> `relation_axioms`
- `dominant_domain_projection` --CONSUMES_TYPE--> `symmetry_condition`
- `executable_semantics` --DEPENDS_ON--> `relation_axioms`
- `relation_axioms` --REQUIRES_PROOF_OF--> `symmetry_condition_relation`
- `symmetry_condition_relation` --CONSUMES_TYPE--> `bounded_symmetry`
- `symmetry_condition_relation` --CONSUMES_TYPE--> `unbounded_symmetry`
- `symmetry_condition_relation` --RETURNS_TYPE--> `symmetry_condition`

## Cycle Analysis

Cycle count: 0

## Direct Blockers

- `AX-R11_DOMAIN_OF_DEFINITION` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R12_PROJECTION_COMPATIBILITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `BLOCK-Q0-INVENTORY-MISSING` `OPERATIONAL_TOOL_FAILURE` blocks `runtime_authority_query`
- `BLOCK-R08-CANONICAL-PROJECTION-SELECTION` `MISSING_DEFINITION` blocks `symmetry_condition_relation, executable_semantics`

## Propagated Blockers

- `BLOCK-PROJECTION-PROPAGATED` propagates to `dominant_domain_projection, executable_semantics` via `[['relation_axioms', 'symmetry_condition_relation', 'dominant_domain_projection']]`

## Proof State

Open obligations: OBL-RT-IDENTITY-WHOLE, OBL-RT-WHOLE-COMPOSITION, OBL-SC-OPERAND-PROJECTION, OBL-R08-CANONICAL-PROJECTION-SELECTION, AX-R11_DOMAIN_OF_DEFINITION, AX-R12_PROJECTION_COMPATIBILITY

## Not Established

- proof
- universal equivalence
- physical correspondence
- complete executable semantics
- zero cycles as mathematical correctness

## Delta Since Prior Crawl

Added: ['symmetry_condition']
Modified: ['bounded_symmetry', 'distinction_permitting_symmetry_condition', 'dominant_domain_projection', 'symmetry_condition_relation', 'unbounded_symmetry']
Status changed: ['distinction_permitting_symmetry_condition']

## Validation Results

{"determinism_validation": {"status": "ENGINE_TESTED"}, "graph_integrity_validation": {"passed": true}, "readonly_validation": {"after_hash": "4B117A6DB5E4556959234DF8C501232FF0F51C67C0AB91CBC35253041686F9E1", "before_hash": "4B117A6DB5E4556959234DF8C501232FF0F51C67C0AB91CBC35253041686F9E1", "changed_paths": [], "checked": true, "read_only": true}, "renderer_consistency_validation": {"status": "RENDERED_FROM_CANONICAL_JSON"}, "schema_validation": {"errors": [], "passed": true}, "source_precedence_validation": {"passed": true}}

## Output Hashes

Canonical JSON hash: `093ACAC59E1215B00559556B9B89A50773B7EC361F76BBFF1669CB8C0A8CEF45`
Markdown hash: `7F43A5646F7E7339EC7F908C6F13030412513BF3C7265DC06AF266DC137AEA61`

## Campaign Assessment

Outcome: `PARTIAL_SUCCESS`
Reason: Open relation axiom set and executable semantics
