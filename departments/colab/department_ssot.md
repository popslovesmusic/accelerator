# Colab Department Single Source of Truth (SSOT)

This document is the local SSOT for the Colab Department.

It governs intake, indexing, provenance classification, and replication routing for `.ipynb` notebooks, result zip archives, artifact manifests, and external Colab-style simulation bundles.

The Colab Department is subordinate to global core, global governance, Analysis Intake, Analysis, and Mathematics. It does not define RT/Core, primitive operators, formal admissibility, theorem status, executable authority, or claim promotion. It prepares notebook and archive evidence for governed review.

---

## Department Charter

The Colab Department exists to prevent notebook and zip artifacts from bypassing provenance, evidence, and approved-tool gates.

Boundary rule:

Notebook source and result zips are evidence artifacts only. They are not canonical claims, approved tools, or validation results unless separately admitted through the governed registries and validators.

Methodological rule:

Every notebook or archive record must preserve source path, hash, execution status, manifest status, and claim ceiling.

Results-directory rule:

`departments/colab/results/` is the governed landing zone for Colab Department output bundles. Every result zip placed there must be inducted through `registry/induction_registry.json`, bound to `governance/live/induction_queue.json`, and registered in `registry/colab_result_archive_registry.json` before citation, interpretation, or claim review.

Experiment-specification rule:

Future notebook or archive outputs cannot be assigned `C2_BOUNDED_NOTEBOOK_OUTPUT` or `C2_LIMITATION_OR_NEGATIVE_RESULT` unless an immutable pre-execution `experiment_spec.json` is present or a governed legacy exception is explicitly recorded. The specification is C1 design/provenance evidence by itself; it gates C2 only when paired with recoverable outputs, hashes, and bounded interpretation.

---

## Scope and Boundaries

### In Scope
- `.ipynb` notebook intake,
- result zip intake,
- governed Colab result-output storage,
- artifact manifest indexing,
- immutable `experiment_spec.json` intake,
- notebook execution-status classification,
- Colab-style simulation bundle routing,
- hash and provenance preservation,
- replication-readiness notes,
- negative and limitation result preservation.

### Out of Scope
- approving simulation tools,
- promoting claims,
- defining math objects,
- theorem or proof status changes,
- replacing Acellorator governed execution,
- claiming external physical validation.

### Claim Ceiling

Default claim ceilings:

- `C1_NOTEBOOK_PROVENANCE`: notebook or archive exists with recoverable path and hash only.
- `C1_EXECUTION_RECONSTRUCTION`: notebook is reconstructed or internally replayed but not independently reproduced.
- `C1_EXPERIMENT_SPECIFICATION`: experiment design, parameter space, interpretation protocol, and immutability metadata are declared before execution; no result evidence is implied.
- `C2_BOUNDED_NOTEBOOK_OUTPUT`: notebook/result archive has recoverable outputs plus manifest or equivalent integrity evidence.
- `C2_LIMITATION_OR_NEGATIVE_RESULT`: notebook/result archive records inconclusive, null, limitation, non-identifiability, or counterexample evidence.

No Colab Department output may exceed C2 without approved-tool replication or separate formal admission.

---

## Evidence Classification Rules

### COLAB_EVIDENCE_001
An `.ipynb` file alone is C1 provenance evidence.

### COLAB_EVIDENCE_002
A result zip alone is C1 archive evidence unless a manifest, hash record, and output interpretation boundary are present.

### COLAB_EVIDENCE_002A
Every result zip in `departments/colab/results/` must have an archive ID, induction ID, queue entry ID, archive hash, manifest state, source notebook, experiment specification reference, evidence class, claim ceiling, and blocker list recorded in `registry/colab_result_archive_registry.json`.

### COLAB_EVIDENCE_003
A notebook plus immutable `experiment_spec.json` and manifest-backed result archive may be C2 bounded computational evidence only inside the declared notebook domain.

### COLAB_EVIDENCE_004
Reconstructed notebooks remain C1 reconstruction or C2 bounded output depending on output integrity, but they do not establish historical reproduction without count/hash match.

### COLAB_EVIDENCE_005
External Colab scripts are candidate tools only. They are non-claim-bearing until admitted through `registry/governance/campaign_tool_ledger.json` or reimplemented under approved tooling.

### COLAB_EVIDENCE_006
Non-identifiability, null regions, inconclusive results, and counterexample catalogs must be preserved as blockers rather than smoothed into positive claims.

### COLAB_EVIDENCE_007
An `experiment_spec.json` records the research question, hypothesis, independent variables, dependent variables, controls, random seed, parameter space, termination conditions, expected outputs, and interpretation protocol. It is immutable once execution begins; corrections require a superseding specification, not in-place mutation.

