# Structural Index Build

## Executive result
The external derived index is `PASS_STRUCTURAL_INDEX_PARTIAL_RESUMABLE`. It passes SQLite integrity validation and contains 76 decision records, 74 completed parses, 961,945 JSON nodes, and 89 checkpoints.

## Source read-only verification
The recorded source SHA-256 is FC0EA2DC93DAB7F7726ED9EA63650DF26158148C951C8384DF6F3E765F2DF31F; source modification was not performed.

## Index design
The index is outside `registry`, uses read-only source access and incremental BLOB reads, and is explicitly derived/rebuildable.

## Rows completed and failed
The source population is 124 decisions. This interrupted run has partial coverage and must resume before full acceptance.

## Largest-payload result
The largest source payload is 963,426,339 bytes; large-payload validation remains partial.

## Resource performance
The external index process remained bounded-memory; the index reached approximately 2.6 GB before interruption.

## Resumability verification
89 checkpoint records are present and the index passes integrity check.

## Preliminary structural findings
Path, repeated-value, and large-string rankings are preliminary queries over completed indexed rows only.

## Known limitations
Coverage is incomplete; canonical subtree hashes and full 124-row validation remain outstanding.

## Recommended next audit
Resume the index build from checkpoint state, then run the structural-index query forensic audit.

## Actions explicitly not taken
No source database, registry, workspace source, or remediation target was modified.
