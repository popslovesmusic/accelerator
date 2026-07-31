# Standalone Governed Crawl Engine

This engine consolidates the deterministic crawl stages into one controller. It reads canonical sources, applies explicit source precedence, inventories the focused mathematical objects, constructs the typed dependency graph, detects cycles, computes a bounded delta, classifies blockers and risk, validates the report, and emits JSON/Markdown outputs.

## Run

From the repository root:

```powershell
python -m crawl_engine.engine --focus symmetry_condition_relation symmetry_condition bounded_symmetry unbounded_symmetry dominant_domain_projection distinction_permitting_symmetry_condition
```

The default output is under `departments/analysis/crawl_reports/`. The engine writes reports only; it does not modify mathematical definitions, proofs, registries, or executable semantics.

## Validation

```powershell
python -m unittest crawl_engine.tests.test_engine
```

Runtime metadata is excluded from deterministic comparison. Source hashes and the repository snapshot hash remain part of every report.
