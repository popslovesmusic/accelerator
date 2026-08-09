# Frozen D/E Baseline — 2026-07-27

This baseline freezes the synchronized registry, SSOT, textbook, DB snapshot, and Notebook 22 evidence as the starting point for resolving `OBL-D-001D` and `OBL-D-001E`.

## Locks

- `OBL-D-001A`: `DISCHARGED`
- `OBL-D-001B`: `DISCHARGED_BOUNDED`
- `OBL-D-001C`: `DISCHARGED_BOUNDED`
- `OBL-D-001D`: `OPEN`
- `OBL-D-001E`: `OPEN`
- Formal claim ceiling: `C1_DEFINED_PROVISIONAL`
- A–C canonical definitions and statuses are frozen and must not be reopened or altered during D/E work.

## Preserved surfaces

The companion JSON manifest records SHA-256 hashes for the canonical registry surfaces, all department SSOTs, the textbook freshness contract, the textbook, the DB snapshot identity, and the Notebook 22 notebook/spec/archive evidence.

Notebook 22 remains a bounded `C2_LIMITATION_OR_NEGATIVE_RESULT`: four finite rows, bare witnesses passing `0/2`, enriched witnesses passing `2/2`, with endpoint projection collision preserved as a limitation.

## Change control

D/E work may add bounded evidence, reviews, falsification tests, and analysis artifacts. It may not modify A–C canonical definitions, reopen A–C statuses, raise the claim ceiling without governed evidence, or overwrite frozen artifacts. Any exception requires an explicit governed unfreeze or superseding-baseline record.
