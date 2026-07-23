# Colab Department

This directory is the peer root for the Colab Department.

The live local SSOT is `departments/colab/department_ssot.md`, and the local agent rules are in `departments/colab/AGENTS.md`.

The department governs intake and indexing of notebook artifacts, result zip archives, immutable experiment specifications, and external Colab-style simulation runs. It does not approve tools, promote claims, or replace executable Acellorator validation.

Governed output root:
- `results/`

Canonical result zip registry:
- `../../registry/colab_result_archive_registry.json`

Experiment specification assets:
- `schemas/experiment_spec.schema.json`
- `templates/experiment_spec.json`

Notebook design packets:
- `notebook_designs/notebook_13_topological_invariants/`
  - v1: pre-execution topology design.
  - v2: ordered chunked Colab scaffold after reported v1 runtime/order failures.
- `notebook_designs/notebook_14_feature_ablation/`
- `notebook_designs/notebook_15_articulation_theory/`
- `notebook_designs/notebook_21_d_threshold_sensitivity/`
  - First campaign for the remaining D-semantics obligations; tests bounded context-indexed `epsilon_a,C` sensitivity.
