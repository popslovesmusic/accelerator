# Staged External Audit of the Calculus Registries and Governance

**Audit ID:** `SEA-CALC-2026-07-20-001`  
**Date:** 2026-07-20  
**Mode:** governed documentation audit; no registry promotion or mathematical repair  
**Repository baseline:** commit `652ae015391c06cdd89d931e6efb796e902d65ce`, with 222 modified or untracked status lines observed before this report was added  
**Primary scope:** Calculus of Distinction / RT calculus authority, mathematical registries, claim gates, lexicon state, proof/theorem status, hash and manifest coverage, and the validators used to represent those surfaces  
**Default evidence class:** `C1_model_relative` repository observation unless a row is explicitly marked `C0_definition`  
**Claim boundary:** this report evaluates internal repository consistency. It does not establish or refute external mathematical, physical, or ontological truth.

## 1. Executive Decision and Scope

The repository is **not yet ready for an unqualified external audit of the Calculus as a single governed formal system**. The appropriate current disposition is:

> **CONDITIONAL FAIL — authority and semantic reconciliation required before external audit attestation.**

This disposition does not mean that every formal artifact is invalid. Several scoped checks passed: the DB snapshot reported fresh, the selected formal-object typing validator passed, registered math-source paths resolved, DB registry alignment passed, the quantifier validator passed, and the governance integrity hash check passed. The blocking issue is that those checks do not resolve contradictory authority, status, claim-class, and registry-coverage surfaces.

This report therefore does two things:

1. defines a staged external-audit procedure that an independent reviewer can execute without silently selecting a preferred authority; and
2. records a repository-local pre-audit of the highest-risk Calculus surfaces.

No theorem, lemma, law, induction, term, evidence class, or claim status is promoted by this report.

## 2. Authority and Evidence Baseline

### 2.1 Authority order used

The audit applied the repository's declared authority separation:

1. `registry/compliance_charter_v2_3.json`;
2. `governance/live/governance_constitution.json`, root `AGENTS.md`, root `GEMINI.md`, and `governance/claim_policy.json`;
3. live ledgers listed by `governance/live/authority_manifest.json`;
4. global canonical registries listed by that manifest;
5. `docs/textbook/mono_process_textbook_complete.md` as the Mathematics Department design SSOT;
6. historical specifications and patch records as lineage evidence only.

The local `GEMINI.md` was found and applied. Its additional simulation-tool restriction did not trigger because no simulation was run.

### 2.2 DB governance gate

The DB-first gate was queried before this document was created.

- `context-capsule`: snapshot `fresh`; global runtime status `warn`; target authority `defer` because the new report path was not catalogued.
- `current-state`: `warn`, zero runtime blockers, zero projected open debt.
- `freshness`: `allow` and `fresh`.
- authority for the textbook: `allow`, current, conflict state clear.
- authority for `docs/MPF_Core_Formalism_v1.md`: `defer`, no matched governed authority surface.
- authority for both theorem-status registry paths: `defer` under the Q0 role-aware query.

Because the report target was not classified, the documented fallback to canonical registries and long-form governance was used.

### 2.3 Current evidence versus historical residue

| Surface | Audit treatment | Evidence class |
|---|---|---|
| Live DB query output | Current runtime observation, subject to the worktree-detection caveat in Finding 11 | `C1_model_relative` |
| Live governance and canonical registries | Current authority according to the authority manifest | `C1_model_relative` |
| Mathematics textbook | Current design intent, subordinate to higher-ranked governance and executable registry state | `C1_model_relative` |
| `docs/MPF_Core_Formalism_v1.md` | Textbook-cited source that self-identifies as SSOT, but is not independently routed by the live authority runtime | `C1_model_relative` |
| `registry/governance/patches/**` | Historical or proposed lineage; not current authority unless an applied live surface incorporates it | `C1_model_relative` |
| Existing untracked audit drafts in `docs/reports/` | Worktree context only; not treated as independent attestation | `C1_model_relative` |

## 3. Staged External-Audit Design

The external audit should be performed in seven stages. A stage fails closed when its exit gate is not met; later stages may still be explored, but no final attestation should be issued.

