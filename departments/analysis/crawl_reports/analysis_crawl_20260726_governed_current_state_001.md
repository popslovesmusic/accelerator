# Analysis Crawl: Governed Current-State Synthesis

## Campaign Purpose

Perform a bounded, read-only current-state crawl across governance, research debt, D-semantics obligations, lexicon gaps, intake preservation, validation health, and recent Analysis outputs.

## Scope and source artifact set

The crawl read the local Analysis rules/SSOT, governance runtime current-state output, global health report, D-semantics obligation registry, research-debt registry, lexicon gap and validation registries, master work index, Analysis recommendation/dependency/state reports, Analysis Intake queue, recent crawl reports, and textbook/governance freshness references where present.

## Directly observed/defined

- The governance runtime returned `warn`; its DB snapshot is stale, with no open runtime debt or runtime blockers in the projection.
- The canonical D registry contains five obligations: A discharged, B discharged-bounded, C discharged-bounded, D open, and E open.
- The lexicon gap queue contains 234 entries: 98 resolved to canonical, 125 provisional C1-defined, and 11 `GAP_OPEN`.
- The Analysis Intake queue preserves eight entries; captured proposals remain review- or promotion-gated rather than executable.
- Global validation is `warning`, with no failed stages, no semantic failures, and two degraded stages; hygiene and math-program warnings remain relevant.
- The master work index contains 91 records and reports zero items needing mapping, but its source-level statuses still include active, provisional, and review states.

## Inferred inside framework

The current state is a split projection: the runtime summarizes no open debt while canonical registries preserve open D-semantics and lexicon obligations. This is a synchronization/freshness boundary, not evidence that the obligations are discharged. Within the Analysis Department interpretation, the highest-value next action is to formalize and review the two open D obligations while separately resolving the 11 exact lexicon gaps.

## Findings by discovery class

1. `GOVERNANCE_DEFECT`: stale DB snapshot prevents freshness-clean closeout and can conceal divergence between runtime projection and canonical registries. Status `OBSERVED`; proof `NOT_ATTEMPTED`.
2. `PROOF_OBLIGATION`: `OBL-D-001D` and `OBL-D-001E` remain open. Status `SOURCE_REPORTED`; proof `BLOCKED` pending authorized evidence.
3. `PROOF_GAP`: 11 lexicon entries remain `GAP_OPEN`; induction/provisional classification is not validation or promotion. Status `OBSERVED`; proof `OBLIGATIONS_IDENTIFIED`.
4. `RESEARCH_CAMPAIGN`: a bounded successor should formalize D/E acceptance tests and produce a separate lexicon review package. Status `CONJECTURED`; proof `NOT_ATTEMPTED`.

## What was not learned

The crawl did not discharge a proof obligation, validate or promote a lexicon term, establish an external or physical correspondence, re-run simulations, refresh the DB, or adjudicate the correctness of the canonical scope itself.

## Open research debt and blockers

- `OBL-D-001D` and `OBL-D-001E` remain open.
- Eleven exact lexicon gaps remain unvalidated.
- DB snapshot freshness is `stale`; this is a closeout blocker for governed tasks requiring DB-indexed authority.
- Existing worktree modifications are unrelated and prevent an isolated task commit; crawl reports are the only permitted writes here.

## Recommended next action

`FORMALIZE`: prepare one authorized D-semantics obligation package with measurable acceptance tests for D/E, then run the required validation and DB refresh. In parallel, review the 11 `GAP_OPEN` terms without promotion.

## Campaign Assessment

`PARTIAL_SUCCESS`, high support for observed inventory and moderate support for the synchronization inference. The crawl reduced uncertainty by separating runtime projection from canonical obligations but discharged no debt.

## What this crawl does not authorize

No registry mutation, DB indexing or refresh, lexicon validation/promotion, proof discharge, execution, claim elevation, textbook patch, or external-reality claim is authorized.

## Reason Campaign Stopped

The finite current-state scope was covered; further progress requires new formal evidence, a separately authorized maintenance action, or a DB snapshot refresh.
