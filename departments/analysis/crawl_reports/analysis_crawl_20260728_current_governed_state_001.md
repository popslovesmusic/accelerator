# Analysis Crawl: Current Governed State

## Scope

Bounded read-only reconciliation of the artifact-indexer repair, ValidRelToken_C closeout, D-semantics obligations, runtime governance, and current validation evidence.

## Directly observed/defined

- The artifact-indexer self-database exclusion patch has four passing focused tests.
- The full indexer passed and skipped the active database, direct sidecars, and a same-file hardlink alias.
- The ValidRelToken_C artifact is indexed with its expected checksum.
- DB freshness and runtime governance pass.
- The ValidRelToken_C patch gate remains blocked because predecessor lifecycle evidence is not satisfied.
- OBL-D-001D and OBL-D-001E remain open; the claim ceiling remains `C1_DEFINED_PROVISIONAL`.
- The patch evidence records a `db_validation` failure for supersession-edge integrity. The checked-in global report is older and reports a different warning state; this discrepancy remains unresolved.

## Inferred inside framework

The infrastructure defect is operationally addressed, but indexing success is independent of semantic validity, predecessor completion, preservation, non-collapse, or D obligation discharge. The current critical path is governance reconciliation and fresh validation, not witness extension.

## External resemblance (Analogy only)

None asserted.

## What it does NOT prove

This crawl does not prove ValidRelToken_C transport, target interpretation, semantic preservation, injectivity, non-collapse, theorem closure, or external physical validity. It does not authorize a commit or the next D path step.

## Failure modes / uncertainty

- Predecessor patch lifecycle state remains inconsistent with the ValidRelToken_C dependency requirements.
- Supersession-edge integrity has a recorded failure in the closeout evidence.
- The current global report and later closeout evidence are not temporally aligned.
- The working tree contains task artifacts and an additional untracked notebook; this crawl did not classify ownership or mutate them.

## Recommended next action

Stop until governed predecessor-lifecycle evidence and a fresh clean `db_validation` result are available. Then rerun the patch gate for human review. This recommendation is analysis-only and authorizes no mutation, promotion, discharge, witness extension, or commit.
