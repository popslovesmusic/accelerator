# Artifact Projection Decomposition and Composite Reconstruction

## Scope
Read-only decomposition of the legacy `artifacts` projection into deterministic sub-projections. No builder implementation, migration, cutover, or source/database mutation occurred.

## Directly observed/defined
- Legacy population: **110,596** rows.
- Allocation: governed source **9**, workspace catalog **110,131**, generated catalog **164**, runtime/transient catalog **262**, historical register **30**.
- Allocation total: **110,596**, with zero unallocated rows.
- Five non-overlapping primary sub-projections and one deterministic composite compatibility view are specified.
- Known static artifacts-table consumers were mapped to compatibility fields and sub-projections.

## Inferred inside framework
The production-facing artifact layer should be treated as a composite derived projection. Governed source authority, observable workspace state, generated outputs, runtime transients, and historical traceability must have separate identities and lifecycle policies.

## External resemblance (Analogy only)
The decomposition resembles a layered materialized catalog. This describes repository storage behavior only and is not a claim about external systems.

## What it does NOT prove
This campaign does not prove semantic equivalence, builder correctness, or production cutover readiness. The builders remain unimplemented and the compatibility tests remain specifications.

## Failure modes / uncertainty
Dynamic or external consumers not visible in repository text search may exist. The historical exception register requires human retention/disposition review. Runtime transients may be needed by legacy workflows and therefore remain available through a compatibility view.

## Decision
Status: **PASS_ARTIFACT_PROJECTION_DECOMPOSITION_COMPLETE**. The next authorized campaign may implement independent candidate builders and validate composite equivalence. Production cutover remains unauthorized.

## Actions explicitly not taken
No legacy database writes, source edits, builder edits, deletion, cleanup, migration, or production switch were performed.
