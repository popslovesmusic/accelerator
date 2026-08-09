# L057 — Unified Admissibility and Gating Law

## Statement
A process update $\Delta x_\alpha$ is admissible if and only if it is a member of the local admissibility window $A_\alpha$, determined by the residue-conditioned filtering operator $\Pi_{A_\alpha}$. Legality evaluation must precede all state updates to ensure participation coherence across CSI boundaries.

## Dependencies
- Definitions: `admissibility_window`, `filtering_operator`, `csi_boundary`
- Assumptions: Admissibility is the primary gate for continuation.
- Prior lemmas: L001, L003, L004, L011, L013, L014, L016, L022, L023.

## Proof sketch
1. From the core process grammar, any continuation actualization $\delta$ is gated by the operator $\Leftrightarrow_R$.
2. This gating is operationalized as a projection $\Pi_A$ that maps candidate increments to the admissible set $A$.
3. Any increment $\Delta x_\alpha$ that does not satisfy $\Delta x_\alpha \in A_\alpha$ is excluded from the realization phase.
4. Symmetry and residue-dependence of CSI boundaries (L011) ensure that this gating is consistent across coupled loci.
5. Therefore, admissibility is the unified regulator of process legality and structural stability.

## Status
draft

## Supersedes / Superseded-by
- **Supersedes:** L001, L003, L004, L011, L013, L014, L016, L022, L023.
- **Notes:** This lemma provides a unified formal grounding for the admissibility and gating rules of the framework.

## Metadata (Migrated from LAW-002)
- **Law Conditions:**
  - admissibility_window_A_explicit
  - projection_domain_explicit
  - projection_image_subset_of_A
  - idempotence_condition_explicit
  - boundary_cases_preserved
  - multi_valued_projection_allowed
  - undefined_projection_cases_preserved
  - no_global_projection_closure_claim
- **Failure Modes:**
  - projection_nonexistence
  - projection_nonuniqueness
  - boundary_instability
  - window_collapse
  - branch_overcollapse
  - false_idempotence_overclaim
  - global_closure_leakage
  - physics_claim_leakage

## Metadata (Migrated from LAW-005)
- **Law Conditions:**
  - boundary_definition_explicit
  - interior_admissibility_condition_explicit
  - boundary_transition_condition_explicit
  - projection_failure_condition_explicit
  - branch_splitting_allowed
  - branch_pruning_allowed
  - multi_valued_continuation_preserved
  - no_global_boundary_stability_claim
- **Failure Modes:**
  - projection_failure
  - boundary_instability
  - window_collapse
  - branch_overcollapse
  - forced_unique_projection
  - topology_discontinuity
  - transport_induced_boundary_divergence
  - physics_claim_leakage

## Metadata (Migrated from LAW-021)
- **Law Conditions:**
  - orientation_array_dependency_explicit
  - local_budget_definition_explicit
  - regional_budget_definition_explicit
  - continuation_cost_candidate_explicit
  - budget_condition_explicit
  - depletion_condition_explicit
  - recovery_condition_explicit
  - saturation_condition_explicit
- **Failure Modes:**
  - unbounded_continuation_assumption
  - infinite_admissibility_budget_overclaim
  - physics_energy_equivalence_leakage
  - global_resource_conservation_overclaim
  - budget_without_cost_definition
  - saturation_failure_suppression
  - primitive_substance_resource_reintroduction
  - physics_claim_leakage

## Metadata (Migrated from LAW-027)
- **Law Conditions:**
  - orientation_array_dependency_explicit
  - metastable_regime_dependency_explicit
  - transition_pressure_candidate_explicit
  - tipping_threshold_candidate_explicit
  - phase_transition_condition_explicit
  - avalanche_condition_explicit
  - topology_reorganization_condition_explicit
  - regime_shift_condition_explicit
- **Failure Modes:**
  - physical_phase_transition_overclaim
  - thermodynamic_criticality_leakage
  - universal_regime_law_overclaim
  - transition_without_threshold
  - avalanche_without_dependency
  - topology_reorganization_without_admissibility
  - primitive_geometry_reintroduction
  - physics_claim_leakage

## Metadata (Migrated from LAW-032)
- **Law Conditions:**
  - orientation_array_dependency_explicit
  - failure_mode_family_explicit
  - runaway_condition_explicit
  - deadlock_condition_explicit
  - fragmentation_condition_explicit
  - reinforcement_lock_condition_explicit
  - admissibility_collapse_condition_explicit
  - cascade_condition_explicit
  - reconstruction_failure_condition_explicit
- **Failure Modes:**
  - failure_mode_suppression
  - false_stability_overclaim
  - catastrophe_theory_leakage
  - physics_failure_claim_leakage
  - complete_stability_classification_overclaim
  - collapse_without_budget_context
  - fragmentation_without_accessibility_context
  - deadlock_without_arbitration_context

## Metadata (Migrated from LAW-024)
- **Law Conditions:**
  - orientation_array_dependency_explicit
  - basin_family_definition_explicit
  - basin_overlap_condition_explicit
  - competition_condition_explicit
  - starvation_condition_explicit
  - cannibalization_condition_explicit
  - co_stabilization_condition_explicit
  - collapse_propagation_condition_explicit
- **Failure Modes:**
  - biological_ecology_overclaim
  - global_selection_overclaim
  - single_winner_collapse
  - unbounded_basin_support_assumption
  - competition_without_budget_constraint
  - collapse_propagation_suppression
  - primitive_law_reintroduction
  - physics_claim_leakage
