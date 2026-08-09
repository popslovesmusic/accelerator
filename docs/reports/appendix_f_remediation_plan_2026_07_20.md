# Appendix F Remediation Plan - 2026-07-20

**Plan ID:** MPF_APPENDIX_F_REMEDIATION_PLAN_2026_07_20  
**Target:** `docs/textbook/mono_process_textbook_complete.md`, Appendix F and directly linked cross-references.  
**Basis:** `docs/reports/calculus_audit_2026_07_20.md`, current Lean pilot status, theorem-status registry, formal-object registry, and current global validation output.  
**Scope:** Documentation remediation only. No claim promotion, theorem-status upgrade, or registry authority change is authorized by this plan alone.

## Current Baseline

- Appendix F was synchronized before the calculus audit for:
  - P111 valuation-linked Affect|Effect inheritance.
  - L118/P112 Context-gated `tensor`.
  - Provisional object references for `otimes`, `K_R`, `Pi_dist`, `<g>_y`, and `H_adm`.
- `lake build` passed.
- `global_validate.py` exited `0` with overall `warning`.
- Unresolved operator domain/codomain references: `0`.
- Direct `REVIEW_LOCK` records remain: `TC_asym`, `gravity_app`.
- `OPEN_BRIDGE_001` status reconciliation has been applied after this plan was drafted: bridge and theorem-status registries now align on `SUPPORTED / STRUCTURAL_ONLY`, while downstream review-lock targets remain independently gated.

## Remediation Objectives

1. Make Appendix F a single canonical, non-duplicated debt ledger.
2. Align every Appendix F claim cap with live theorem-status and bridge-governance gates.
3. Separate constructive Lean pilot discharges from broader framework claims.
4. Preserve review locks explicitly instead of implying that bridge-family support auto-promotes downstream objects.
5. Keep formal-object/domain sync visible while avoiding evidence promotion.

## Required Finding Classifications

Use these labels in the remediation commit notes and any follow-up audit:

- `ACTIVE_DEFECT`: a live contradiction or validation failure that changes calculus behavior.
- `STALE_ARTIFACT`: old wording, duplicate sections, or historical status residue that conflicts with current governance.
- `SYNC_RESOLVED`: a previously stale or missing sync surface now reconciled.
- `GENERATED_OUTPUT_ONLY`: validation/report churn with no source semantics change.
- `NEW_REGRESSION`: a problem introduced by the remediation pass.

## Phase 0 - Guardrails

Classification: `SYNC_RESOLVED`

Before editing Appendix F:

1. Run `python scripts\query_governance.py current-state --summary`.
2. Confirm DB freshness is `fresh` or refresh with `python scripts\db\snapshot_registries.py`.
3. Confirm current Lean status with `lake build` in `proofs/lean`.
4. Confirm formal-object references with `python scripts\math\validate_formal_objects.py`.
5. Record the current dirty worktree state so generated-output churn is not confused with Appendix F edits.

Acceptance:

- DB gate does not block documentation work.
- Lean remains buildable before the Appendix F edit.
- Operator domain/codomain warnings remain zero.

## Phase 1 - De-Duplicate Appendix F

Classification: `STALE_ARTIFACT`

Observed issue:

- `mono_process_textbook_complete.md` contains duplicated Appendix F headings and overlapping Appendix F content blocks.
- The duplicated blocks risk divergent status language for the same obligations.

Plan:

1. Choose one canonical Appendix F heading.
2. Merge unique content from the duplicate block into the canonical block.
3. Remove repeated boilerplate and repeated status tables.
4. Add a short header note:
   - Appendix F is the living debt ledger.
   - The theorem-status registry controls promotion caps.
   - Appendix F text is explanatory and non-authoritative when it conflicts with registries.

Acceptance:

- Exactly one `# Appendix F: Known Missing Definitions and Open Bridges` heading remains.
- No duplicate P111/L118/P112 entries remain.
- No duplicated Open Bridge Registry table remains.

## Phase 2 - Normalize Status Vocabulary

Classification: `STALE_ARTIFACT`

Observed issue:

- Appendix F mixes labels such as `SUPPORTED`, `PROVISIONAL_PENDING_RIGOR`, `STRUCTURAL_ONLY`, `C1_DEFINED_PROVISIONAL`, `THEORETICAL_ONLY`, and `CONSTRUCTIVELY_DISCHARGED_SUBSTANTIVE` without a local key.

Plan:

1. Add a compact Appendix F status key:
   - `CONSTRUCTIVELY_DISCHARGED_SUBSTANTIVE`: Lean/proof-pilot result inside encoded model only.
   - `C1_DEFINED_PROVISIONAL`: registered definition/formal object, no broad theorem claim.
   - `STRUCTURAL_ONLY`: bridge or projection can support structure-level discussion only.
   - `REVIEW_LOCK`: no promotion or downstream inheritance until rewrite/reroute/downgrade/retire/retest.
   - `THEORETICAL_ONLY`: formal scaffold pending validation.
2. For every Appendix F item, include:
   - `Status`
   - `Claim cap`
   - `Authority source`
   - `Does not license`

Acceptance:

- No Appendix F item uses status language without a claim cap.
- No entry implies external reality, physical fact, or universal closure from internal formalization.

## Phase 3 - Preserve Reconciled OPEN_BRIDGE_001 Language

Classification: `STALE_ARTIFACT`

Observed issue:

- Reconciled: later textbook entries, the bridge registry, and theorem-status registry now state that `OPEN_BRIDGE_001` is supported at the structural/topological-selector level.
- Still active: downstream objects remain blocked/review-locked despite bridge support.

