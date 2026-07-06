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

Use semantic authority resolution when a patch declares semantic targets or when a theorem, operator binding, claim, domain rule, or runtime rule needs direct semantic ownership:

`python scripts/query_governance.py authority --semantic <key> --semantic-type <type>`

Use patch-chain resolution for the patch ID before attempting application:

`python scripts/query_governance.py patch-chain --patch-id <PATCH_ID>`

Use debt runtime resolution for governed debt before attempting application:

`python scripts/query_governance.py debt --status <open|partial|resolved|blocking|all>`

Use the minimal runtime capsule as the preferred preflight summary before opening broad docs:

`python scripts/query_governance.py context-capsule [--target <path-or-surface>] [--task <label>]`

Use the patch gate for an apply/block/defer decision. When a patch declares semantic targets, the patch gate also consults semantic authority before allowing application:

`python scripts/query_governance.py patch-gate --patch-id <PATCH_ID> --target <path-or-surface>`

Governance-significant runtime changes may also be recorded as append-only facts with `python scripts/query_governance.py emit-event` and inspected with `python scripts/query_governance.py events`.

If the runtime cannot classify the action, use `outputs/audits/global_health_report.json` and the canonical docs as fallback evidence. Document-first routing is fallback only.

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
Any remaining gaps must be added to `lexicon_gap_queue.json` or documented in the project's `MEMORY.md`.
