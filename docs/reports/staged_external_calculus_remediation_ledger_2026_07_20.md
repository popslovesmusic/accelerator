# Staged External Calculus Audit Remediation Ledger

**Ledger ID:** `SEA-CALC-REMED-2026-07-20-001`  
**Date:** 2026-07-20  
**Scope:** factual review of `SEA-CALC-F001` through `SEA-CALC-F014`, bounded remediation, and post-repair external-audit rerun.  
**Mode:** governed maintenance and documentation audit.  
**Local governance:** root `AGENTS.md`, local `GEMINI.md`, `docs/AGENTS.md`, and `registry/AGENTS.md` were found and applied.  
**DB gate:** queried before edits. The new report path was not covered by the authority catalog, so the runtime returned `defer`; fallback to canonical registries and long-form governance was used.  
**Claim boundary:** this ledger records repository consistency only. It does not promote theorem, claim, lexicon, or empirical status.

## 1. Scope

This ledger audits each finding in `docs/reports/staged_external_calculus_registry_audit_2026_07_20.md` for factual correctness against the current working tree, classifies it, records whether it was remediated in this pass, and reruns the staged external audit against the repaired repository.

Because the repository was already heavily dirty, this pass does not treat the worktree as a clean release artifact. Repairs were limited to documentation statements whose correction does not require theorem promotion, registry renaming, or authority restructuring.

## 2. Directly Observed or Defined

- The DB governance runtime deferred authority for this new ledger path and continued to warn that no modified or untracked files were detected, despite Git reporting many modified or untracked paths.
- The math narrative contained unsupported escalation language (`This proves`, `grammar is universal`), stale counts, and unbounded gravity projection language.
- The textbook Appendix G source table treated `docs/MPF_Core_Formalism_v1.md` as an authorized SSOT and repeated Singularity Rebound as `C5/L3`.
- `docs/MPF_Core_Formalism_v1.md` described MT-001 through MT-005 as C6 symbolic trace closure while the active T005 theorem file describes T005 as a conditional operational lemma.
- The active charter requires 100 seeds for L3 and caps L3 at C4; C5-capable L4 requires 200 seeds and two independent mechanisms. The Singularity Rebound paper records 50 seeds and one model class.
- The root formal-object registry uses `dependency_links`; under that schema, unresolved links remain for `MT-RTN-001`, `MT-TZR-001`, `MT-RTM-001`, and `OBJ-S-PRUNED-CANDIDATE-SET`.

## 3. Finding Classification