Plan:

1. Split bridge language into explicit nodes:
   - `OPEN_BRIDGE_001_original`: historical direct-support formulation; falsified/superseded.
   - `OPEN_BRIDGE_001_selector_family`: supported structural selector family, no auto-promotion.
   - `OPEN_BRIDGE_001_v2`: supported induced-alignment bridge.
   - `OPEN_BRIDGE_001_v3`: supported procedural-model bridge with recorded exit path.
2. Add a bridge-family warning:
   - Supported bridge-family records do not lift `TC_asym`, `gravity_app`, `field_app`, `matter_app`, or `QM_app_GR_app_bridge`.
3. Preserve the current review-lock table:
   - `TC_asym`: `REVIEW_LOCK`.
   - `gravity_app`: `REVIEW_LOCK`.
   - `OPEN_BRIDGE_001` review-lock targets remain listed as downstream guardrails.

Acceptance:

- Appendix F no longer reads as if `SUPPORTED` means downstream promotion.
- `TC_asym` and `gravity_app` remain visibly locked.
- Historical falsification evidence remains archived and not overwritten.

## Phase 4 - Harden L116-L118 / P110-P112 Entries

Classification: `SYNC_RESOLVED`

Observed issue:

- Appendix F currently contains the right P111 and Context-gated L118/P112 entries, but nearby textbook sections still have looser phrasing such as closed compositional properties for `Pi_A otimes Pi_B`.

Plan:

1. Keep the P111 entry but make its bounded scope more uniform:
   - It is valuation-linked `AEInheritance`.
   - It is not a general Affect|Effect ontology theorem.
   - Failed terms collapse to `none`.
2. Keep L118/P112 as Context-gated:
   - `tensor c A B = proj_inter A B` only under `ProjectionClosed c`.
   - Unclosed contexts collapse to `empty_projection`.
3. Patch nearby summary wording outside Appendix F that still says bare closed operator algebra without the Context gate.

Acceptance:

- No bare `Pi_A otimes Pi_B = Pi_{A cap B}` claim appears without a Context-closed qualifier.
- P111 is not described as a string-label inheritance table.
- The failure boundary is stated for P111 and L118/P112.

## Phase 5 - Formal-Object Sync Note

Classification: `SYNC_RESOLVED`

Observed issue:

- The calculus audit resolved domain/codomain references by adding provisional formal object classes, but Appendix F does not yet summarize that remediation.

Plan:

1. Add a short Appendix F note:
   - `otimes`, `K_R`, `Pi_dist`, `<g>_y`, and `H_adm` now have declared formal object references.
   - This is a typing/registry sync only.
   - It does not promote the operators beyond their current claim caps.
2. Include the validation command:
   - `python scripts\math\validate_formal_objects.py`
   - Expected: `pass`, `warnings: []`.

Acceptance:

- Appendix F records that domain/codomain sync is resolved.
- No entry treats provisional object registration as proof or validation.

## Phase 6 - Remove Or Quarantine Overbroad C6 Language

Classification: `STALE_ARTIFACT`

Observed issue:

- The textbook still contains claim-class tables where `C6` is described in broad language such as universal mechanism independence or formal derivation from axiomatic floor.
- That language is not suitable near Appendix F without tight scoping.

Plan:

1. In Appendix F-adjacent claim tables, rewrite C6 descriptions to:
   - Formal closure within the declared stack and registered dependencies.
   - External or universal interpretation remains blocked unless separately validated.
2. Cross-reference the audit position:
   - The calculus is governed, typed, and partial.
   - It is not a closed universal calculus.

Acceptance:

- No Appendix F section uses C6 as blanket universality.
- Claim-class language matches the non-occlusive humility rule.

## Phase 7 - Verification

Classification: `GENERATED_OUTPUT_ONLY` for refreshed reports, unless failures appear.

After edits:

1. `lake build` from `proofs/lean`.
2. `python scripts\math\validate_formal_objects.py`.
3. `python scripts\db\check_registry_alignment.py`.
4. `python scripts\global_validate.py`.
5. `python scripts\query_governance.py freshness --summary`.
6. Search checks:
   - `rg -n "# Appendix F: Known Missing Definitions and Open Bridges" docs\textbook\mono_process_textbook_complete.md`
   - `rg -n "Pi_A.*otimes|REVIEW_LOCK|OPEN_BRIDGE_001|CONSTRUCTIVELY_DISCHARGED|C6" docs\textbook\mono_process_textbook_complete.md`

Acceptance:

- Lean passes.
- Formal-object validation passes with zero unresolved domain/codomain warnings.
- DB registry alignment passes.
- Global validation has no failed stages.
- Any remaining warning is classified as historical hygiene, readiness policy, or generated-output-only.

## Exit Criteria

Appendix F remediation is complete when:

1. There is one canonical Appendix F section.
2. Each listed obligation has status, claim cap, authority source, and non-license statement.
3. P111 and L118/P112 are bounded exactly to the Lean pilot semantics.
4. OPEN_BRIDGE_001 family support cannot be read as downstream promotion.
5. Direct review locks remain visible.
6. Operator domain/codomain sync is recorded as resolved.
7. Validation commands complete without new failed stages.

## Explicit Non-Goals

- Do not promote `TC_asym` or `gravity_app`.
- Do not convert structural bridge support into physics support.
- Do not remove historical falsification records.
- Do not treat generated validation-output churn as a textbook semantic change.
- Do not alter Lean theorem definitions as part of this Appendix F documentation remediation.