### Stage 0 — Evidence freeze and independence declaration

**Objective:** establish exactly what an external reviewer inspected.

Required actions:

- record commit, full worktree status, submodule state if any, filesystem timestamps, and hashes of all authority-bearing inputs;
- export the DB runtime snapshot and query outputs without refreshing or mutating them first;
- identify auditor identity, conflicts of interest, repository access level, and excluded surfaces;
- separate current authority, generated evidence, proposals, and historical residue.

Exit gate: an immutable evidence manifest exists and the dirty worktree is either frozen as the audit subject or replaced by an explicitly identified clean revision.

### Stage 1 — Authority graph and SSOT resolution

**Objective:** determine which artifact wins for every audited semantic and state question.

Required crosswalks:

- compliance charter -> constitution/policies -> live ledgers -> canonical registries -> department SSOT -> source documents;
- design authority versus execution authority;
- semantic authority versus status authority versus write authority;
- active versus proposed, superseded, mirrored, and historical paths.

Exit gate: every primary Calculus surface has one declared authority owner, one state owner, one write path, and an explicit supersession rule. `defer` is acceptable only with a documented fallback result.

### Stage 2 — Machine-readable structural integrity

**Objective:** test parseability and referential closure before interpreting mathematics.

Required checks:

- JSON/schema validity;
- duplicate IDs and duplicate semantic keys;
- broken source paths and dependency links;
- mirror divergence;
- manifest coverage of all theorem, lemma, and proof files;
- hash coverage and hash freshness;
- registry-to-DB projection alignment.

Exit gate: zero unexplained duplicate authorities, zero broken required links, and 100% registered coverage for in-scope current mathematical artifacts.

### Stage 3 — Calculus semantic crosswalk

**Objective:** compare the same mathematical object across every authority surface.

Minimum objects:

- canonical root expression and operator subscript/notation variants;
- T001 / 3-Peak Rule;
- SING-001 / Singularity Rebound;
- L043 / Tertiary Node Structure;
- L045 / Topology-Geometry Biconditional;
- `RT_core`, `delta`, `delta_a`, `delta alpha`, `iff_R`, and `iff_x`;
- current primitive set and operator genealogy.

For each object, the auditor must record identifier, expression, scope, status, claim cap, dependencies, evidence, failure modes, and authoritative source.

Exit gate: no unresolved expression, identifier, primitive-role, or status conflict remains in the primary set.

### Stage 4 — Theorem, claim, and evidence gate audit

**Objective:** reconstruct every promotion from source evidence rather than accepting a label.

Required checks:

- theorem-status taxonomy versus object-level theorem state;
- C-level meaning, L-level rigor meaning, and TS-level theorem meaning;
- seed count, mechanism count, independent measurement count, falsification vectors, replication, and recoverable output paths;
- claim-registry and claim-support-matrix coverage;
- review-lock and downstream inheritance behavior.

Exit gate: every promoted label is derivable under one current policy, and no locked object is described elsewhere as currently supported at a higher level.

### Stage 5 — Validator adequacy and adversarial testing

**Objective:** determine what each passing validator actually guarantees.

Required attacks:

- mutate a canonical root variant in a controlled copy and verify detection;
- insert a missing or broken dependency and verify detection;
- move a lexicon record outside its schema container and verify detection;
- create mirror drift and verify detection;
- assign a theorem an unauthorized C-level and verify detection;
- test dirty-worktree freshness detection.

Exit gate: every critical governance invariant has a positive control, negative control, and explicit failure result.

### Stage 6 — Remediation verification and final attestation

**Objective:** close findings without using the remediation itself as proof of correctness.

Required actions:

- review each repair through the DB gate;
- rerun structural and semantic checks from the frozen test protocol;
- obtain a second independent reviewer for all critical closures;
- publish unresolved findings, waivers, and residual risk;
- synchronize the textbook after registry and policy authority is settled.

Exit gate: all critical findings are closed or explicitly waived by named authority, high findings have bounded remediation plans, and the final report distinguishes passed controls from unresolved scope.

