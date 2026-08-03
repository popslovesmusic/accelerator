# Analysis Crawl: Governed State Reconciliation

## Campaign Purpose

Reconcile the current induction queue, formal-obligation registry, Analysis projections, validation reports, and runtime freshness signals after the incremental validation work and the latest MTO/OTM induction.

## Scope

This was a bounded, read-only crawl of governance, Analysis, induction, formal-obligation, and validation surfaces. It did not modify canonical files, refresh the database, execute work items, or promote claims.

## Objects Analyzed

- 15 Analysis Intake queue entries.
- The D-semantics obligation registry.
- Analysis program-state, dependency, and recommendation projections.
- Global health and diff-validation reports.
- The latest MTO/OTM calculus induction.
- Runtime current-state and freshness warnings.

## What Was Learned

The current queue contains 15 inducted entries. `RT_INDUCTION_MTO_OTM_CALCULUS_001` is research-registered, preserved literally, not reviewed, held at `C1`, and remains a noncanonical candidate. One existing intake item remains visibly blocked because its source payload is partial.

The canonical D-semantics registry reports `OBL-D-001A` through `OBL-D-001E` as discharged or discharged-bounded. Older Analysis projections still describe the C/D/E frontier as open. This is a projection-drift contradiction, not evidence that either source is mathematically false.

The diff validator passes and now caches unchanged stage results. Its current optimization is stage-scoped; it does not yet prove safe per-item reuse inside a selected validator stage.

## What Was Not Learned

The crawl did not establish the truth of the MTO/OTM calculus, prove identity-destructive closure, validate aspect equivalence, or establish an executable orientation-resolution algorithm. It also did not resolve the runtime freshness warning, which reports a source-marker discrepancy despite a successful snapshot refresh.

## Major Discoveries

1. `CONTRADICTION`: canonical D status and Analysis projection are not synchronized.
2. `RESEARCH_CAMPAIGN`: the MTO/OTM proposal is registered and discoverable but remains provisional and unreviewed.
3. `GOVERNANCE_DEFECT`: incremental validation has a defined stage-cache boundary, while item-level cache contracts remain unspecified.

## Proof Progress

No new proof obligation was discharged. The MTO/OTM proposal carries obligations for formal semantics, admissibility, deterministic orientation resolution, identity-destructive closure, and executable reduction.

## New Contradictions and Blockers

- D-semantics status drift between the canonical obligation registry and older Analysis projections.
- Runtime query reports stale DB snapshot status relative to the source worktree, although the latest snapshot command reported success.
- `RT_ASYM_SYMBOL_TYPE_RECONCILIATION_20260728_001` remains visibly blocked by `PARTIAL_SOURCE_PAYLOAD`.

## Open Research Debt

The highest-value immediate debt is projection reconciliation: determine whether the older Analysis D-status text is superseded, intentionally historical, or incorrectly current, and record the result through an authorized maintenance task. The MTO/OTM proposal should then receive a separate bounded formalization campaign; its induction status does not authorize canonical adoption.

## Campaign Assessment

`PARTIAL_SUCCESS`, with high support for the observed inventory and moderate support for the projection-drift classification. The crawl reduced uncertainty by separating canonical current status from stale projections, but it did not mutate or repair either surface.

## Recommended Next Campaign

Run a bounded projection-reconciliation campaign for the D-semantics status conflict. Inputs should include the canonical D registry, Analysis SSOT/projections, supersession records, and freshness contracts. The stopping condition is a documented classification of each conflicting projection as current, superseded, historical, or blocked pending authority.

## Reason Campaign Stopped

The declared current-state scope was covered. Additional crawl depth would repeat inventory work without the authorized projection-reconciliation action or new formal evidence.

## Support, Limits, and Authorization Boundary

Observed queue and registry facts are repository-local evidence. Cross-surface drift is a bounded repository comparison. No finding authorizes registry mutation, projection repair, database refresh, proof discharge, theorem promotion, MTO/OTM review, or external physical interpretation.
