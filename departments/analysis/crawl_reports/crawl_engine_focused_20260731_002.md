# Governed Crawl Report

## Repository Snapshot

Commit: `d01a112c8fa8d32720379c873b2a927c37cbe2c5`
Snapshot hash: `8047ACCFA1FC828269E4E82ED277940658400CCFC6BA3042D00270A4E664BE56`
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

- `AX-R08_DETERMINISM` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R09_ASSOCIATIVITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R10_COMMUTATIVITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R11_DOMAIN_OF_DEFINITION` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R12_PROJECTION_COMPATIBILITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `BLOCK-Q0-INVENTORY-MISSING` `OPERATIONAL_TOOL_FAILURE` blocks `runtime_authority_query`

## Propagated Blockers

- `BLOCK-PROJECTION-PROPAGATED` propagates to `dominant_domain_projection, executable_semantics` via `[['relation_axioms', 'symmetry_condition_relation', 'dominant_domain_projection']]`

## Proof State

Open obligations: OBL-RT-IDENTITY-WHOLE, OBL-RT-WHOLE-COMPOSITION, OBL-SC-OPERAND-PROJECTION, AX-R08_DETERMINISM, AX-R09_ASSOCIATIVITY, AX-R10_COMMUTATIVITY, AX-R11_DOMAIN_OF_DEFINITION, AX-R12_PROJECTION_COMPATIBILITY

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

{"determinism_validation": {"status": "ENGINE_TESTED"}, "graph_integrity_validation": {"passed": true}, "readonly_validation": {"after_hash": "8047ACCFA1FC828269E4E82ED277940658400CCFC6BA3042D00270A4E664BE56", "before_hash": "8047ACCFA1FC828269E4E82ED277940658400CCFC6BA3042D00270A4E664BE56", "changed_paths": [], "checked": true, "read_only": true}, "renderer_consistency_validation": {"status": "RENDERED_FROM_CANONICAL_JSON"}, "schema_validation": {"errors": [], "passed": true}, "source_precedence_validation": {"passed": true}}

## Output Hashes

Canonical JSON hash: `FADC71FD0AB32D29FF0630E357DBE5D7CCA3872A7661D07A171E8AB6C4F2B4F9`
Markdown hash: `03639A6E460A91F33EE2ABC171AC9937E197D7F60CC9B9CA5E2B9DC4E25C2AA0`

## Campaign Assessment

Outcome: `PARTIAL_SUCCESS`
Reason: Open relation axiom set and executable semantics
