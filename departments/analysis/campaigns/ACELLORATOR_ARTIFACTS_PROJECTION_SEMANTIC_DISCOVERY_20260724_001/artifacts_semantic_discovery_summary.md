# Artifacts Projection Semantic Discovery ? 2026-07-24

## Scope
Read-only characterization of `registry/db/acellorator_index.sqlite` table `artifacts`, comparison with the prior source-only candidate projection, and bounded current-workspace inventory. No builder revision or production mutation was performed.

## Directly observed/defined
- Legacy artifacts rows: **110596**.
- Candidate source-inventory rows: **2191**.
- Exact normalized path intersection: **2180**.
- Current workspace paths present for legacy rows: **110384**; absent: **212**.
- Legacy artifact classes were assigned deterministically and counts reconcile to **110596**.
- The largest legacy populations are `bin` (41629), `json` (35606), `directory` (17610), and `log` (6548).

## Inferred inside framework
The source-only candidate is not semantically equivalent to the legacy projection. The legacy table is a mixed projection containing physical files/directories, historical/generated outputs, command-audit material, runtime/build products, database sidecars, and transient or unresolved legacy records. A universal normalized path key is insufficient; retained classes require class-aware identity and lineage.

## External resemblance (Analogy only)
The legacy table resembles a materialized artifact catalog with multiple retention strata. This is an analogy about storage shape, not a claim about external systems.

## What it does NOT prove
This campaign does not prove which legacy classes should remain in production, that all absent paths are disposable, or that the revised contract is approved. It does not revise the builder.

## Failure modes / uncertainty
The `LEGACY_ONLY_UNRESOLVED` class contains rows whose current source or generation lineage is unavailable from the bounded corpus. Historical epoch identity, command-audit retention, and class-level authority require human decisions. Gap attribution is therefore partial rather than a final migration decision.

## Recommendation
Status: **PASS_PARTIAL_TAXONOMY_REQUIRES_HUMAN_DECISION**. Approve the revised contract only after deciding retained classes, separate projections, and historical-row disposition. Keep builder revision locked until `PASS_ARTIFACTS_SEMANTICS_CLOSED`.

## Actions explicitly not taken
No source files, legacy database, candidate database, production database, builder, or authoritative registry was modified. No cleanup, deletion, migration, or cutover was executed.