## 4. What Was Directly Defined or Observed

The following are direct repository observations, not external conclusions:

- The live authority manifest lists `registry/theorem_status_registry.json` as a global canonical registry and the textbook as a department SSOT, but does not list `registry/math/theorem_status_registry.json` or `docs/MPF_Core_Formalism_v1.md`.
- The textbook calls `docs/MPF_Core_Formalism_v1.md` the authorized SSOT for primitives, the generative condition, and core operator algebra.
- Root instructions lock the canonical root expression to the residue-conditioned form, while the core-expression validator requires the generalized `_x` form to occur somewhere in the repository.
- The foundational math tree contains 201 non-template theorem/lemma/proof Markdown files: 130 lemmas, 66 proof artifacts, and 5 theorem files.
- The unified governance manifest registers 179 of those files: 125 lemmas, 49 proofs, and 5 theorems. Twenty-two in-scope files are absent from that manifest.
- The root formal-object registry contains 158 objects and ten unresolved/null dependency links under a same-registry closure check.
- The selected formal-object validator passed while inspecting the separate 56-class registry plus 24 operators and 3 relations.
- Root and mirrored lexicon queues contain 183 and 155 queue records respectively. Root and mirrored validation registries expose 108 and 103 entries under `terms`, and the root file additionally places 25 term-like records at top level.
- The DB runtime reported that no modified or untracked files were detected, while `git status --short` reported 222 lines before this report was added.

## 5. Registry-to-SSOT Findings

All findings below are `C1_model_relative` internal consistency observations.

