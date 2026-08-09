# Notebook 14 Design: Generic Topology Feature Ablation

## Scope

Notebook 14 tests whether Notebook 13 v2's perfect topology classification survives removal of near-definitional branch-pair features.

It is a pre-execution design. Current status is `C1_SPECIFICATION_ONLY`.

## Directly Observed / Defined

Notebook 13 v2 result review found:

- 13,824 invariant rows,
- zero skipped configurations,
- topology-feature balanced accuracy of 1.0,
- direct topology proxies for the geometry definition present in the feature set.

Notebook 14 therefore excludes:

- `root_branch_pair_count`,
- `irreversible_separated_pair_count`,
- `has_irreversible_separation`,
- `merge_depth_min`,
- `merge_depth_mean`,
- `merge_depth_max`.

## Research Question

Can generic topology alone classify reconvergence geometry after the direct branch-pair and merge-depth proxy features are removed?

## Generic Feature Families

- SCC structure
- SCC condensation DAG
- articulation hierarchy
- bridge structure
- partial-order width
- reachability lattice measures
- basin decomposition
- graph diameter / depth profile
- dominance-tree properties
- graph-size controls

## Feature Ablation

Notebook 14 runs:

1. all permitted generic topology features,
2. graph-size-only baseline,
3. forbidden-proxy-only diagnostic,
4. one-family-removed ablations:
   - remove SCC,
   - remove condensation,
   - remove articulation,
   - remove bridge,
   - remove partial-order,
   - remove reachability,
   - remove basin,
   - remove diameter/depth,
   - remove dominance,
   - remove graph size.

The primary output is a table:

| Feature family removed | Balanced accuracy | Delta from all-generic |
| --- | --- | --- |

## Interpretation

If generic performance remains high, the result supports bounded evidence that non-definitional graph structure carries reconvergence signal.

If performance collapses while forbidden-proxy-only remains high, the result supports bounded limitation evidence that Notebook 13 v2 success depended on near-definitional features.

Either outcome advances the theory inside the bounded Notebook 12/13 domain.

## What It Does Not Prove

It does not prove implementation-independent continuation geometry. It does not validate external physical systems. It does not promote claims above C2. It does not authorize C5/C6 language.
