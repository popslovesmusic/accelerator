# Governed Crawl Report

## Repository Snapshot

Commit: `666b2099d38c5ea5178926bb13fe22b5249e7c51`
Snapshot hash: `E2A8EB557E3EC1D9C0ABC1D059F01370F5D7BB49B4365C58323E780A5B473676`
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
- `AX-R11_DOMAIN_OF_DEFINITION` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `AX-R12_PROJECTION_COMPATIBILITY` `MISSING_AXIOM` blocks `symmetry_condition_relation`
- `BLOCK-R08-CANONICAL-PROJECTION-SELECTION` `MISSING_DEFINITION` blocks `symmetry_condition_relation, executable_semantics`
- `BLOCK-R11-EXECUTABLE-TOTALITY` `MISSING_EXECUTABLE_SEMANTICS` blocks `symmetry_condition_relation, executable_semantics`
- `BLOCK-R11-ASYM-DOMAIN-COMPATIBILITY` `MISSING_TYPE_RULE` blocks `symmetry_condition_relation`

## Propagated Blockers

- `BLOCK-PROJECTION-PROPAGATED` propagates to `dominant_domain_projection, executable_semantics` via `[['relation_axioms', 'symmetry_condition_relation', 'dominant_domain_projection']]`

## Proof State

Open obligations: OBL-RT-IDENTITY-WHOLE, OBL-RT-WHOLE-COMPOSITION, OBL-SC-OPERAND-PROJECTION, OBL-R08-CANONICAL-PROJECTION-SELECTION, OBL-R11-EXECUTABLE-TOTALITY, OBL-R11-ASYM-DOMAIN-COMPATIBILITY, AX-R08_DETERMINISM, AX-R11_DOMAIN_OF_DEFINITION, AX-R12_PROJECTION_COMPATIBILITY

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

{"determinism_validation": {"status": "ENGINE_TESTED"}, "graph_integrity_validation": {"passed": true}, "readonly_validation": {"after_hash": "E2A8EB557E3EC1D9C0ABC1D059F01370F5D7BB49B4365C58323E780A5B473676", "before_hash": "E2A8EB557E3EC1D9C0ABC1D059F01370F5D7BB49B4365C58323E780A5B473676", "changed_paths": [], "checked": true, "read_only": true}, "renderer_consistency_validation": {"status": "RENDERED_FROM_CANONICAL_JSON"}, "schema_validation": {"errors": [], "passed": true}, "source_precedence_validation": {"passed": true}}

## Output Hashes

Canonical JSON hash: `0719FB36A93C16307A62222D16125DD8DDDFC3EF7776E41AA3401783BE4BFC9C`
Markdown hash: `7C69463A9116E2AB15A3CBE87B22E5AE5E296A93490B2700447006612C615B84`

## Campaign Assessment

Outcome: `PARTIAL_SUCCESS`
Reason: Active open relation axioms and executable semantics
