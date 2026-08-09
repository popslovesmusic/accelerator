# Analysis Intake Department Single Source of Truth (SSOT)

This document is the local SSOT for the Analysis Intake Department.

It governs ingestion, parsing, claim extraction, classification, deduplication, routing, and proposal generation for structured packets and raw human notes.

The Analysis Intake Department is subordinate to the global core, global governance, the Analysis Department, and the Mathematics Department. It does not define RT/Core, primitive operators, formal admissibility, formal residue, theorem status, or executable authority. In this SSOT, every primitive is treated as RT-governed and traced to `RT_core`, but not every RT-governed expression is primitive; RT-derived continuations, projections, and operational regimes remain RT without being primitive. It converts provisional input into proposed governed artifacts only.

---

## Department Charter

The Analysis Intake Department exists to turn human-supplied material into governed work proposals without collapsing provenance or authority boundaries.

Boundary rule:

Raw input is provisional. Structured input is routable. Neither becomes authority until approved by the appropriate governed ledger.

Methodological rule:

Every extracted item must preserve source provenance, including the source excerpt when available.

---

## Scope and Boundaries

### In Scope
- ingest,
- parse,
- extract claims and terms,
- classify,
- deduplicate,
- route,
- propose artifacts,
- queue for approval,
- preserve provenance and source context.

### Out of Scope
- modifying authoritative registries,
- executing work,
- promoting claims directly from raw text,
- closing queues or campaigns,
- discarding ambiguity,
- inventing source evidence.

### Claim Ceiling
Unless separately validated, Analysis Intake outputs are capped at:
- `C0_definition` for intake rules and packet normalization,
- `C1_model_relative` for routing proposals and candidate work items.

No intake output may be treated as authority.

---

## Accepted Inputs

### Structured Inputs
- `json`,
- `json5`,
- `audit_packet`,
- `patch_packet`.

### Unstructured Inputs
- `raw_text`,
- `conversation_notes`,
- `research_notes`,
- `brainstorming`,
- `uploaded_text_files`.

Structured JSON must be schema-validated before routing.

Raw text must be treated as provisional and routed through extraction and review.

---

## Classification Targets

The intake layer may route candidates toward:
- `induction_queue`,
- `lexicon_gap_queue`,
- `campaign_registry`,
- `research_debt_registry`,
- `theorem_candidate_registry`,
- `proof_registry`,
- `validator_backlog`,
- `documentation_backlog`,
- `work_reduction_framework`,
- `master_work_index`.

---

## Intake Pipeline

All Analysis Intake outputs should follow this pipeline:
1. ingest,
2. parse,
3. extract_claims,
4. classify,
5. deduplicate,
6. route,
7. propose_artifacts,
8. queue_for_approval.

Ambiguous items must be routed to review rather than forced into a registry.

---

## Output Contract

All intake products must distinguish:
1. input class,
2. extracted candidates,
3. provenance,
4. routing target,
5. approval status.

Required outputs:
- `intake_summary`,
- `candidate_work_items`,
- `candidate_lexicon_entries`,
- `candidate_inductions`,
- `candidate_campaigns`,
- `warnings`,
- `unrouted_items`.

Artifact paths:
- `outputs/analysis_intake/intake_report_<id>.json`
- `outputs/analysis_intake/intake_report_<id>.md`
- `outputs/analysis_intake/candidate_patch_<id>.json`

---

## Induction Routing

The Analysis Intake Department is the local place for induction-class packet intake and pre-analysis normalization when a packet or study needs governed clarification before downstream review.

- Induction packets are handled as intake-layer inputs.
- Analysis Intake may extract definitions, dependency gaps, open questions, and support levels.
- Analysis Intake does not promote or authorize the induced claims.
- When an induction packet is relevant to current program state, it is routed toward `candidate_inductions` or the appropriate downstream review surface as a provisional item, not as authority.
- RT-calculus induction packets such as `RT_CALCULUS_AI_INDUCTION_PACKET_003` belong here as provisional intake material while their definitions remain under review.

### Bound Induction Notes

