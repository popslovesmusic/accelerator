# Governed Crawl Report

## Repository Snapshot

Commit: `ed7af90f5be4bda170c37150aa4596a240db2567`
Snapshot hash: `F13FDADE9A8644A485BFFF682424A1CFA7893A5A3295275CCD070B1B1B06F392`
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

- `AX-R12_PROJECTION_COMPATIBILITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `BLOCK-Q0-INVENTORY-MISSING` `OPERATIONAL_TOOL_FAILURE` blocks `runtime_authority_query`
- `BLOCK-R08-CANONICAL-PROJECTION-SELECTION` `MISSING_DEFINITION` blocks `symmetry_condition_relation, executable_semantics`
- `BLOCK-R11-EXECUTABLE-TOTALITY` `MISSING_EXECUTABLE_SEMANTICS` blocks `symmetry_condition_relation, executable_semantics`
- `BLOCK-R11-ASYM-DOMAIN-COMPATIBILITY` `MISSING_TYPE_RULE` blocks `symmetry_condition_relation`

## Propagated Blockers

- `BLOCK-PROJECTION-PROPAGATED` propagates to `dominant_domain_projection, executable_semantics` via `[['relation_axioms', 'symmetry_condition_relation', 'dominant_domain_projection']]`

## Proof State

Open obligations: OBL-RT-IDENTITY-WHOLE, OBL-RT-WHOLE-COMPOSITION, OBL-SC-OPERAND-PROJECTION, OBL-R08-CANONICAL-PROJECTION-SELECTION, OBL-R11-EXECUTABLE-TOTALITY, OBL-R11-ASYM-DOMAIN-COMPATIBILITY, AX-R12_PROJECTION_COMPATIBILITY

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

{"determinism_validation": {"status": "ENGINE_TESTED"}, "graph_integrity_validation": {"passed": true}, "readonly_validation": {"after_hash": "F13FDADE9A8644A485BFFF682424A1CFA7893A5A3295275CCD070B1B1B06F392", "before_hash": "F13FDADE9A8644A485BFFF682424A1CFA7893A5A3295275CCD070B1B1B06F392", "changed_paths": [], "checked": true, "read_only": true}, "renderer_consistency_validation": {"status": "RENDERED_FROM_CANONICAL_JSON"}, "schema_validation": {"errors": [], "passed": true}, "source_precedence_validation": {"passed": true}}

## Output Hashes

Canonical JSON hash: `50AAD1449E8E04C52643845A5F4F8880C20920549157215B0B552ABB64404D12`
Markdown hash: `69379B6EB7E96D2A22A76B039518617666C913E93F10525AAF09C46F499E6228`

## Campaign Assessment

Outcome: `PARTIAL_SUCCESS`
Reason: Open relation axiom set and executable semantics
