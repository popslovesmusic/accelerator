# Analysis Crawl — Notebook 25/26 Clean-Room Frontier

## Campaign purpose

Run an incremental, bounded, read-only crawl of the new Notebook 25 adversarial-oracle result, Notebook 26 reference-stand-in results, and the clean-room oracle self-test.

## Scope and source artifact set

The crawl read the Analysis Department rules and SSOT; live D-semantics, archive, debt, and exclusion registries; the three recoverable result manifests/reviews; the clean-room self-test report; and the complete textbook for freshness comparison. Notebook 23 remained excluded frozen provenance and was not used as evidence.

## Directly observed/defined

- Notebook 25 processed 54 baselines across 11 adversarial families, 1,296 evaluations, and 270 invariant checks. It reported zero oracle disagreements, invariant failures, falsification flags, and replay divergence. Its evidence class and ceiling remain C2 bounded output.
- Notebook 26 reference-harness processing covered 128 baselines, 16 fault families, 4,352 evaluations, and 768 invariant checks. The self-contained variant covered 25 fault families, 6,656 evaluations, and 2,816 invariant checks. Both used a `REFERENCE_STANDIN`, not the governed frozen candidate.
- The clean-room implementation self-test reported 5 passed Python tests and successful Lean compilation. It did not perform candidate comparison or formal equivalence.
- Live inventory is 17 archive records, 56 induction-queue entries, 236 lexicon-gap entries, and 17 research-debt records; one low-severity Analysis Intake discoverability debt remains open.

## Inferred inside framework

Notebook 25 adds bounded adversarial consistency evidence for the frozen predicate behavior. Notebook 26 validates harness, corpus, replay, and artifact paths only. The clean-room self-test supports implementation health only. None of these observations closes universal D/E semantics or theorem obligations.

## Major discoveries

1. `INVARIANT_CANDIDATE` — Notebook 25’s finite adversarial consistency result; `PARTIALLY_SUPPORTED`, proof `NOT_ATTEMPTED`, C2 ceiling.
2. `MISSING_MECHANISM` — Notebook 26 lacks the exact governed candidate adapter and provenance required for an authoritative comparison; `OBSERVED`, proof `NOT_ATTEMPTED`, C1 ceiling.

## What was not learned

The crawl did not establish candidate/oracle equivalence, formal equivalence, universal D/E correctness, injectivity, reversibility, theorem closure, C5/C6 status, or external physical validity. Zero counterexamples in the declared finite domains do not establish absence of counterexamples outside those domains.

## Open debt, blockers, and falsification

- The D registry remains `ACTIVE_OPEN` with `C1_DEFINED_PROVISIONAL` ceiling, although its five obligation entries carry bounded statuses.
- The research-debt entry still blocks theorem promotion and the Pi_D preservation claim.
- Notebook 26 requires an exact candidate adapter, candidate identity/hash, provenance, and clean-room review.
- Notebook 25 retains a generated-spec metadata limitation and an internal-oracle limitation.
- The textbook contains Notebook 25 coverage but no visible Notebook 26 coverage. This is a freshness mismatch, not a permission to patch during crawl.
- Analysis Intake discoverability debt remains open and requires source binding without treating queued entries as reviewed or promoted.

## Recommended next action

`FORMALIZE`: obtain authorized candidate provenance and formalize the comparison/equivalence obligations, followed by bounded adversarial review. Preserve the current C1/C2 ceilings.

## Outcome and authorization boundary

`PARTIAL_SUCCESS` with high confidence for the bounded classification. Only noncanonical crawl reports were written. No registry, textbook, claim, lexicon, obligation, DB artifact, or execution state was changed. The crawl authorizes no promotion, execution, or commit.

- [Machine-readable report](D:/projects/acellorator/departments/analysis/crawl_reports/analysis_crawl_20260731_notebook25_26_cleanroom_frontier_001.json)
