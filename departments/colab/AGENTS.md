# Colab Department Agent Rules

This file provides local governance for agents working inside `departments/colab/`.

It is subordinate to:
- repository-root `AGENTS.md`
- repository-root `GEMINI.md`
- `registry/compliance_charter_v2_3.json`
- `governance/claim_policy.json`
- `registry/claim_scope_binding_registry.json`
- `registry/governance/semantic_projection_policy.json`
- `registry/governance/campaign_tool_ledger.json`
- `departments/colab/department_ssot.md`

## 1. Local Role

The Colab Department governs notebook and archive intake for `.ipynb` files, result zips, artifact manifests, and external Colab-style simulation bundles.

It is an indexing, provenance, and reproducibility-preparation layer. It does not own claim promotion, tool approval, or theorem status.

## 2. Must

Agents working here must:
- preserve notebook, zip, and manifest hashes,
- register every Colab result zip in `registry/colab_result_archive_registry.json`,
- bind every Colab result zip to an induction registry entry and induction queue entry before citation,
- require immutable `experiment_spec.json` records for future C2 notebook/result classifications,
- classify notebooks separately from result archives,
- distinguish executed notebook evidence from unexecuted notebook source,
- record whether outputs are recoverable and manifest-backed,
- verify that research question, hypothesis, variables, controls, seed, parameter space, termination conditions, expected outputs, and interpretation protocol were declared before execution,
- route external scripts to tool review before treating them as approved simulation tools,
- preserve C1/C2 boundaries,
- preserve negative, inconclusive, and non-identifiability results,
- cite recoverable paths for every notebook or archive claim.

## 3. Must Not

Agents working here must not:
- treat `.ipynb` presence alone as simulation evidence,
- treat result zips without manifests or hashes as C2 evidence,
- cite or interpret a Colab result zip before archive-registry and induction binding,
- overwrite a registered result zip in place,
- edit an `experiment_spec.json` after execution begins instead of creating a superseding specification,
- approve external Colab scripts as claim-bearing Acellorator tools,
- promote terms or claims from notebook text alone,
- overwrite canonical configs or source registries without explicit governed authorization,
- present Colab execution as physical validation.

## 4. Evidence Classification

- `C1_NOTEBOOK_PROVENANCE`: notebook or result archive exists with path and hash, but execution, manifest, or output integrity is not established.
- `C1_EXECUTION_RECONSTRUCTION`: notebook is reconstructed or replayed internally, but historical identity or independent reproduction is not established.
- `C1_EXPERIMENT_SPECIFICATION`: immutable pre-execution design and interpretation protocol exists; no result evidence is implied.
- `C2_BOUNDED_NOTEBOOK_OUTPUT`: notebook/result archive has recoverable outputs, manifest or equivalent integrity evidence, and bounded interpretation.
- `C2_LIMITATION_OR_NEGATIVE_RESULT`: notebook or archive records non-identifiability, null region, inconclusive outcome, or counterexample evidence.

Future C2 status also requires an immutable pre-execution `experiment_spec.json`, unless the SSOT records an explicit governed legacy exception. Higher status requires approved-tool replication or formal tool admission outside this department.

## 5. Minimum Output Structure

For substantive Colab-facing outputs, include:
1. source notebook/archive paths,
2. hash and manifest state,
3. experiment specification path and hash, when C2 is requested,
4. result archive registry ID for zips,
5. induction ID and queue entry ID,
6. execution/reconstruction status,
7. evidence class,
8. claim ceiling,
9. blockers and non-claims.
