# Documentation Department Single Source of Truth (SSOT)

This document is the local SSOT for the Documentation Department.

It governs documentation consistency, onboarding quality, discoverability, drift detection, and documentation debt tracking across the Acellorator repository.

The Documentation Department is subordinate to the global core and global governance. It does not define mathematical truth, governance truth, theorem status, or execution authority. It maintains documentation surfaces so they accurately reflect the live governed state.

---

## Department Charter

The Documentation Department exists to keep project documentation coherent, synchronized, and auditable.

Boundary rule:

Live governance artifacts remain authoritative. Documentation must reflect them, but may not override them.

Methodological rule:

Broken references, stale onboarding, missing README files, and historical/spec drift are governed documentation work.

---

## Scope and Boundaries

### In Scope
- README files,
- department README files,
- department SSOT organization,
- AGENTS.md consistency,
- onboarding documentation,
- project navigation,
- documentation inventories,
- documentation audits,
- documentation debt,
- documentation reduction recommendations.

### Out of Scope
- governance registry mutation,
- mathematics registry mutation,
- proof registry mutation,
- validator logic,
- execution artifacts,
- theorem promotion,
- changing live authority through documentation alone.

### Claim Ceiling
Unless separately validated, Documentation Department outputs are capped at:
- `C0_definition` for documentation rules and organization,
- `C1_model_relative` for documentation audit and sync recommendations,
- `C3_structural_comparison` for drift and consistency assessments.

No documentation output may supersede a live governed ledger.

---

## Dependencies on Global Core

The Documentation Department depends on:
- `AGENTS.md`
- repository-root `GEMINI.md`
- `registry/compliance_charter_v2_3.json`
- `governance/claim_policy.json`
- `registry/claim_scope_binding_registry.json`
- `registry/governance/semantic_projection_policy.json`

---

## Dependencies on Governed State

The Documentation Department depends on:
- `governance/live/authority_manifest.json`
- `governance/live/department_registry.json`
- `governance/live/department_layout_manifest.json`
- `governance/live/department_relationship_registry.json`
- `governance/live/work_reduction_framework.json`
- `governance/live/master_work_index.json`
- `governance/live/induction_queue.json`
- `registry/induction_registry.json`
- `outputs/audits/global_health_report.json`
- `scripts/query_governance.py` when live governance state is inspected for documentation sync; use explicit evidence levels (`--level summary|diagnostic|governance|forensic`) and keep `--summary` as the compatibility alias for `--level summary`

Every documentation recommendation must cite the live artifact or artifacts it was derived from.

---

## Documentation Framework

All Documentation Department outputs must distinguish:
1. source artifact set,
2. drift or consistency rule,
3. recommendation class,
4. support level.

Interpretive boilerplate:

`Within the Documentation Department interpretation...`

### Canonical Reading

Within this department, documentation is a synchronized reflection of live governed state rather than an independent authority.

### Drift Reading

Within this department, broken references, stale onboarding, and outdated department READMEs are documentation debt.

---

## Initial Interpretive Entries

#### DOC_INT_001
- **Title:** Documentation as Synchronization Layer
- **Source Evidence:** live authority manifest, live department registry, live work-reduction framework, master work index
- **Interpretation:** documentation is treated as a maintenance layer that reflects live governance without replacing it.
- **Claim Class:** `C3_structural_comparison`
- **Status:** provisional interpretation

#### DOC_INT_002
- **Title:** Broken References as Documentation Debt
- **Source Evidence:** root README, department README files, onboarding paths
- **Interpretation:** broken links and stale references are treated as governed documentation debt.
- **Claim Class:** `C1_model_relative`
- **Status:** derivation scaffold

#### DOC_INT_003
- **Title:** Historical Specification Drift as Residue
- **Source Evidence:** live ledgers versus legacy specification artifacts
- **Interpretation:** superseded specs are treated as historical residue that must be labeled clearly when live authority has moved on.
- **Claim Class:** `C3_structural_comparison`
- **Status:** provisional interpretation

---

## Validation / Falsification Status

- No documentation recommendation in this SSOT is a governance mutation.
- No documentation inventory in this SSOT is a source of truth over live ledgers.
- No documentation sync report may override canonical registries.
- This department remains a support layer for discoverability and maintenance.

Current department status:
- documentation consistency: active
- onboarding quality: active
- execution authority: none over governance truth
- promotion authority: none

---

## Prohibited Promotions

The following are blocked:
- documentation to governance authority,
- documentation to mathematical authority,
- documentation to theorem status,
- stale references treated as current authority,
- historical specification treated as live ledgers,
- documentation drift ignored as non-governed noise.
