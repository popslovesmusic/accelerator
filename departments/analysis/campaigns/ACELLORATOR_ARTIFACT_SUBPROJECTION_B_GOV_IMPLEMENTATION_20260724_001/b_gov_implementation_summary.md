# B-GOV Governed Source Inventory Implementation

## Scope
B-GOV is implemented as an isolated non-production builder over current `.md` and `.json` files under `docs/` and `registry/`. Legacy database access used an immutable read-only connection.

## Directly observed/defined
- Current governed-source records emitted: **2192**.
- Root counts: `docs/` **925**, `registry/` **1267**.
- Two independent rebuilds are byte-identical.
- Every record contains canonical identity, source path/type, content hash, authority metadata, and provenance.
- Workspace-only, generated, transient, and historical-only records are excluded.

## Inferred inside framework
B-GOV is the authoritative governed-source subprojection and is not the complete composite artifacts catalog.

## What it does NOT prove
It does not prove full artifacts-table equivalence or authorize production cutover. Remaining subprojection builders are untouched.

## Legacy comparison
The predecessor campaign reported nine legacy governed rows and 2,191 candidate rows. The current read-only comparison reports ten legacy governed rows and 2,192 B-GOV records; this snapshot drift is recorded explicitly, and neither legacy count is used as the completeness target.

## Freeze
**FROZEN_VALIDATED**. Downstream non-production builders may depend on B-GOV. Any modification requires a B-GOV revision and revalidation packet.

## Actions explicitly not taken
No source, legacy database, production database, B-WS/B-GEN/B-RT/B-HIST/B-COMP builder, migration, or cutover was modified or executed.