| ID | Severity | Finding | Direct evidence | Required disposition |
|---|---|---|---|---|
| `SEA-CALC-F001` | Critical | **Canonical root expression is not machine-unified.** Root governance locks `(E != 0) iff_R delta(E > 0)`, the textbook uses residue-conditioned variants with `delta_a` and `delta alpha`, multiple math documents call `(E != 0) iff_x delta(E > 0)` generalized canonical, and the core-expression validator requires only the `_x` string. The semantic theorem registry also stores a mojibake-corrupted canonical expression. No machine-readable precedence/equivalence rule was found that makes these exact strings safely interchangeable. | `AGENTS.md:27`; textbook `:85`, `:145`; `scripts/validation/validate_core_expression_presence.py:17`; `registry/theorem_registry.json:12-18` | Select one canonical serialization, explicitly type permitted variants, repair encoding, and make validators compare governed equivalence rather than repository-wide presence. |
| `SEA-CALC-F002` | Critical | **The four execution-authority laws do not share a compatible current status.** T001's document says formally proven/C6; L043 says simulated; L045 says draft; exact `SING-001` is absent from the audited theorem-status, claim, and formal-object registries while `singularity_rebound` is only partially verified at L2 in the lexicon validation registry. These are all presented as co-equal foundational laws in root governance. | `AGENTS.md:20-23`; T001 `:46-50`; L043 status block; L045 status block; `registry/lexicon_validation_registry.json` term record | Create authority-level records for all four laws with explicit status/cap semantics, or narrow the instruction text to defined governance assumptions rather than evidentiary status claims. |
| `SEA-CALC-F003` | Critical | **C-level semantics collide.** The claim policy defines C5 as an external claim and blocks it by default; the charter defines an L0-L5 rigor ladder reaching C6; the global theorem-status taxonomy maps C6 to externally validated TS5; the textbook defines C6 as formal closure plus universal mechanism independence; the math theorem-status registry uses `C6_formal_closure`. These are not one coherent ordinal scale. | `governance/claim_policy.json:32-40`; charter `:737-822`; `registry/theorem_status_registry.json`; textbook `:3105`, `:3850`, `:4045`; math theorem-status `:740-795` | Namespace the systems, for example `CLAIM_C*`, `RIGOR_L*`, `THEOREM_TS*`, and `FORMAL_FC*`, with a governed conversion table and no overloaded bare `C6`. |
| `SEA-CALC-F004` | Critical | **Master-theorem status is contradictory and incompletely routed.** `docs/MPF_Core_Formalism_v1.md` says MT-001 through MT-005 have C6 symbolic closure, but T005's theorem file is a conditional operational lemma. The unified manifest marks T001-T004 formally proven and T005 conditional, while neither object-level theorem-status surface nor the root formal-object theorem inventory provides a complete T001-T005 status set. | Core formalism `:127-132`; T005 theorem status block; governance-manifest theorem nodes; root and math theorem-status registries | Establish a single object-status registry for T001-T005, bind it to the TS taxonomy, and remove C6 wording from any source that cannot reproduce the active promotion gate. |
| `SEA-CALC-F005` | High | **The math synchronization contract is stale and incomplete.** Root instructions require `registry/math_registry.json`, which does not exist. A proposed historical patch selects `registry/math_source_registry.json`, while `scripts/sync_math_registry.py` actually updates `registry/governance_manifest.json`. Its success message reports 179 registered artifacts but leaves 22 current non-template math files outside the manifest, including L100 and P_GEO_001. It does not update either math hash registry. | `AGENTS.md:39`; `PATCH_DB_GOVERNANCE_RUNTIME_012A`; sync script `:119`, `:175`; manifest/disk comparison | Apply or supersede the naming reconciliation, rename the sync command or change its target, enforce 100% artifact coverage, and define which hash registry covers source documents versus granular registries. |
| `SEA-CALC-F006` | High | **The textbook and narrative contain live claim/status conflicts.** The textbook describes `gravity_app` as a C5 projected observable at `:2852` and as `REVIEW_LOCK` at `:3359`. The math theorem-status registry confirms `REVIEW_LOCK` with zero evidence records. `MATH_PROGRAM_NARRATIVE.md` uses prohibited or unbounded wording including “This proves,” “the grammar is universal,” and identity/gravity formulations, despite its closing disclaimer. | Textbook `:2852`, `:3359`; math theorem-status `gravity_app`; narrative `:43`, `:55`, `:73`, `:85` | Preserve the lock, downgrade stale prose to scoped model-relative language, and attach recoverable evidence paths directly to every retained numerical observation. |
| `SEA-CALC-F007` | High | **Singularity Rebound is overclassified across surfaces.** Its paper reports one model class and 50 seeds but labels itself L3/C5. The active charter requires 100 seeds for L3, caps L3 at C4, and requires 200 seeds plus two independent mechanisms for the C5-capable L4 tier. The lexicon validator records only L2/partially verified, while the textbook source table repeats C5/L3. | Singularity paper metadata and Classification section; charter `:754-772`; lexicon validation term; textbook `:4475` | Reclassify under the active charter or document a formally authorized legacy-policy waiver; keep `SING-001` as a governed hypothesis/law assumption only if that role is explicitly separated from evidence rank. |
| `SEA-CALC-F008` | High | **Lexicon lifecycle and mirror state are internally inconsistent.** Singularity-related queue entries simultaneously say `RESOLVED_L2`, `default_claim_status: PROVISIONAL`, role evidence L0, and `governance_status: not_verified`, while the validation registry says L2. The root/mirror queues differ by 28 queue records, validation `terms` differ by 5, and 25 newer term-like validation records sit outside the `terms` container. | Root and mirrored lexicon registries; direct structured counts | Define one lifecycle state machine, migrate all validation entries under one schema container, and retire or automatically verify mirrors. |
| `SEA-CALC-F009` | High | **The root formal-object registry is not dependency-closed.** Four operator objects contain null dependency entries and six objects reference IDs absent from the same registry, including MT-RTN-001, MT-TZR-001, MT-RTM-001, and OBJ-S-PRUNED-CANDIDATE-SET. | Structured scan of `registry/formal_object_registry.json` | Declare cross-registry namespaces or replace links with canonical object IDs; block validation on null or unresolved required dependencies. |
| `SEA-CALC-F010` | High | **Authority routing omits live Calculus state surfaces.** The authority manifest routes the root theorem-status taxonomy but not the object-level math theorem-status registry. The textbook is runtime-recognized; the core formalism, despite being cited by the textbook as an authorized SSOT, is not. Role-aware DB queries defer both theorem-status paths as outside Q0. | `governance/live/authority_manifest.json:58-78`; DB authority queries | Add explicit semantic/state/write ownership for Calculus registries and classify the core formalism as current, superseded, or source-only. |
| `SEA-CALC-F011` | High | **Runtime freshness can misdescribe the audit worktree.** The DB reported a fresh snapshot and simultaneously warned that no modified/untracked files were detected, although Git reported 222 status lines. This undermines use of the runtime warning as an evidence-freeze assertion. | DB context/current-state/freshness output; `git status --short` count | Add a dirty-worktree control test and make freshness report the observed source of its worktree inventory. |
| `SEA-CALC-F012` | Medium | **Mirrored registries are not governed as projections.** The two governance manifests are byte-identical now, but lexicon and governance-hash mirrors differ. Historical patches explicitly required mirrored lexicon updates, so divergence is not clearly archival. | File hashes and structured root/mirror counts | Designate mirrors generated-only with one-way build rules, or remove them from live workflows after migration. |
| `SEA-CALC-F013` | High | **Passing validators provide narrower assurance than current reports imply.** The root-expression check is a presence scan for `_x`; the formal-object check validates a class vocabulary rather than the 158-object root registry; DB alignment checks paths but not semantic/status agreement. These passes do not contradict Findings F001-F012. | Validator source and command output | Publish validator contracts and negative controls; add cross-authority semantic validators. |
| `SEA-CALC-F014` | Medium | **Program inventory counts are stale.** `MATH_PROGRAM_NARRATIVE.md` reports 64 lemmas and 25 proofs, while the current non-template foundational tree contains 130 lemma files and 66 proof artifacts; the unified manifest contains 125 and 49. | Narrative `:96-98`; filesystem and manifest counts | Replace hand-maintained counts with generated counts that distinguish on-disk artifacts, registered artifacts, and status-qualified objects. |

