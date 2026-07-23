# Global Validation Routine (Agentic Remediation)

## Purpose
This document defines the governed procedure for an AI agent to remediate failures identified by the Tier 1 Global Validation Harness (`scripts/global_validate.py` / `python -m scripts.global_validate`).

## Canonical Invocation
Until `DEBT_VALIDATOR_IMPORT_PATH_001` is resolved, the canonical governed invocation is:

`python -m scripts.global_validate`

Direct file invocation via `python scripts/global_validate.py` is currently non-canonical because package-style imports fail in that execution mode.

## Governance Runtime Gate
Before patch application, authority-bearing edits, or blocked-dependency resolution, query the DB governance runtime first.

Use the current-state capsule to inspect live state:

`python scripts/query_governance.py current-state`

Use freshness to inspect snapshot recency before DB-dependent operations:

`python scripts/query_governance.py freshness [--target <path-or-surface>]`

Freshness compares source-affecting changes against the stored source marker and runtime-only DB churn against the stored runtime marker. Routine decision logs, event emission, and refresh metadata do not stale the source projection unless they move beyond the runtime marker; if freshness remains stale, the command output must name the source drift or refresh failure directly.

Use authority resolution for the target surface before modifying any authority-bearing file:

`python scripts/query_governance.py authority --target <path-or-surface>`

For the governed Q0 authority partition surfaces, generic authority lookup is fail-closed. Operators must declare the requested Q0 role explicitly with `--authority-role <REGISTRY_STATE_AUTHORITY|REGISTRY_WRITE_AUTHORITY|VALIDATION_INVOCATION_AUTHORITY|VALIDATION_REDUCTION_AUTHORITY|INSTRUCTION_AUTHORITY|GENERATED_EVIDENCE>`.

Use semantic authority resolution when a patch declares semantic targets or when a theorem, operator binding, claim, domain rule, or runtime rule needs direct semantic ownership:

Patch-chain evaluation is no longer limited to one implicit dependency meaning. When a patch declares `dependency_requirements`, the runtime distinguishes `REQUIRES_COMPLETED_PREDECESSOR`, `REQUIRES_EXISTING_EVIDENCE`, `REQUIRES_SEMANTIC_RULE`, and `HISTORICAL_LINEAGE_ONLY` instead of collapsing every `depends_on` edge into a completed-predecessor gate.

`python scripts/query_governance.py authority --semantic <key> --semantic-type <type>`

Use patch-chain resolution for the patch ID before attempting application:

`python scripts/query_governance.py patch-chain --patch-id <PATCH_ID>`

Use debt runtime resolution for governed debt before attempting application:

`python scripts/query_governance.py debt --status <open|partial|resolved|blocking|all>`

Use the minimal runtime capsule as the preferred preflight summary before opening broad docs:

`python scripts/query_governance.py context-capsule [--target <path-or-surface>] [--task <label>]`

Use the patch gate for an apply/block/defer decision. When a patch declares semantic targets, the patch gate also consults semantic authority before allowing application:

`python scripts/query_governance.py patch-gate --patch-id <PATCH_ID> --target <path-or-surface>`

Governance runtime queries now accept standardized evidence levels. Use `--level summary`, `--level diagnostic`, `--level governance`, or `--level forensic` on `current-state`, `authority`, `patch-chain`, `patch-gate`, `debt`, `freshness`, `context-capsule`, `events`, `replay-events`, and `reconcile-events` when you want to bound the payload. `--summary` remains a compatibility alias for `--level summary`. Summary mode returns a bounded report-grade payload with `patch_id`, `query`, `status`, `verdict`, `reason`, `blockers`, `runtime_path`, and `full_report_available`; higher levels return progressively richer evidence surfaces, and forensic mode preserves the full runtime object.

Governance-significant runtime changes may also be recorded as append-only facts with `python scripts/query_governance.py emit-event` and inspected with `python scripts/query_governance.py events`.

If the runtime cannot classify the action, use `outputs/audits/global_health_report.json` and the canonical docs as fallback evidence. Document-first routing is fallback only.

## Bounded Validation Modes
The default governed invocation remains the full harness:

`python -m scripts.global_validate`

Additive bounded modes are now available when a smaller surface is needed:

`python -m scripts.global_validate --quick`

`python -m scripts.global_validate --registries-only`

`python -m scripts.global_validate --governance-only`

`python -m scripts.global_validate --patch-chain-only`

`python -m scripts.global_validate --db-only`

`python -m scripts.global_validate --math-only`

`python -m scripts.global_validate --stage-timeout-seconds <seconds>`

`python -m scripts.global_validate --profile`

`python -m scripts.global_validate --no-db-log`

`python -m scripts.global_validate --history`

`python -m scripts.global_validate --trend`

`python -m scripts.global_validate --trend --trend-baseline <run_id>`