### COLAB_EVIDENCE_008
For future Colab Department C2 assignments, the `experiment_spec.json` content hash must be preserved before execution and cited with the notebook, result archive, manifest, and output hashes. Previously admitted pre-spec artifacts keep their recorded ceiling as legacy intake but require backfilled or superseding specifications before further replication or promotion review.

---

## Current Bound Intake

### NEW_FOLDER_STAGED_INDUCTION_PACKET_2026_07_22

Source root: `D:\projects\New folder`

Bound artifacts:
- `RT_Notebook_10_Continuation_Domain_Geometry_Restored.ipynb`
- `rt_notebook_10_outputs.zip`
- `RT_Notebook_11_Reachability_Overlap_Rigor_Endorsed.ipynb`
- `rt_notebook_11_outputs.zip`
- `RT_Notebook_12_Mechanism_Isolation.ipynb`
- `rt_notebook_12_outputs_results.zip`
- `campaign_runner.py`
- `phase_map_runner.py`

Classification:
- Notebook 10: `C1_EXECUTION_RECONSTRUCTION` / bounded C2 output only for its generated reconstruction dataset; not historical reproduction.
- Notebook 11: `C2_LIMITATION_OR_NEGATIVE_RESULT`; non-identifiability diagnosis blocks overlap-mechanism promotion.
- Notebook 12: `C2_BOUNDED_NOTEBOOK_OUTPUT`; bounded enumerated computational evidence inside its declared factorial domain.
- Result zips with manifest/hash evidence: C2 only inside declared source domain.
- External scripts: `C0_EXTERNAL_INTAKE` / non-claim-bearing candidate tools until reviewed.

Canonical routing:
- Intake packet: `outputs/analysis_intake/intake_report_NEW_FOLDER_STAGED_INDUCTION_PACKET_2026_07_22.json`
- Queue entry: `governance/live/induction_queue.json` entry `IQ_2026_07_22_011`
- Induction registry entry: `registry/induction_registry.json` entry `NEW_FOLDER_STAGED_INDUCTION_PACKET_2026_07_22`
- Tool ledger entries: `new_folder_campaign_runner_py_external`, `new_folder_phase_map_runner_py_external`

Active blockers:
- approved-tool replication pending,
- pre-spec legacy intake for Notebook 10/11/12 artifacts; backfilled experiment specifications required before further replication or promotion review,
- Notebook 11 non-identifiability,
- phase-map no-stable-region result,
- residue-causality `INCONCLUSIVE` outcome,
- Notebook 10 historical reproduction mismatch.

---

## Dependencies on Global Core

The Colab Department depends on:
- `AGENTS.md`
- repository-root `GEMINI.md`
- `registry/compliance_charter_v2_3.json`
- `governance/claim_policy.json`
- `registry/claim_scope_binding_registry.json`
- `registry/governance/semantic_projection_policy.json`

---

## Dependencies on Governed State

The Colab Department depends on:
- `departments/analysis_intake/department_ssot.md`
- `departments/analysis/department_ssot.md`
- `governance/live/department_registry.json`
- `governance/live/department_layout_manifest.json`
- `governance/live/department_relationship_registry.json`
- `governance/live/induction_queue.json`
- `registry/induction_registry.json`
- `registry/claim_registry.json`
- `registry/colab_result_archive_registry.json`
- `registry/governance/campaign_tool_ledger.json`
- `outputs/audits/global_health_report.json`

---

## Governance Rules

### COLAB_001
Every notebook and result archive must be classified before being cited.

### COLAB_002
Notebook outputs must include recoverable paths and hashes before C2 status is assigned.

### COLAB_003
Future C2 notebook/result classifications require an immutable pre-execution `experiment_spec.json` or an explicit governed legacy exception.

### COLAB_004
Colab-style execution does not imply approved Acellorator tool status.

### COLAB_005
Notebook/result archive evidence must preserve declared limitations and blockers.

### COLAB_006
Replication routing must prefer approved Acellorator tools or explicit tool-admission review.

### COLAB_007
No Colab result zip may be cited, interpreted, or routed for claim review until it has both induction binding and archive-registry binding.

### COLAB_008
Replacing a registered zip in place is prohibited. Corrections require a new archive ID, new hash, and supersession link.

---

## Prohibited Promotions

The following are blocked:
- `.ipynb` file to validation evidence without outputs,
- result zip to C2 without manifest/hash integrity,
- result zip citation without induction and `registry/colab_result_archive_registry.json` registration,
- in-place overwrite of a registered result zip,
- post-execution `experiment_spec.json` editing to rescue or expand a result claim,
- external Colab script to approved tool,
- notebook reconstruction to historical reproduction,
- C2 bounded notebook output to C5/C6 claim,
- analogy or visualization to physical fact.