## 6. What Is Inferred Inside the Framework

Within the repository's governance model, the findings imply that the immediate risk is not absence of mathematical material but **authority non-convergence**. The Calculus has substantial definitions, registries, proof scaffolds, validators, and evidence. However, a reviewer can reach different conclusions by selecting the textbook, core formalism, global status taxonomy, math status registry, unified manifest, or a mirrored lexicon surface.

The safe internal characterization is therefore:

> The repository contains a governed but incompletely reconciled partial Calculus. Its source and executable surfaces are sufficient for staged audit, but not yet sufficient for a single unqualified status attestation.

This is an internal governance inference, not a statement about the mathematical merit of the Calculus outside the declared repository stack.

## 7. External Resemblance — Analogy Only

The proposed audit resembles a configuration-control and requirements-traceability audit: policies define precedence, registries represent controlled state, documents express design intent, validators act as controls, and evidence artifacts support status decisions. This is an organizational analogy only. It does not imply accreditation, standards compliance, peer review, or independent mathematical certification.

## 8. What This Does Not Prove

This report does not prove that:

- the Calculus is mathematically false or mathematically complete;
- any physical, cosmological, or ontological interpretation is true or false;
- every notation variant is semantically incompatible;
- every broken link changes runtime behavior;
- every duplicated registry is intentionally authoritative;
- passing validators are useless; they remain evidence for their declared narrow scopes;
- an independent external reviewer will assign the same severity.

It also does not authorize deletion, status demotion, registry rewrites, theorem supersession, or claim promotion.

## 9. Failure Modes, Uncertainty, and Audit Limits

- The worktree was already heavily dirty. Findings describe the current working tree, not a clean release artifact.
- Some modified or untracked files may be mid-remediation. They were preserved and treated as observed state, not as completed authority.
- The audit did not semantically inspect every granular file under `registry/math/`; it prioritized authority, core laws, lifecycle, and validator boundaries.
- Historical patch intent can clarify lineage but cannot close a current conflict by itself.
- Encoding corruption makes exact string comparison hazardous on some surfaces.
- A full external audit still requires an independent reviewer, a frozen evidence bundle, and adversarial negative controls.
- Severity reflects governance impact inside this repository, not external scientific impact.