`python -m scripts.global_validate --trend --no-history`

The harness now records per-stage durations and can classify a stall as semantic, runtime, or tooling-related in the generated report.
The report now also includes `stage_results`, `slowest_stages`, `runtime_failures`, `tooling_failures`, `semantic_failures`, and a `stale_report_warning` flag so stage-localization is preserved even when the run is bounded.

For narrower subtask runs, use `--stages` to trim the selected validation plan to one or more named stages, and `--list-stages` to print the available stage names for the chosen mode before running anything. Stage names accept space-separated or comma-separated input, so a focused invocation can be as small as:

`python -m scripts.global_validate --registries-only --stages manifest_validation,json_parse_validation,registry_validation`

Dedicated wrapper entrypoints are also available when a named surface is easier to remember than a stage list:

`python scripts/validate_registry_surface.py`

`python scripts/validate_governance_surface.py`

`python scripts/validate_db_surface.py`

`python scripts/validate_math_surface.py`

`python scripts/validate_operational_surface.py`

When `--history` is enabled, the harness appends a compact JSONL summary to `outputs/audits/validation_history.jsonl`. The summary is intentionally compact and excludes recursive evidence trees, so it can be used as longitudinal telemetry without becoming an authority surface.

When `--trend` is enabled, the harness writes `outputs/audits/validation_trend_report.json` comparing the current run to the most recent passing full validation run by default. A specific baseline may be selected with `--trend-baseline <run_id>`. If no usable baseline exists, the trend report records `TREND_HISTORY_UNAVAILABLE` or `TREND_HISTORY_CORRUPT` and the semantic validation outcome remains unchanged.

History and trend telemetry are audit artifacts only. They do not alter validator semantics, patch promotion semantics, or RT_core governance.

The current stage model is:

`manifest_validation`

`json_parse_validation`

`registry_validation`

`hash_registry_validation`

`governance_ledger_validation`

`patch_record_validation`

`patch_chain_validation`

`patch_gate_validation`

`db_authority_validation`

`math_validation`

`math_test_provenance_validation`

`math_program_validation`

`hygiene_validation`

`report_write`

Partial modes select a governed subset of those stages:

`--quick` favors manifest, registry, database authority, patch-chain, and patch-gate smoke checks.

`--registries-only` favors manifest, JSON parse, registry, hash registry, governance ledger, and patch record checks.

`--governance-only` favors registry, ledger, patch record, patch-chain, patch-gate, and database authority checks.

`--db-only` isolates the database authority/runtime probe.

`--math-only` isolates the math validation surfaces.

## Procedure

### 1. Ingestion
The agent must read the latest `outputs/audits/global_health_report.json` after the runtime gate has been queried or when the runtime does not provide a decision surface. The governed runtime order is context-capsule -> current-state -> freshness -> authority -> patch-chain -> debt -> patch-gate. The context capsule now also surfaces bounded replay reconciliation coverage alongside the other minimal runtime summary fields.

### 2. Analysis & Priority
The agent must categorize failures into three tiers:
1.  **Critical (Registry/Integrity):** Broken JSON or missing cross-references.
2.  **High (Engine/C4):** Smoke test failures for certified dynamcis engines.
3.  **Medium (Hygiene):** Naming or structural violations in the `results/` directory.

### 3. Remediation Actions

#### Tier 1: Registry Remediation
*   **Action:** If a tool is missing from the manifest but used in the lexicon, the agent must either induct the tool or correct the lexicon entry.
*   **Tool:** `replace`, `write_file`.

#### Tier 2: Engine Remediation
*   **Action:** If a C4 engine smoke test fails, the agent must check the `outputs/debug/smoke_<tool_name>` logs.
*   **Diagnosis:** Identify if the failure is due to environment (Intel oneAPI), parameter mismatch, or logic regression.
*   **Correction:** Update the tool's `sim_governed.py` or recommend a rigor endorsement downgrade to C1.

#### Tier 3: Hygiene Remediation
*   **Action:** For naming violations, the agent must rename directories to match the `YYYY-MM-DD_runNN_name` schema.
*   **Action:** For missing papers/data, the agent must search for orphaned artifacts and co-locate them or flag the run as `unrecoverable`.

### 4. Finalization
After remediation, the agent MUST rerun `python -m scripts.global_validate` to confirm a "pass" status.
After required validation and textbook synchronization are complete, every governed state-changing task MUST end with an intentional Git commit covering the task-scoped delta before closeout.
If unrelated dirty state prevents an isolated task-scoped commit, the task remains open and the blocker MUST be recorded explicitly in the closeout report or governance ledger.
Read-only audit tasks are exempt because they do not modify governed state.
Any remaining gaps must be added to `lexicon_gap_queue.json` or documented in the project's `MEMORY.md`.
