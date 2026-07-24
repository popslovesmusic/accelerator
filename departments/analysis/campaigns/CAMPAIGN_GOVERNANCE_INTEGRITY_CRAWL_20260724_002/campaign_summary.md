# Campaign Summary: Governance Integrity Crawl

## Campaign Purpose
Analyze and document the repository's governance integrity and database snapshot freshness status following the commit `1aee6f842`, which introduced rules for the `crawl` approval gate in `AGENTS.md` and `GEMINI.md` without registering the updated file hashes or refreshing the SQLite database index.

## Scope
This campaign inspected the active commit `1aee6f842`, the modified governance files (`AGENTS.md`, `GEMINI.md`, `departments/analysis/AGENTS.md`, and `departments/analysis/GEMINI.md`), the baseline hash registry (`registry/governance_hash_registry.json`), the live SQLite index freshness capsule, and the global validation script execution log.

## Objects Analyzed
Eighteen objects were analyzed, including the core repository governance contracts, the department layout manifests, the database snapshot, and the global validation stages.

## What Was Learned
- The commit `1aee6f842` modified critical governance files without updating their baseline hashes.
- As a result, the `governance_integrity_validation` stage of `global_validate.py` fails with status `FAIL_SEMANTIC`.
- The SQLite database snapshot is stale because the worktree change timestamp is newer than the database snapshot refresh marker.
- The proof obligation `OBL-D-001C` (typed transition preservation) has been successfully discharged within type-level boundaries in commit `00489ef56`.
- The next active proof obligation in the D-semantics critical path is `OBL-D-001D` (representable distinction preservation).

## What Was Not Learned
No new theorems or proofs were derived. No canonical registries were mutated.

## Major Discoveries
- The repository is in a blocked state for automated claims or promotions due to the failing governance integrity checks.
- Modifying governance assets without matching updates in the hash registry or change ledger immediately triggers semantic failures in the global validation suite.

## Proof Progress
The proof obligations `OBL-D-001A` (Eval_D domain and codomain), `OBL-D-001B` (Context threshold), and `OBL-D-001C` (Typed transition preservation) are discharged. Obligations `OBL-D-001D` (Representable distinction preservation) and `OBL-D-001E` (Non-collapse boundary) remain open.

## New Contradictions
One contradiction was identified: a mismatch between the modified governance files on disk and their registered hashes in `registry/governance_hash_registry.json`.

## Open Research Debt
- `DEBT_D_SEMANTICS_PROOF_001` remains open with blockers `OBL-D-001D` and `OBL-D-001E`.
- A temporary maintenance debt exists to restore repository global health validation.

## Campaign Assessment
`BLOCKED` due to failing repository-level validation. Confidence is high.

## Recommended Next Campaign
Execute `CAMPAIGN_GOVERNANCE_HASH_REPAIR_20260724_001` to re-baseline the governance hashes and refresh the SQLite database snapshot, followed by routing the `OBL-D-001D` semantic preservation review.

## Reason Campaign Stopped
The governance defect and blocking conditions are fully mapped. Further crawl depth would duplicate findings without resolving the validation block.

**Executive recommendation:** `FORMALIZE`
