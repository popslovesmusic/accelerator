# Tool Equivalence Manifest Schema (MPF-ACELL-EQUIV-002)

## 1. Purpose
Subject all high-performance engines (C++, CUDA, etc.) to mandatory equivalence declarations. This schema ensures that every performance-optimized tool is explicitly tied to a governed reference baseline and that its validation history is machine-traceable.

## 2. Mandatory Fields
- **tool_name**: The unique ID of the tool.
- **reference_python_tool**: The ID of the Python tool used as the authoritative reference baseline.
- **equivalence_metrics**: The suite of metrics (e.g., `residue_mean`, `order_parameter`) used to compare implementations.
- **tolerance_policy**: Explicit numerical bounds for `absolute_tolerance` and `relative_tolerance`.
- **seed_policy**: Requirements for fixed seeds and minimum seed counts to ensure reproducible comparison.
- **failure_policy**: Defines the system behavior when divergence is detected (e.g., `HALT_ON_DIVERGENCE`).

## 3. Implementation Rule
All tools in `registry/tool_manifest.json` that use `cpp` or `hybrid` backends MUST provide a valid manifest according to this schema.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