| Finding | Classification | Factual audit result | Remediation disposition |
|---|---|---|---|
| `SEA-CALC-F001` | Accepted with qualification | Confirmed: root governance, textbook, core formalism, and validator surfaces use divergent root/operator serializations. Qualification: some variants may be intentional semantic refinements, but no machine-readable equivalence or precedence rule was found. | Not closed. Requires authority-level canonicalization and validator redesign. |
| `SEA-CALC-F002` | Accepted with qualification | Confirmed: the four named execution-authority laws do not share one object/status surface. Qualification: root governance may define them as governing assumptions rather than equal evidence-ranked theorem records. | Not closed. Requires explicit law-role versus evidence-status records. |
| `SEA-CALC-F003` | Accepted | Confirmed: `C*` labels are overloaded across claim policy, rigor charter, theorem taxonomy, textbook prose, and math theorem status. | Not closed. Requires namespacing and conversion policy. |
| `SEA-CALC-F004` | Accepted | Confirmed: the core formalism's MT-001 through MT-005 closure language conflicts with T005's current conditional status and incomplete routed object-status coverage. | Partially remediated by qualifying `docs/MPF_Core_Formalism_v1.md`; registry routing remains open. |
| `SEA-CALC-F005` | Accepted with qualification | Confirmed in principle: the documented `registry/math_registry.json` contract is stale, and sync targets are confusing. Qualification: current manifest searches now show L100 and P_GEO_001 present in `registry/governance_manifest.json`, so the exact missing-file examples are no longer current evidence. | Not closed. Requires sync-contract decision and generated coverage check. |
| `SEA-CALC-F006` | Accepted | Confirmed: public-facing narrative/textbook language conflicted with active claim gates and review-lock surfaces. | Partially remediated by patching `MATH_PROGRAM_NARRATIVE.md` and Appendix G source rows in the textbook. |
| `SEA-CALC-F007` | Accepted | Confirmed: Singularity Rebound paper metadata overstates current charter-compatible rank given 50 seeds and one model class; lexicon validation remains lower. | Partially remediated by qualifying the textbook source table. The paper metadata itself remains archival/current-source conflict debt. |
| `SEA-CALC-F008` | Accepted | Confirmed: lexicon queue, validation registry, top-level validation records, and mirrors remain structurally inconsistent. | Not closed. Requires schema migration and mirror policy. |
| `SEA-CALC-F009` | Accepted | Confirmed after using the actual `dependency_links` schema field: unresolved dependency links remain in the root formal-object registry. | Not closed. Requires registry edit and dependency validator hardening. |
| `SEA-CALC-F010` | Accepted | Confirmed: live authority manifest routes the root theorem-status taxonomy and textbook, not the math object-level theorem status registry or core formalism as an independent current SSOT. | Not closed. Requires authority manifest/routing patch. |
| `SEA-CALC-F011` | Accepted | Confirmed: DB freshness/worktree inventory output still conflicts with Git status. | Not closed. Requires runtime dirty-worktree control test and reporting fix. |
| `SEA-CALC-F012` | Accepted with qualification | Confirmed: mirrors diverge for lexicon-related surfaces. Qualification: some mirrors may be generated or historical, but no current one-way projection rule was found. | Not closed. Requires mirror designation or retirement. |
| `SEA-CALC-F013` | Accepted | Confirmed: the passing validators cover narrower contracts than the governance claims needing assurance. | Not closed. Requires validator contract documentation and negative controls. |
| `SEA-CALC-F014` | Accepted with qualification | Confirmed: narrative counts were stale. Qualification: exact counts depend on whether templates, registries, symbolic traces, and non-directory proof artifacts are included. | Partially remediated by replacing fixed verified-count claims with current on-disk counts and registry-authority wording. |

No finding is classified as `Rejected with evidence`. No finding is merely `Governance preference`; each accepted item has a current-file or current-command basis, though several require qualification because the correct repair depends on authority policy.

## 4. Remediation Ledger

| Finding | Concrete change made in this pass | File(s) changed | Residual work |
|---|---|---|---|
| `SEA-CALC-F004` | Replaced source-local C6 closure wording with registry-gated status language and identified MT-005 as conditional under current theorem files. | `docs/MPF_Core_Formalism_v1.md` | Route core formalism authority and create a complete T001-T005 object-status surface. |
| `SEA-CALC-F006` | Rewrote narrative claim escalation into bounded model-relative language; rewrote gravity prose as review-locked projection hypothesis; qualified textbook source table. | `MATH_PROGRAM_NARRATIVE.md`; `docs/textbook/mono_process_textbook_complete.md` | Audit remaining textbook sections for all C5/C6 and review-lock inheritance conflicts. |
| `SEA-CALC-F007` | Replaced textbook `C5/L3` Singularity Rebound row with legacy-metadata versus active-validation wording. | `docs/textbook/mono_process_textbook_complete.md` | Decide whether to patch archival paper metadata or add a governed waiver/status overlay. |
| `SEA-CALC-F014` | Replaced stale verified lemma/proof counts with observed on-disk counts and registry-authority caveat. | `MATH_PROGRAM_NARRATIVE.md` | Add generated count tooling that reports on-disk, registered, and status-qualified counts separately. |

