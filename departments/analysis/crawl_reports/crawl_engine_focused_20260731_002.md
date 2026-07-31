# Governed Crawl Report

## Repository Snapshot

Commit: `028a3e3fdd0503d620053fba3ee8c193166d1625`
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

- `AX-R03_IDENTITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
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

Open obligations: AX-R03_IDENTITY, AX-R04_SUBSTITUTION, AX-R05_COMPOSITION, AX-R06_CLOSURE, AX-R07_MALFORMED_CONSTRUCTION, AX-R08_DETERMINISM, AX-R09_ASSOCIATIVITY, AX-R10_COMMUTATIVITY, AX-R11_DOMAIN_OF_DEFINITION, AX-R12_PROJECTION_COMPATIBILITY

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

Canonical JSON hash: `3674BA59254469CED542EA11F1266B0E0D7185F739FCD43731A8F86F448D24EE`
Markdown hash: `E97C3C19F96C3BCAE0A2CDC11C2A64C6A3D3806C506AF0DDC3EE734A4800F9FE`

## Campaign Assessment

Outcome: `PARTIAL_SUCCESS`
Reason: Open relation axiom set and executable semantics
