# Calculus Audit Packet - 2026-07-20

**Audit ID:** MPF_CALCULUS_AUDIT_2026_07_20  
**Scope:** Rerun audit of the Acellorator / Mono-Process formal program as a calculus: typed objects, operators, closure/failure semantics, theorem-status gates, generated-output freshness, and governance synchronization.  
**Evidence class:** command-evidence / repository-local validation.  
**Claim scope:** Internal repository and formal-program consistency only. This audit does not assert external mathematical, physical, or ontological truth.

## Baseline Preservation

### Exact Commit And Worktree State

- Base commit inspected: `652ae015391c06cdd89d931e6efb796e902d65ce`.
- Worktree state: dirty before audit packet creation.
- Dirty inventory before packet creation: `207` porcelain status lines.
- Diff stat before packet creation: `206 files changed, 724 insertions(+), 477 deletions(-)`.
- Known substantive dirty surfaces from the current maintenance pass:
  - `MATH_PROGRAM_NARRATIVE.md`
  - `docs/textbook/mono_process_textbook_complete.md`
  - `registry/tool_manifest.json`
  - `registry/formal_objects/formal_object_registry.json`
  - `registry/governance_change_ledger.json`
  - `registry/governance/patches/MPF_TOOL_MANIFEST_INVENTORY_SYNC_001.json`
  - `registry/governance_manifest.json`
  - `registry/math_core_hashes.json`
  - `outputs/audits/global_health_report.json`
- Generated-output churn is present under `outputs/debug/`, `outputs/s_validation/`, and `validation/results/`.

### Pre-Inspection Synchronization Confirmation

Confirmed before inspection:

- Narrative synchronization: `MATH_PROGRAM_NARRATIVE.md` had already been narrowed to registry-gated, bounded claim language.
- Registry synchronization:
  - `python scripts\sync_math_registry.py` completed: `Sync complete. Registered 179 mathematical items in the unified manifest.`
  - `python scripts\sync_economics_hashes.py` completed.
  - `python scripts\check_tool_manifest_sync.py` completed: `OK: tool_manifest matches rigor endorsement manifests.`
  - `python scripts\check_manifest_gaps.py` completed: `All C++ directories are in registry/tool_manifest.json`.
  - `python scripts\db\check_registry_alignment.py` completed: `status: pass`, no mismatches.
- Appendix F/textbook synchronization: `docs/textbook/mono_process_textbook_complete.md` had been updated so the L118/P112 `otimes` projection case is explicitly Context-gated and collapses to `empty_projection` when unclosed in the Lean pilot.
- Promotion/governance ledger synchronization:
  - `registry/governance_change_ledger.json` contains `CHG_MPF_TOOL_MANIFEST_INVENTORY_SYNC_001`.
  - `registry/governance/patches/MPF_TOOL_MANIFEST_INVENTORY_SYNC_001.json` exists as the diff report.
  - `python scripts\governance\enforce_governance_integrity.py` passed and recognized `registry/tool_manifest.json` as approved by ledger.
- DB snapshot freshness:
  - `python scripts\db\snapshot_registries.py` completed with `status: success`.
  - Freshness query returned `db_snapshot_status: fresh`, `decision: allow`.

## Build And Validation Baseline

- `lake build` in `proofs/lean/`: exit code `0`; result: `Build completed successfully.`
- `python scripts\global_validate.py`: exit code `0`; report written to `outputs/audits/global_health_report.json`.
- Global validation run ID: `GV-20260720T120825.978633-692`.
- Global validation start: `2026-07-20T12:08:25.978633`.
- Global validation complete: `2026-07-20T12:08:58.921594`.
- Global validation overall status: `warning`.
- Failed stages: none.
- Degraded stages: `hygiene_validation`, `math_program_validation`, `report_write`.
- Runtime failures: `0`.
- Tooling failures: `0`.
- Semantic failures: `0`.
- Clean pass eligible: `false`.

## Generated Output Refresh

Generated outputs were refreshed during this rerun.

Evidence:

- `outputs/audits/global_health_report.json` was rewritten by `global_validate.py`.
- Multiple smoke summaries under `outputs/debug/` were rewritten.
- `outputs/s_validation/s_operator_audit.json` and `outputs/s_validation/s_validation_results.json` were rewritten.
- Many `validation/results/*_result.json` files were rewritten with fresh validation timestamps.

Classification: `GENERATED_OUTPUT_ONLY` for timestamp/result-output churn where no source semantics changed.

## Warning Counts By Category

| Category | Count | Source | Classification |
|---|---:|---|---|
| Legacy results naming hygiene | 131 | `hygiene_validation.warnings` | `STALE_ARTIFACT` |
| Governance approved-bypass notices | 18 | `governance_integrity_validation.warnings` | `SYNC_RESOLVED` |
| Math-program readiness warning | 1 status-level warning, 0 warning messages | `math_program_validation.status` | `STALE_ARTIFACT` |
| Report-write stale-report note | 1 | `stage_results.report_write` | `GENERATED_OUTPUT_ONLY` |

Notes:

- The prior operator-domain warning (`otimes` referencing `typed_operand_X`) is resolved.
- `math_program_validation` still reports warning status because `minimal_theorems` is warning and `mt_law_a_foundations_audit` / `mpf_palg_018_simultaneity` are `unknown`, not because unresolved operator domains remain.

## Theorem-Status Distribution

Source: `registry/math/theorem_status_registry.json`. Counted records from both embedded object records and `status_records`: `39`.

### Current Claim Level

| Claim level | Count |
|---|---:|
| `AXIOMATIC_FLOOR` | 1 |
| `C1_defined_provisional` | 24 |
| `C2_simulation_observed` | 2 |
| `C6_formal_closure` | 3 |
| `RESOLVED_L2` | 7 |
| `REVIEW_LOCK` | 2 |

### Maximum Allowed Claim Level

| Maximum allowed | Count |
|---|---:|
| `AXIOMATIC_FLOOR` | 1 |
| `C1_defined_provisional` | 24 |
| `C2_simulation_observed` | 2 |
| `C5` | 1 |
| `C6` | 4 |
| `RESOLVED_L2` | 7 |

### Current Status

| Status | Count |
|---|---:|
| `C1_DEFINED_PROVISIONAL` | 18 |
| `CAMPAIGN_SUPPORTED_REVIEW_REQUIRED` | 1 |
| `CONDITIONAL` | 1 |
| `FORMALLY_PROVEN` | 3 |
| `LOCKED` | 1 |
| `PROVISIONAL_INDUCTION_TARGET` | 1 |
| `PROVISIONAL_PENDING_RIGOR` | 1 |
| `RESOLVED_L2` | 7 |
| `REVIEW_GATED` | 2 |
| `REVIEW_LOCK` | 2 |
| `SUPPORTED_PENDING_REPLICATION` | 1 |
| `symbolic_checked` | 1 |

## Remaining Review Locks

Direct `REVIEW_LOCK` records:

| Object | Type | Claim level | Classification |
|---|---|---|---|
| `TC_asym` - Asymmetric Triadic Closure | `THEOREM` | `REVIEW_LOCK` | `STALE_ARTIFACT` |
| `gravity_app` - Gravity Projection | `APPLICATION_PROJECTION` | `REVIEW_LOCK` | `STALE_ARTIFACT` |

Review-lock source record:

- `OPEN_BRIDGE_001` remains `PROVISIONAL_PENDING_RIGOR`, claim level `C1_defined_provisional`, with review-lock targets: `TC_asym`, `K`, `B_K`, `topology_app`, `geometry_app`, `field_app`, `gravity_app`, `QM_app_GR_app_bridge`.

Interpretation:

- These are not new regressions from this rerun.
- They remain active governance constraints on promotion and downstream claim inheritance.

## Operator Domain/Codomain References

Command: `python scripts\math\validate_formal_objects.py`.

Result:

- Status: `pass`.
- Formal object count: `56`.
- Operator count: `24`.
- Relation count: `3`.
- Warnings: `0`.
- Open questions: `0`.
- Closure gaps: `0`.

Conclusion:

- Unresolved operator domain/codomain references: `0`.
- Prior unresolved references for `otimes`, `K_R`, `Pi_dist`, `<g>_y`, and `H_adm` are now resolved by provisional formal object registry entries.

Classification: `SYNC_RESOLVED`.

## Calculus Evaluation

The program currently behaves as a governed partial calculus rather than a closed universal calculus.

Observed strengths:

- Primitive/root expression governance is explicit and guarded against geometry-first, topology-first, operator-first, or physics-master-equation readings.
- Operators are increasingly typed through registries, with domain/codomain checks now passing.
- The Lean pilot compiles and gives constructive coverage for the current L116-L118/P110-P112 closure packet, including Context-gated `tensor`.
- Failure behavior is explicit in key places: unclosed tensor contexts collapse to `empty_projection`, failed P111 terms collapse to no inheritance record, and promotion gates block unsupported claim inheritance.

Observed limits:

- The calculus remains partial: many theorem-status records are C1 provisional and two direct records remain under `REVIEW_LOCK`.
- `global_validate.py` remains warning-level because historical result directories use legacy naming and some math-program validators are warning/unknown.
- Generated validation output churn is large and should be treated as runtime evidence refresh, not semantic source drift.
- No blanket C6, external-reality, physics, or universal-closure claim is licensed by this audit.

## Findings

| ID | Classification | Finding | Evidence | Action |
|---|---|---|---|---|
| F-001 | `SYNC_RESOLVED` | Narrative, registries, Appendix F/textbook wording, and promotion/governance ledger were synchronized before inspection. | Sync commands, governance integrity pass, Appendix F/textbook `otimes` update. | No further action for this audit. |
| F-002 | `SYNC_RESOLVED` | Unresolved operator domain/codomain references are cleared. | `validate_formal_objects.py`: pass, 0 warnings. | Preserve provisional object entries; do not promote beyond current claim levels. |
| F-003 | `GENERATED_OUTPUT_ONLY` | Generated outputs were refreshed by validation and smoke checks. | `global_health_report.json`, `outputs/debug/`, `outputs/s_validation/`, `validation/results/`. | Treat as refreshed command evidence, not semantic source changes. |
| F-004 | `STALE_ARTIFACT` | Legacy results naming remains a hygiene warning. | 131 hygiene warnings in `global_validate.py`. | Separate migration/archival cleanup task; avoid rewriting historical result paths casually. |
| F-005 | `STALE_ARTIFACT` | `math_program_validation` remains warning-level despite 0 warning messages because selected domain validators are warning/unknown. | `minimal_theorems` warning; `mt_law_a_foundations_audit` and `mpf_palg_018_simultaneity` unknown. | Audit validator readiness/status semantics separately. |
| F-006 | `STALE_ARTIFACT` | Two direct theorem/application records remain in `REVIEW_LOCK`. | `TC_asym`, `gravity_app`; source: `registry/math/theorem_status_registry.json`. | Preserve locks until rewrite, reroute, downgrade, retire, or retest path is completed. |
| F-007 | `SYNC_RESOLVED` | Tool manifest inventory drift is resolved without evidence promotion. | `check_manifest_gaps.py`: all C++ directories registered; governance ledger approval present. | Maintain C1/no-certification flags unless tool-local evidence is added. |
| F-008 | `GENERATED_OUTPUT_ONLY` | The report-write stale warning reflects that the prior health report was stale before this rerun, while the rerun refreshed it. | `stage_results.report_write`: `STALE_REPORT_WARNING`; latest report run ID recorded above. | No calculus defect. |

No `ACTIVE_DEFECT` or `NEW_REGRESSION` was identified in this rerun.

## Final Audit Position

The calculus is internally synchronized at the inspected registry and operator-typing surfaces, Lean builds successfully, and global validation exits cleanly with warning status. The warning status reflects historical hygiene and bounded-readiness issues, not a new crash, missing operator typing, failed DB alignment, or broken Lean proof pilot.

The correct current characterization is:

> A governed, typed, partial calculus with explicit promotion gates, active review locks, and refreshed validation evidence. It is not a closed universal calculus and does not license unrestricted external claims.
