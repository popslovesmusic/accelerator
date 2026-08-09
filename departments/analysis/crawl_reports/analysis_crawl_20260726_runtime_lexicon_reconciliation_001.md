# Analysis Crawl: Runtime Lexicon Reconciliation

## Campaign Purpose

Reconcile the governance runtime’s 11 missing core validation keys with the live lexicon gap queue, validation registry, D-gate state, textbook freshness state, and DB snapshot.

## Scope and source artifact set

This was a bounded, read-only crawl. It inspected the runtime manifest, lexicon validation registry, lexicon gap queue, the latest prior crawl, combined D review 017, the textbook freshness contract, global validation output, and the registry DB snapshot.

## Directly observed/defined

- The governance runtime remains `BLOCK` because 11 exact core-term keys are absent from `registry/lexicon_validation_registry.json`.
- All 11 terms are now present in `registry/lexicon_gap_queue.json` as `GAP_OPEN`, with `C0_UNDEFINED` claim status and `not_verified` governance status.
- The textbook freshness contract is `current`; the latest DB snapshot is `REFRESH-20260727T013300668330Z`.
- Global validation is `warning` with no failed stages or semantic failures in the recorded report.
- The latest D review remains `BLOCKED_NOT_READY` with claim ceiling `C1_DEFINED_PROVISIONAL`; OBL-D-001D and OBL-D-001E remain open.

## Inferred inside framework

The queue induction reduced provenance debt by preserving the 11 runtime-required names, but it did not reduce validation debt. Exact-key runtime synchronization, operational definition, role classification, and evidence validation remain separate obligations.

## Findings and support

1. **Governance defect — observed, C1 governance validation:** the runtime manifest and validation registry are not synchronized under the runtime’s exact-key rule.
2. **Proof gap — observed, C0 undefined:** the 11 terms have no accepted role-specific validation state.
3. **D proof obligation — source-reported, C1 defined provisional:** bounded D/E evidence remains blocked from stronger promotion.

## What was not learned

The crawl did not determine valid definitions for the 11 terms, establish their roles, validate them, discharge D obligations, or establish any external or physical correspondence.

## Recommended next action

Prepare a bounded lexicon review package for the 11 `GAP_OPEN` terms, starting with role-specific definitions and exact validation requirements. Then rerun the runtime check. Keep all terms unvalidated until the required evidence is accepted.

## Failure modes / uncertainty

The runtime check is an exact-name presence check and does not perform alias resolution. Near-match terms may exist elsewhere, but they do not satisfy the current runtime contract. The crawl did not adjudicate whether the runtime core set itself is correctly scoped.

## Campaign Assessment

`PARTIAL_SUCCESS_RUNTIME_LEXICON_DEBT_RECORDED`. The crawl reconciled the current state and identified one bounded successor action. It does not authorize registry promotion, validation, execution, or theorem closure.

## Crawl boundary

Only noncanonical crawl reports were emitted. No canonical registry, source artifact, script, configuration, executable work item, or authority-bearing report was modified.
