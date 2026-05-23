# L027 — Relational Orientation Array

## Statement
Continuation is evaluated relative to a **global -(i) orientation array**, which functions as a distributed orientation topology. The framework is tree-like rather than chain-like because process continuation can branch and stabilize relative to multiple orientation relations simultaneously.

## Dependencies
- Specification: `Recursive Residue-Conditioned Conti.txt`
- Lemmas: L017 (Induced orientation)
- Prior lemmas: none

## Proof sketch
Branching emerges when selection `O*` satisfies multiple admissible continuation paths under different orientation contexts. ∎

## Status
draft

## Proof Type
heuristic

## Metadata (Migrated from LAW-006)
- **Law Conditions:**
  - local_orientation_operator_explicit
  - distributed_orientation_array_explicit
  - local_vs_global_roles_distinguished
  - NavT_local_operator_dependency_preserved
  - CSI_array_topology_dependency_preserved
  - recursion_density_emerges_from_array_structure
  - ordering_generated_distributively
  - no_local_global_collapse
- **Failure Modes:**
  - local_global_orientation_collapse
  - array_as_simple_collection_error
  - forced_global_orientation_frame
  - geometry_as_primitive_leakage
  - hidden_absolute_time_reintroduction
  - distributed_reconciliation_loss
  - orientation_operator_overextension
  - physics_claim_leakage

## Metadata (Migrated from LAW-008)
- **Law Conditions:**
  - orientation_array_topology_explicit
  - accessibility_relation_candidate_explicit
  - CSI_definition_candidate_explicit
  - local_ordering_neighborhood_explicit
  - transport_reachability_condition_explicit
  - finite_flux_dependency_preserved
  - spacetime_metric_not_assumed
  - no_global_accessibility_claim
- **Failure Modes:**
  - spacetime_metric_reintroduction
  - global_accessibility_overclaim
  - CSI_as_simple_distance_ball_error
  - unbounded_reachability
  - transport_without_admissibility
  - array_topology_collapse
  - hidden_global_causal_order
  - physics_claim_leakage
