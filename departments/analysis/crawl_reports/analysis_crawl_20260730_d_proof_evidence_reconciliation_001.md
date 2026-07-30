# Analysis Crawl — D Proof-Evidence Reconciliation — 2026-07-30

## Scope

Bounded, read-only reconciliation of P127/P128 proof candidates, their finite checks, canonical D-obligation status, registry synchronization, validation health, DB freshness, and textbook freshness.

## Directly observed / defined

- P127 and P128 are registered in the unified mathematical manifest and linked from the D-obligation registry.
- The proof-candidate checker passes 6/6 finite cases.
- OBL-D-001D and OBL-D-001E remain `OPEN` with human review pending.
- DB snapshot is fresh and the textbook projection freshness check passes.
- Global validation is warning-level with no failed stages; hygiene, math-program, and report-write stages remain degraded.

## Inferred inside framework

The artifacts provide stronger, explicit conditional derivations and boundary checks. They support C1 bounded reasoning only; they do not constitute accepted discharge certificates.

## External resemblance (Analogy only)

None asserted.

## What it does not prove

This crawl does not prove universal preservation, non-collapse for all domains, injectivity, reversibility, normalization, physical validity, or theorem closure. It does not authorize status promotion.

## Failure modes / uncertainty

The derivations depend on declared premises and finite checks. Human/formal acceptance has not yet been recorded. Validation warnings remain unresolved.

## Findings and next action

The outcome is `PARTIAL_SUCCESS`. The next action is `HUMAN_REVIEW_P127_P128`: independently review the premises, derivation scope, and falsification vectors before changing either obligation’s status.

## Required deliverables

- [Machine-readable report](D:/projects/acellorator/departments/analysis/crawl_reports/analysis_crawl_20260730_d_proof_evidence_reconciliation_001.json)