## 10. Remediation Order and Acceptance Criteria

Repairs should be separately authorized and applied in this order:

1. **Freeze and route authority.** Classify every primary Calculus surface and remove unresolved SSOT ambiguity.
2. **Canonicalize the root serialization.** Define exact canonical form plus typed admissible variants and encoding.
3. **Separate status namespaces.** Stop overloading C-levels across claim, rigor, formal closure, and external validation.
4. **Reconcile the four foundational laws.** Add explicit object/state records and bounded language for T001, SING-001, L043, and L045.
5. **Close registry coverage and dependencies.** Register all 201 current non-template artifacts or explicitly archive/exclude them; repair broken formal-object links.
6. **Normalize lexicon lifecycle and mirrors.** One schema, one current store, generated mirrors only.
7. **Synchronize textbook and narrative.** Preserve review locks, remove unsupported escalation, and replace stale counts.
8. **Harden validators.** Add negative controls for root semantics, authority conflicts, claim caps, mirror drift, dependency closure, and dirty-worktree freshness.
9. **Run the external re-audit.** Use the frozen protocol in Section 3 and publish residual exceptions.

Critical closure requires all of the following:

- one current authoritative expression for `RT_core` with typed variant rules;
- one non-overloaded status mapping;
- explicit current records for the four foundational laws;
- no C5/C6 or review-lock contradiction in current public-facing text;
- complete manifest coverage or explicit exclusions;
- zero unresolved required formal-object dependencies;
- DB freshness that accurately reports dirty-worktree state;
- independent negative-control evidence for each critical validator.

## 11. Reproducibility, Validation, and Textbook Synchronization Record

### 11.1 Commands and observed results

| Command/surface | Observed result |
|---|---|
| `python scripts/query_governance.py context-capsule ... --level summary` | Runtime `warn`; snapshot fresh; report target authority deferred |
| `python scripts/query_governance.py current-state --level summary` | Runtime `warn`; zero blockers/open debt |
| `python scripts/query_governance.py freshness ... --level summary` | `allow`, fresh, with incorrect no-dirty-worktree warning |
| `python scripts/validation/validate_core_expression_presence.py` | Pass; presence of generalized `_x` string only |
| `python scripts/math/validate_formal_objects.py` | Pass; 56 classes, 24 operators, 3 relations |
| `python scripts/db/check_registry_alignment.py` | Pass; zero path mismatches in its declared scope |
| `python scripts/math/validate_quantifier_explicitness.py` | Pass; 6 scopes, 2 quantifiers, 9 failure modes |
| `python scripts/governance/enforce_governance_integrity.py` | Pass; 96 verified assets and approved-bypass warnings |
| `python scripts/global_validate.py` | Exit 0; run `GV-20260720T220920.524424-7752`; overall `warning`; no failed stages; degraded stages `hygiene_validation` and `math_program_validation`; zero runtime, tooling, and semantic failures; clean-pass eligibility false |

### 11.2 Textbook synchronization audit

The textbook was audited and is **not synchronized** with current claim gates in at least these linked areas:

- `gravity_app` is described as C5 at line 2852 and as `REVIEW_LOCK` at line 3359;
- C6 is described as universal mechanism independence at lines 3105, 3850, and 4045, conflicting with other current claim/status meanings;
- the Appendix G source table repeats Singularity Rebound as C5/L3 at line 4475 despite the active charter and L2 lexicon state;
- the textbook calls the core formalism an authorized SSOT at line 4474, while live authority routing does not classify that file.

These mismatches remain intentionally unpatched in this audit task so that the evidence is preserved and because status/policy repair requires a separately governed remediation decision. This explicit mismatch record satisfies the task-level textbook synchronization audit requirement without silently changing disputed authority.

### 11.3 Final claim-humility review

The report was written as scoped repository observation. It does not use simulation as external proof, analogy as identity, or internal consistency as universal validation. Any words such as “proof,” “proven,” or “C6” appear as quoted repository labels, validator targets, or bounded descriptions of formal artifacts.
