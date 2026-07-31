# Governed Crawl Report

## Repository Snapshot

Commit: `88a5209f30208ef66a98916b6da4f4741017f96b`
Snapshot hash: `8A1EDDF39738642D48EBB9CB08B0F8B3B86AB03B58D53278CDF8F93BA4CA58E2`
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

- `AX-R04_SUBSTITUTION` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R05_COMPOSITION` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R06_CLOSURE` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R07_MALFORMED_CONSTRUCTION` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R08_DETERMINISM` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R09_ASSOCIATIVITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R10_COMMUTATIVITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R11_DOMAIN_OF_DEFINITION` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R12_PROJECTION_COMPATIBILITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`

## Propagated Blockers

- `BLOCK-PROJECTION-PROPAGATED` propagates to `dominant_domain_projection, executable_semantics` via `[['relation_axioms', 'symmetry_condition_relation', 'dominant_domain_projection']]`

## Proof State

Open obligations: OBL-RT-IDENTITY-WHOLE, AX-R04_SUBSTITUTION, AX-R05_COMPOSITION, AX-R06_CLOSURE, AX-R07_MALFORMED_CONSTRUCTION, AX-R08_DETERMINISM, AX-R09_ASSOCIATIVITY, AX-R10_COMMUTATIVITY, AX-R11_DOMAIN_OF_DEFINITION, AX-R12_PROJECTION_COMPATIBILITY

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

{"determinism_validation": {"status": "ENGINE_TESTED"}, "graph_integrity_validation": {"passed": true}, "readonly_validation": {"after_hash": "8A1EDDF39738642D48EBB9CB08B0F8B3B86AB03B58D53278CDF8F93BA4CA58E2", "before_hash": "8A1EDDF39738642D48EBB9CB08B0F8B3B86AB03B58D53278CDF8F93BA4CA58E2", "changed_paths": [], "checked": true, "read_only": true}, "renderer_consistency_validation": {"status": "RENDERED_FROM_CANONICAL_JSON"}, "schema_validation": {"errors": [], "passed": true}, "source_precedence_validation": {"passed": true}}

## Output Hashes

Canonical JSON hash: `C6D1C49CD5C43160B63A59390FC601F2B5D71F59F57190063E833F62B5F6A7F0`
Markdown hash: `572043E7EED1BA24F61116189B900CEF873211CE45649699F30112555D83AC18`

## Campaign Assessment

Outcome: `PARTIAL_SUCCESS`
Reason: Open relation axiom set and executable semantics
