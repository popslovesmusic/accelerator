# Notebook 13 Design: Topological Invariants of Continuation Geometry

## Scope

Design a pre-execution Colab notebook that regenerates every continuation graph in the bounded Notebook 12 factorial domain and tests whether topology-only invariants classify:

- `universal_reconvergence`,
- `partial_reconvergence`,
- `obstruction`.

This design is C1 specification evidence only. It does not report Notebook 13 results.

## Directly Observed / Defined

Notebook 12 output archive `D:/projects/New folder/rt_notebook_12_outputs_results.zip` contains:

- `factorial_results.parquet` with 13,824 configurations and existing `geometry` / `J` labels,
- `graph_metrics.parquet` with the same 41 summary columns,
- `branch_pair_results.parquet` with 19,686 branch-pair rows,
- `candidate_invariant_ranking.csv`,
- witness and counterexample catalogs,
- `manifest.json` declaring the bounded interpretation constraint.

The archive does not contain serialized continuation graphs. Notebook 13 must therefore regenerate graphs from the Notebook 12 generator/configuration domain or use an explicit adapter that returns the same `networkx.DiGraph` objects.

## Research Question

Can topology alone classify universal reconvergence, partial reconvergence, and obstruction across the continuation graphs generated from Notebook 12?

## Hypothesis

Within the bounded Notebook 12 domain:

`local mechanisms -> continuation graph topology -> reconvergence geometry -> J`

The test succeeds only if topology-only features classify geometry beyond label-frequency and graph-size-only controls while preserving failures and counterexamples.

## Required Invariant Families

- Reachability lattice: unique descendant-closure sets, inclusion relations, lattice height, lattice width proxy, closure collisions.
- SCC condensation DAG: SCC count, condensation edges, source/sink counts, DAG height, topological generation profile.
- Basin decomposition: sink basins in the condensation DAG, basin sizes, overlap, terminal basin count.
- Articulation hierarchy: undirected articulation points, articulation depths, subtree split sizes, hierarchy height.
- Irreversible separation depth: earliest branch depth where future closures separate without later merge.
- Merge depth: earliest common descendant depth for root-branch pairs, mean/min/max merge depths.
- Partial-order width: maximum antichain or bounded exact/approximate width of the condensation DAG.
- Dominance tree: immediate dominator tree from the root, dominator depth, branch dominance counts.
- Closure lattice: closure signatures ordered by subset inclusion; ambiguous closure-to-label cases.

## Controls

- Majority-label / empirical-frequency baseline.
- Graph-size-only baseline: node count, edge count, max depth, branch width.
- Mechanism-label exclusion: no mask bits or mechanism booleans in topology-only classifiers.
- Grouped evaluation by mechanism mask and parameter panel where feasible.
- Counterexample preservation for topology-equivalent signatures with different `geometry` or `J`.

## Interpretation Protocol

SUCCESS_C2_CANDIDATE:
Topology-only invariants classify the three geometry classes above controls under grouped evaluation, with bounded and recoverable counterexamples.

PARTIAL_C2_CANDIDATE:
Topology separates obstruction from non-obstruction or predicts J strata, but fails full three-class classification.

FAILURE_OR_LIMITATION_C2_CANDIDATE:
Topology-equivalent or near-equivalent signatures produce different geometry/J labels, or performance collapses under controls.

INCONCLUSIVE:
Graph regeneration, dependency constraints, or artifact mismatch prevents complete evaluation.

## What This Does Not Prove

It does not prove that topology universally governs reconvergence outside Notebook 12. It does not validate external physical systems. It does not promote claims above C2. It does not establish an implementation-independent theory unless replicated through approved Acellorator tooling and independent measurements.

