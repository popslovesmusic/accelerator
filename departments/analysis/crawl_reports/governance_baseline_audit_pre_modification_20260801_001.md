# Governance Baseline Audit — Pre-Modification

Audit: `GOVERNANCE_BASELINE_AUDIT_PRE_MODIFICATION_001`  
Mode: read-only  
Status: completed with baseline findings  
Claim ceiling: `C1_MODEL_RELATIVE`

## Scope

The incident patch was treated only as a defect-discovery context. Its proposed classifications and controls were not used as current governance, and the withheld original summary was not inducted or evaluated.

## Current lifecycle

The live governance model reconstructs as:

1. Preserve or capture the complete first-contact artifact in Analysis Intake.
2. Record provenance, hashes, capture mode, review status, and promotion status separately.
3. Register the induction in the Global Governance queue.
4. Create the matching canonical induction record.
5. Route new terminology through the lexicon gap queue.
6. Apply validation and claim ceilings before vocabulary or program promotion.
7. Expose the result through read-only analysis projections.

The policy is explicit that review, normalization, classification, promotion, or execution must not precede first-contact preservation.

## Authority and status inventory

| Surface | Current inventory | Authority/function |
|---|---:|---|
| Analysis Intake queue | 11 entries | Preserves first contact and provenance; does not promote |
| Global induction queue | 56 entries | Activation gate for active governed work |
| Canonical induction registry | 53 entries | Canonical induction record |
| Lexicon gap queue | 261 entries | Term resolution and validation pipeline |
| Canonical lexicon | 1,085 terms | Downstream vocabulary projection |

Observed global queue statuses are `bound_to_registry` (45), `queued` (8), and `excluded_frozen` (3). Review and promotion fields remain separate, including `NOT_REVIEWED`, `PARTIAL`, `HOLD_C1`, and `UNQUEUED_FOR_PROMOTION`.

## Preservation guarantee

The preservation guarantee is strong at the intake layer. Records carry source paths, hashes, sizes, capture modes, immutable-capture markers, and preservation statuses such as `PRESERVED_LITERAL`, `PRESERVED_PROVISIONAL`, `APPENDED_WITH_PARENT_IMMUTABLE`, and `INDUCTED`.

This means a `HOLD_C1` or `NOT_REVIEWED` disposition does not erase the submitted artifact. It does not, however, prove that every preserved artifact is linked correctly into every downstream registry.

## Reconciliation finding

The current queue/registry surfaces are not fully synchronized:

- 4 global queue entries lack a linked canonical registry entry.
- 1 canonical induction registry entry lacks a matching queue ID.
- The live DB runtime reports a stale snapshot relative to the worktree.

This is the highest-priority baseline defect because the governing rule requires both queue and canonical-record linkage before active governed work.

## Induction and review coupling

Review is downstream of preservation, and the records preserve review status independently from promotion status. The current schema visibly supports deferred or held work. Explicit terminal semantics for failed review and a complete induction-specific supersession ledger are not evident in the audited surfaces.

## Projection completeness

Projection completeness is not established. Exact term-name matching between the 261-entry gap queue and the 1,085-term canonical lexicon produces many mismatches, but that comparison is not itself decisive because aliases, derived shorthand, and resolution mappings are allowed. A governed queue-to-canonical/alias reconciliation manifest is not evident in this audit scope.

## Baseline findings

1. First-contact preservation is explicitly governed and evidenced.
2. The intended multi-surface lifecycle is clear.
3. Queue-to-registry synchronization is incomplete.
4. Preservation is separated from review and promotion, but failed-review and supersession survival rules are not fully observable.
5. Downstream projection completeness cannot be certified from current records alone.
6. The DB runtime is stale and must not be treated as a fresh baseline projection.

## What this audit does not authorize

No governance modification, original-summary induction, scientific-content induction, promotion, queue closure, DB refresh, or registry mutation was performed or authorized by this report.

Machine-readable evidence: [governance_baseline_audit_pre_modification_20260801_001.json](/D:/projects/acellorator/departments/analysis/crawl_reports/governance_baseline_audit_pre_modification_20260801_001.json)
