# Governance Evidence Forensic Audit

## Executive finding
All 124 decisions were streamed and raw-hashed. Evidence totals 11,031,215,381 bytes; the database pre/post SHA-256, size, and modification time matched.

## Confirmed growth mechanism
Inline storage in `governance_decision_log.evidence_json` is confirmed. Full-snapshot accumulation remains unresolved under the bounded parser.

## Largest byte contributors
The largest payload is 963,426,339 bytes; 17 payloads received bounded deep sampling at or above 100 MiB.

## Internal duplication
One exact cross-decision duplicate group is quantified. Internal subtree duplication remains unresolved because full DOM parsing exceeded safe memory limits.

## Cross-decision accumulation
All raw payloads were SHA-256 hashed. Canonical near-duplicate and inherited-block analysis remains unresolved.

## Recursive embedding
Marker candidates were recorded, but markers are not proof. Structural confirmation remains unresolved.

## Reconstructability
Reference candidates were extracted, but major content blocks remain `UNRESOLVED` pending hash-resolved artifact comparison.

## Authority-preserving redesign
Design-only recommendation: compact inline envelope plus content-addressed evidence manifests, with snapshot roots and deltas.

## Estimated effect
A 2,048-byte illustrative envelope would require approximately 253,952 inline bytes; external storage effects remain unresolved.

## Unresolved risks
Canonical JSON hashing, complete JSON-path attribution, semantic similarity, and byte-identical reconstruction require a memory-safe streaming JSON parser.

## Actions explicitly not taken
No SQL writes, evidence deletion, externalization, migration, compaction, source modification, or remediation was performed.
