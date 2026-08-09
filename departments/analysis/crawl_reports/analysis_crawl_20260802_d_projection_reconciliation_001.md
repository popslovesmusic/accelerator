# D Projection Reconciliation Crawl

## Campaign Purpose

Compare the canonical D-semantics obligation dispositions with the live research-debt record and Analysis projections, preserving the distinction between bounded support and theorem-promotion eligibility.

## Scope

This was a bounded, read-only crawl of the five D obligations, their upstream debt, the D promotion gate, Analysis Department projections, current validation, and current DB freshness. No canonical file was changed.

## Source Artifact Set

The crawl read `registry/math/d_semantics_obligation_registry.json`, both research-debt registries, `departments/analysis/department_ssot.md`, `program_state_report.json`, `dependency_report.json`, `recommended_action_queue.json`, the current global health report, the textbook freshness surface, and `scripts/query_governance.py`. Exact SHA-256 values are recorded in the companion JSON report.

## Objects Analyzed

- `OBL-D-001A`: `DISCHARGED`
- `OBL-D-001B` through `OBL-D-001E`: `DISCHARGED_BOUNDED`
- D registry aggregate status: `ACTIVE_OPEN`
- Live research-debt status: `resolved`
- Promotion gate: theorem promotion and claims above C1 remain blocked

## What Was Learned

The canonical obligation records preserve bounded dispositions for all five obligations. The Analysis projections also preserve the C1 ceiling and theorem-promotion block. Current global validation passes with warnings, and the DB snapshot is fresh.

## What Was Not Learned

The crawl did not establish that `resolved`, `ACTIVE_OPEN`, `DISCHARGED_BOUNDED`, and “promotion blocked” are governed aliases with a complete machine-readable mapping. The intended lifecycle meaning of each aggregate status remains under-specified.

## Major Discovery

There is a status-vocabulary alignment defect: the live research-debt record calls the bounded package resolved while retaining active blockers and stating that no proof obligation was discharged; the D registry calls the aggregate active/open while marking each obligation discharged or discharged-bounded. This is a projection/lifecycle distinction, not evidence that the bounded records should be erased or that promotion is allowed.

Support level: `C3_REPOSITORY_COMPARISON`.

Epistemic status: `OBSERVED`.

Proof status: `NOT_ATTEMPTED`.

## Proof Progress

No proof was attempted or discharged. The theorem-promotion gate remains blocked.

## New Contradictions

`CONTRADICTION_D_STATUS_VOCABULARY_001`: aggregate status terms differ across authority projections while the same promotion blockers remain active.

## Open Research Debt

The remaining work is a status-mapping review: define whether aggregate “resolved” means bounded research-debt disposition, while `ACTIVE_OPEN` denotes an unresolved promotion gate, and make that distinction explicit across projections.

## Campaign Assessment

Outcome: `PARTIAL_SUCCESS`.

The crawl sharply bounded the apparent conflict and found no canonical mathematical delta. Confidence is high for the observed fields and moderate for their intended lifecycle semantics.

## Recommended Next Campaign

1. Conduct a separately authorized status-mapping/projection-alignment review.
2. Then run the previously identified finite MTO/OTM fixture evaluator for role typing, deterministic MTO selection, and OTM multiplicity preservation.

## Reason Campaign Stopped

The declared comparison scope is complete. Further progress requires human review or an authorized projection repair; crawl mode does not authorize either.

## What This Crawl Does Not Authorize

It does not authorize registry mutation, Analysis SSOT repair, proof discharge, theorem promotion, claim elevation, MTO/OTM fixture execution, or external physical interpretation.
