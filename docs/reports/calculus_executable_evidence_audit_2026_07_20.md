# Calculus Executable Evidence Audit

**Audit packet:** `SEA_CALC_EXECUTABLE_EVIDENCE_AUDIT_2026_07_20`  
**Date:** 2026-07-20  
**Mode:** controlled adversarial audit  
**Final attestation:** `FAIL`  
**Machine report:** `outputs/audits/calculus_executable_evidence_audit_2026_07_20.json`  
**Evidence directory:** `outputs/evidence/executable_authority_audit_2026_07_20/`  
**Finding ledger:** `registry/governance/executable_evidence_audit_finding_ledger.json`

## Audit Baseline

The audit captured repository commit, Git status, Python version, operating system, database hash, schema hash, authority architecture hash, runtime policy hash, and DB summary in `outputs/evidence/executable_authority_audit_2026_07_20/baseline_manifest.json`.

This audit does not establish mathematical truth, physical truth, theorem promotion, claim promotion, lexicon promotion, proof completeness, or external scientific validation.

## Environment and Isolation

The audit used the current repository and production governance query path. No theorem, lemma, law, claim, lexicon, proof, evidence class, or canonical DB row was promoted or demoted.

Isolation was partial. The audit did not create mutating fixtures, did not open database transactions, and did not create a temporary database clone. Because no clean disposable worktree fixture was created, clean-worktree and ignored-file boundary controls are recorded as `INCONCLUSIVE`.

Cleanup evidence is recorded in `outputs/evidence/executable_authority_audit_2026_07_20/cleanup_report.json`.

## Validator Inventory

The declared test plan contained 33 tests across seven validator families:

| Validator | Result |
|---|---|
| `VAL-WORKTREE-EVIDENCE-001` | Executed against the real Git and governance freshness/context paths; 2 failed and 2 were inconclusive |
| `VAL-AUTH-PIPELINE-001` | `NOT_IMPLEMENTED` |
| `VAL-RUNTIME-AUTH-001` | `NOT_IMPLEMENTED` |
| `VAL-PROJECTION-TRACE-001` | `NOT_IMPLEMENTED` |
| `VAL-PROJECTION-FRESHNESS-001` | `NOT_IMPLEMENTED` |
| `VAL-STATUS-NAMESPACE-001` | `NOT_IMPLEMENTED` |
| `VAL-CANONICAL-EXPRESSION-001` | `NOT_IMPLEMENTED` |

Result counts: 2 `FAIL`, 2 `INCONCLUSIVE`, 29 `NOT_IMPLEMENTED`.

## Positive Controls

`WTE-POS-001` was `INCONCLUSIVE` because a clean disposable worktree was not created. The remaining positive controls for admission, runtime authority, projection trace, projection freshness, status namespace, and canonical expression resolution are `NOT_IMPLEMENTED` because no executable production validator entry points were found.

## Negative Controls

Two worktree evidence negative controls failed:

- `WTE-NEG-001`: expected tracked-file dirtiness to be reported by both Git and runtime freshness. Git reported a dirty worktree; runtime freshness/context reported `runtime_reports_dirty: false`.
- `WTE-NEG-002`: expected untracked-file dirtiness to be reported by both Git and runtime freshness. Git reported untracked state; runtime freshness/context reported `runtime_reports_dirty: false`.

Evidence bundles:

- `outputs/evidence/executable_authority_audit_2026_07_20/bundles/WTE-NEG-001.json`
- `outputs/evidence/executable_authority_audit_2026_07_20/bundles/WTE-NEG-002.json`

All non-worktree negative controls are `NOT_IMPLEMENTED`.

## Boundary Controls

`WTE-BND-001` was `INCONCLUSIVE` because the ignored-file-only fixture was not created. All other boundary controls are `NOT_IMPLEMENTED`.

## Observed Results

The real governance freshness/context path did not satisfy the declared worktree evidence invariant. The observed failure is concrete:

```json
{
  "git_dirty": true,
  "runtime_reports_dirty": false,
  "runtime_no_dirty_warning": true,
  "source_change_count": 0,
  "runtime_only_change_count": 0
}
```

This is a critical executable failure for worktree evidence accuracy. It confirms that policy and schema records are not enough to attest the directional authority pipeline.

## Failures and Inconclusive Results

The final result is `FAIL`, not merely `CONDITIONAL_FAIL`, because a critical control failed: worktree freshness reports clean/no modified-or-untracked state under the declared runtime path while Git reports dirty state.

The missing validator families remain separate implementation gaps:

- admission traceability
- runtime authority exclusion
- projection traceability
- projection freshness
- status namespace enforcement
- canonical expression semantic resolution

## Canonical-State Non-Contamination

No mutating audit fixtures were created. The cleanup report records `canonical_math_state_changed_by_audit: false`. The audit created evidence, report, and finding-ledger artifacts only.

## Assurance Boundaries

Passing JSON generation or report creation does not prove runtime enforcement. The only real executable control exercised in this pass was the current worktree/freshness path. Its negative controls failed.

All `NOT_IMPLEMENTED` results mean the repository currently lacks the executable mechanism needed for attestation; they must not be counted as pass, policy compliance, or implied enforcement.

## Residual Risks

- The audit did not execute clean disposable worktree or ignored-file fixtures.
- The audit did not use a temporary DB clone because no admission/runtime tests were available to run against it.
- Existing generated evidence reflects the current dirty worktree, not a clean release artifact.
- The DB remains useful as an index/projection layer, but this audit did not demonstrate complete canonical authority enforcement.

## Final Attestation

Final result: **FAIL**.

The declared architecture is testable, but executable evidence does not yet support the assertion that the real governance mechanisms enforce the full directional authority pipeline. The immediate repair target is `VAL-WORKTREE-EVIDENCE-001`, followed by implementation of admission, runtime authority, projection trace/freshness, status namespace, and canonical expression validators.
