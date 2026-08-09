# SQLite Read-Only Triage Summary

## Executive finding
The audit opened both databases through SQLite read-only immutable connections and made no database or source mutations. The primary runtime path is `D:\projects\acellorator\registry\db\acellorator_index.sqlite`.

## Which database is authoritative
`D:\projects\acellorator\registry\db\acellorator_index.sqlite` is AUTHORITATIVE_PROBABLE with HIGH confidence from runtime source defaults. The nested copy is not confirmed authoritative.

## How the second database appeared
Both paths resolve to the same filesystem file identifier and `fsutil hardlink list` reports both paths, so the nested path is a hard-link alias rather than an independent live database. The likely creation mechanism is recursive registry path construction or indexing; the mechanism itself remains an inference.

## Whether the databases diverge
They are classified EXACT_DUPLICATE by current full-file SHA-256 equality; schemas, pragmas, row counts, stable IDs, and divergence evidence are in `database_divergence_report.json`.

## Largest evidence rows
The primary database contains 124 governance decisions. The largest `evidence_json` payload is 963,426,339 bytes, with total evidence storage of 11,031,215,381 bytes.

## Duplicate and recursive-content findings
Raw payload duplicate hashes, JSON-validity samples, embedded-content markers, and bounded structure analysis are in the four governance evidence reports. Full giant payloads were not exported.

## Operational severity
CRITICAL: oversized evidence payloads materially dominate database footprint and create runtime, backup, and integrity-check risk.

## Recommended next patch
Human review should authorize a separate non-destructive remediation design addressing evidence externalization/compaction and nested-database authority. This campaign applied no remediation.

## Actions explicitly not taken
No INSERT, UPDATE, DELETE, schema change, pragma mutation, vacuum, checkpoint, relocation, rename, deletion, source edit, or registry edit was performed.