Accepted findings not listed above were not repaired because the concrete fix would require authority-bearing registry changes, validator redesign, schema migration, or theorem-status decisions beyond a safe documentation repair.

## 5. Framework-Internal Inference

The factual review supports the original audit's core diagnosis: the primary risk is authority and status non-convergence, not absence of material. After this pass, several public-facing documentation conflicts are reduced, but the repository still cannot receive an unqualified external audit attestation.

Current internal disposition after repair:

> **CONDITIONAL FAIL, IMPROVED** - documentation escalation was reduced, but authority routing, status namespaces, lexicon lifecycle, validator scope, dirty-worktree freshness, and formal-object dependency closure remain unresolved.

## 6. External Resemblance - Analogy Only

The remediation process resembles a configuration-control disposition ledger: findings are accepted, qualified, rejected, or classified as preference; accepted findings map to work items; residual risks remain visible. This is an analogy only and does not imply standards certification or independent mathematical review.

## 7. What This Does Not Prove

This remediation ledger does not prove mathematical completeness, physical validity, or external correctness of the Calculus. It also does not prove that every notation variant is semantically wrong. It records only the current repository consistency state and the bounded repairs made in this pass.

## 8. Failure Modes and Uncertainty

- The worktree remains dirty, so this is not a release attestation.
- Some observed conflicts may be mid-repair in user-owned uncommitted files.
- This pass did not rewrite authority-bearing registries except through observation; unresolved registry repairs need explicit policy decisions and validator updates.
- Counts are current observations from the working tree, not durable generated metrics.
- Encoding corruption remains on some surfaces and can affect exact string matching.

## 9. Post-Repair External Audit Rerun

The staged external audit was rerun conceptually against the repaired repository state, using the same stage gates:

| Stage | Post-repair result | Reason |
|---|---|---|
| Stage 0 - Evidence freeze | Fail | Dirty worktree remains and DB freshness still misreports worktree inventory relative to Git. |
| Stage 1 - Authority graph | Fail | Core formalism and object-level math theorem status routing remain unresolved. |
| Stage 2 - Structural integrity | Fail | Lexicon mirrors/schema and formal-object dependency closure remain unresolved. |
| Stage 3 - Calculus semantic crosswalk | Fail | Root expression/operator serialization has not been machine-canonicalized. |
| Stage 4 - Theorem/claim/evidence gates | Fail | Status namespace overload and foundational-law status reconciliation remain unresolved. |
| Stage 5 - Validator adequacy | Fail | Negative controls and cross-authority semantic validators are not yet present. |
| Stage 6 - Final attestation | Fail | Critical findings remain open, though documentation escalation is partially repaired. |

Final rerun disposition:

> **NO UNQUALIFIED EXTERNAL ATTESTATION.** The repository is better aligned in current prose, but it still requires authority-routing, registry, and validator repairs before the external audit can pass.

## 10. Validation and Textbook Synchronization Record

Textbook synchronization was performed for the directly linked Appendix G rows affected by this remediation. Remaining textbook mismatches are explicitly carried as residual debt rather than silently patched because they depend on authority routing and registry decisions.

Validation commands run after repair:

| Command | Result |
|---|---|
| `python scripts/validation/validate_core_expression_presence.py` | Pass |
| `python scripts/math/validate_formal_objects.py` | Pass in declared scope: 56 classes, 24 operators, 3 relations |
| `python scripts/db/check_registry_alignment.py` | Pass |
| `python scripts/math/validate_quantifier_explicitness.py` | Pass |
| `python scripts/governance/enforce_governance_integrity.py` | Pass; approved-bypass warnings only |
| `python scripts/global_validate.py` | Exit 0; run `GV-20260720T225821.009839-11724`; overall `warning`; no failed stages; degraded stages `hygiene_validation` and `math_program_validation`; clean-pass eligibility false |

Claim-humility review was performed on this ledger and the patched prose. Unsupported external truth language was not introduced.
