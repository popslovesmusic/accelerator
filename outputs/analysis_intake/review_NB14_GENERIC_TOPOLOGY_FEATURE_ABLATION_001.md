# Notebook 14 Result Review

## Scope

Review of `departments/colab/results/NB14_GENERIC_TOPOLOGY_FEATURE_ABLATION_001.zip`.

This review is bounded to the supplied Notebook 14 Colab archive and the registered Notebook 13 v2 invariant table it consumes. It does not establish external physical validity or promote any claim above C2.

## Directly Observed / Defined

- Archive path: `departments/colab/results/NB14_GENERIC_TOPOLOGY_FEATURE_ABLATION_001.zip`
- Archive SHA-256: `929D137D0606FD9F31A09BED2821A2F62A58758786C33A2C3779A8D9634E5F91`
- Archive contents:
  - `feature_manifest.json`
  - `feature_ablation_results.csv`
  - `generic_topology_classification_report.json`
- Expected `manifest.json` is present as an external sibling file at `departments/colab/results/manifest.json`, SHA-256 `FD1BB5D383F491ABCF7ACB7E6A044E70981A01EFF0960FBE31A666CB6715C41C`.
- The manifest is not inside the zip archive.
- Forbidden features were declared:
  - `root_branch_pair_count`
  - `irreversible_separated_pair_count`
  - `has_irreversible_separation`
  - `merge_depth_min`
  - `merge_depth_mean`
  - `merge_depth_max`
- `all_generic_features` excludes the forbidden features.

Observed balanced accuracy:

| Condition | Balanced accuracy | Delta from all-generic |
| --- | ---: | ---: |
| all_generic | 0.931843 | 0.000000 |
| graph_size_only | 0.710971 | 0.220872 |
| forbidden_proxy_only_diagnostic | 1.000000 | -0.068157 |
| remove_graph_size | 0.932641 | -0.000798 |
| remove_reachability_lattice | 0.934344 | -0.002502 |
| remove_scc_structure | 0.930937 | 0.000906 |
| remove_condensation_dag | 0.932517 | -0.000674 |
| remove_basin_decomposition | 0.932435 | -0.000593 |
| remove_articulation_hierarchy | 0.814305 | 0.117538 |
| remove_bridge_structure | 0.930801 | 0.001042 |
| remove_partial_order_width | 0.932849 | -0.001007 |
| remove_dominance_tree | 0.928620 | 0.003222 |

## Inferred Inside Framework

Within the Notebook 13 v2 / Notebook 12 bounded domain, generic topology features retain strong classification performance after the near-definitional branch-pair and merge-depth proxy features are excluded.

The ablation table indicates that articulation hierarchy carries the largest observed marginal signal among the declared feature families: removing articulation features reduces balanced accuracy by about `0.1175`. Other single-family removals have small or slightly negative deltas in this run.

The forbidden-proxy-only diagnostic remains perfect, confirming the Notebook 13 v2 review concern that direct branch-pair and merge-depth features encode the label construction.

## External Resemblance

The result resembles a transition from definitional graph-label features toward more generic structural graph signals. This is an analogy only.

## What It Does Not Prove

- It does not prove implementation-independent continuation geometry.
- It does not prove that topology universally governs reconvergence outside the Notebook 12/13 domain.
- It does not validate external physical systems.
- It does not satisfy C5/C6 requirements.
- It does not eliminate all possible feature leakage or data-split dependence.

## Failure Modes / Uncertainty

- The expected `manifest.json` is present beside the archive but absent from the zip itself.
- The report does not show grouped evaluation by mechanism mask or panel.
- The classifier split appears to be a standard stratified split; correlated configurations may still leak across train/test.
- Feature-family groups are based on the Notebook 13 v2 invariant table; graph diameter was requested conceptually but no distinct diameter feature appears in the table.
- Approved-tool replication remains pending.