- `NEW_FOLDER_STAGED_INDUCTION_PACKET_2026_07_22` is admitted as bounded provisional research intake only.
- The canonical intake artifacts are `outputs/analysis_intake/intake_report_NEW_FOLDER_STAGED_INDUCTION_PACKET_2026_07_22.json` and `.md`.
- The live queue binding is `governance/live/induction_queue.json` entry `IQ_2026_07_22_011`.
- The canonical induction registry binding is `registry/induction_registry.json` entry `NEW_FOLDER_STAGED_INDUCTION_PACKET_2026_07_22`.
- Claim ceiling is `C2_EXTERNAL_BOUNDED_INDUCTION`.
- The external scripts from `D:\projects\New folder` are recorded in the campaign tool ledger only as unapproved, non-claim-bearing candidate artifacts.
- Active blockers against promotion: residue-causality outcome `INCONCLUSIVE`, phase-map no-stable-region result, Notebook 10 non-reproduction status, and Notebook 11 non-identifiability.

---

## Dependencies on Global Core

The Analysis Intake Department depends on:
- `AGENTS.md`
- repository-root `GEMINI.md`
- `registry/compliance_charter_v2_3.json`
- `governance/claim_policy.json`
- `registry/claim_scope_binding_registry.json`
- `registry/governance/semantic_projection_policy.json`

---

## Dependencies on Governed State

The Analysis Intake Department depends on:
- `departments/analysis/department_ssot.md`
- `governance/live/authority_manifest.json`
- `governance/live/department_registry.json`
- `governance/live/department_layout_manifest.json`
- `governance/live/department_relationship_registry.json`
- `governance/live/work_reduction_framework.json`
- `governance/live/master_work_index.json`
- `outputs/audits/global_health_report.json`

---

## Governance Rules

### ANALYSIS_INTAKE_001
Analysis Intake SHALL accept both structured JSON and raw human notes.

### ANALYSIS_INTAKE_002
Raw input SHALL be classified into proposed governed work but SHALL NOT itself become authority.

### ANALYSIS_INTAKE_003
Every routed item SHALL retain source provenance.

### ANALYSIS_INTAKE_004
The intake department SHALL recommend routing but SHALL NOT execute, promote, or close work.

### ANALYSIS_INTAKE_005
Approved or explicitly user-authorized definitions introduced through intake SHALL be inducted into the canonical root lexicon gap queue before downstream use. Induction SHALL preserve source provenance and keep the term at `GAP_OPEN` or another explicitly authorized provisional status; lexicon induction does not constitute validation, promotion, theorem registration, or execution authority.

### ANALYSIS_INTAKE_006
Every evidence intake, including imported external evidence packages and their derived review notes, SHALL perform a lexicon-delta pass. The pass SHALL compare governed terms and operator names in the imported evidence, extracted findings, and candidate patches against the canonical lexicon and existing gap queue. Each genuinely new governed term SHALL be added to `registry/lexicon_gap_queue.json` as `GAP_OPEN` before downstream review, synthesis, or notes induction. The entry SHALL retain the evidence package identifier, source path or excerpt, and available manifest/archive or source hash. Ordinary prose, unqualified common-language modifiers, and terms already represented canonically or as aliases need not be duplicated; ambiguous cases SHALL be routed to review.

---

## Validation / Falsification Status

- No intake recommendation in this SSOT is a registry mutation.
- No raw-text extraction in this SSOT is an authority claim.
- No candidate patch in this SSOT becomes authoritative without approval.
- This department remains an intake and proposal layer over provisional input.
- The 2026-07-22 New Folder induction is an exception only in the narrow sense that the user authorized registry binding; the bound content remains provisional, C2-capped, and non-promotional.

Current department status:
- intake parsing: active
- routing proposals: active
- execution authority: none
- promotion authority: none

---

## Prohibited Promotions

The following are blocked:
- raw text to authority,
- provisional notes to registry mutation,
- candidate work item to executed work,
- intake summary to promotion claim,
- extraction heuristic to canonical truth.
