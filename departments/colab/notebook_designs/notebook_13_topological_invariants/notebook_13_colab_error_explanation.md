# Notebook 13 Colab Error Explanation

## What Happened

The reported `NameError: name 'invariants' is not defined` is a downstream error.

The `invariants` DataFrame is created only after this chain succeeds:

1. imports and paths are defined,
2. `rt_notebook_12_outputs_results.zip` is found,
3. `nb12` is loaded from `factorial_results.parquet`,
4. Notebook 12 graph-construction classes/functions are defined,
5. topological invariant helpers are defined,
6. the graph loop completes at least one row.

When any earlier step fails, `invariants` is never assigned. Later cells that assume it exists then raise `NameError`.

## Root Causes

- **Colab path mismatch:** The original path `D:/projects/New folder/rt_notebook_12_outputs_results.zip` is a Windows host path. Colab cannot see it unless the zip is uploaded or mounted under a Colab-visible path such as `/content/rt_notebook_12_outputs_results.zip` or `/content/drive/MyDrive/...`.
- **Kernel reset / crash:** Colab clears Python memory after a runtime reset. Variables such as `zipfile`, `nb12`, `build_graph_from_nb12_row`, `topological_invariants`, and `invariants` disappear even if their cells ran earlier.
- **Cell order sensitivity:** The v1 scaffold split imports, loading, graph construction, invariant functions, and execution across separate cells. Running later cells after a reset produces missing-name errors.
- **Wrong column mapping:** Notebook 12 rows contain `state_modulus`, `max_depth`, `branch_width`, `initial_value`, `initial_suffix`, `schedule_seed`, and mechanism boolean columns. They do not contain `target_phase`, `target_depth`, `k_value`, `j_value`, or `r_value`.
- **No checkpointing:** The original exhaustive loop attempted to process all 13,824 configurations in one in-memory run. If Colab crashed, progress was lost.

## Corrective Action

Notebook 13 v2 supersedes the v1 execution scaffold for Colab execution. It keeps the same research question but changes the runtime strategy:

- one ordered bootstrap cell defines imports, paths, Notebook 12 graph reconstruction, and invariant functions,
- configuration rows are processed in chunks,
- each chunk is saved immediately,
- reruns skip completed chunks,
- final aggregation reads checkpoint files instead of relying on a live `invariants` object.

This is an execution-robustness change only. It does not promote any claim.
