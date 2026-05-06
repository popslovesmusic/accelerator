# Global Validation Routine (Agentic Remediation)

## Purpose
This document defines the governed procedure for an AI agent to remediate failures identified by the Tier 1 Global Validation Harness (`scripts/global_validate.py`).

## Procedure

### 1. Ingestion
The agent must read the latest `outputs/audits/global_health_report.json`.

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
*   **Correction:** Update the tool's `sim_governed.py` or recommend a certification downgrade to C1.

#### Tier 3: Hygiene Remediation
*   **Action:** For naming violations, the agent must rename directories to match the `YYYY-MM-DD_runNN_name` schema.
*   **Action:** For missing papers/data, the agent must search for orphaned artifacts and co-locate them or flag the run as `unrecoverable`.

### 4. Finalization
After remediation, the agent MUST rerun `scripts/global_validate.py` to confirm a "pass" status.
Any remaining gaps must be added to `lexicon_gap_queue.json` or documented in the project's `MEMORY.md`.
