import json
import os
import argparse
import subprocess
import sys
from datetime import datetime

def run_math_validator(script_spec):
    try:
        # spec can be a simple script name or script + args
        parts = script_spec.split(' ', 1)
        script_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        # Construct absolute path to handle execution from root
        script_path = os.path.join("scripts/math", script_name)
        if not os.path.exists(script_path):
            return {"status": "fail", "warnings": [f"Validator script missing: {script_name}"]}
            
        cmd = [sys.executable, script_path]
        if args:
            # Simple split for space-separated args; may need more robustness for complex args
            cmd.extend(args.split(' '))
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
             return {"status": "fail", "warnings": [f"Script crashed: {result.stderr}"]}
        return json.loads(result.stdout)
    except Exception as e:
        return {"status": "fail", "warnings": [str(e)]}

def validate_math_program():
    validators = {
        "formal_objects": "validate_formal_objects.py",
        "participation_laws": "validate_participation_laws.py",
        "participation_measure_refinement": "validate_participation_measure_refinement.py",
        "epsilon_null_measure": "validate_epsilon_null_measure.py",
        "boundary_case_classification": "validate_boundary_case_classification.py",
        "continuation_laws": "validate_continuation_laws.py",
        "residue_coupling_laws": "validate_residue_coupling_laws.py",
        "operational_stability": "validate_operational_stability.py",
        "delta_selection": "validate_delta_selection.py",
        "transition_flux_convergence": "validate_transition_flux_convergence.py",
        "residue_behavior": "validate_residue_behavior.py",
        "residue_conservation": "validate_residue_conservation.py",
        "orientation_minimization": "validate_orientation_minimization.py",
        "branch_pruning": "validate_branch_pruning.py",
        "nonlocal_transport": "validate_nonlocal_transport.py",
        "theory_induction_template": "validate_theory_induction_template.py",
        "quantifier_explicitness": "validate_quantifier_explicitness.py",
        "operator_composition": "validate_operator_composition.py",
        "equivalence_relations": "validate_equivalence_relations.py",
        "equivalence_properties": "validate_equivalence_properties.py",
        "operator_functional_forms": "validate_operator_functional_forms.py",
        "symbolic_reduction_chains": "validate_symbolic_reduction_chains.py",
        "reduction_step_formalization": "validate_reduction_step_formalization.py",
        "symbolic_derivation_closure": "validate_symbolic_derivation_closure.py",
        "proof_elevation_campaign": "validate_proof_elevation_campaign.py",
        "recursive_convergence": "validate_recursive_convergence.py",
        "recursive_transport_closure": "validate_recursive_transport_closure.py",
        "selection_uniqueness": "validate_selection_uniqueness.py",
        "mt001_readiness": "validate_mt001_formal_candidate_readiness.py",
        "mt001_theorem_consolidation": "validate_mt001_theorem_consolidation.py",
        "mt002_readiness": "validate_mt002_formal_candidate_readiness.py",
        "mt002_theorem_consolidation": "validate_mt002_theorem_consolidation.py",
        "mt003_readiness": "validate_mt003_formal_candidate_readiness.py",
        "mt003_theorem_consolidation": "validate_mt003_theorem_consolidation.py",
        "formal_proof_artifacts": "validate_formal_proof_artifacts.py",
        "formal_verification_artifacts": "validate_formal_verification_artifacts.py",
        "theorem_proof_strengthening": "validate_theorem_proof_strengthening.py",
        "operational_stability_baseline": "validate_operational_stability_baseline.py",
        "phase_3_stability": "validate_phase_3_stability.py",
        "phase_3_test_results": "validate_phase_3_test_results.py --path outputs/math_tests/phase_3_stability_results.json",
        "well_posedness": "validate_well_posedness.py",
        "reconstruction": "validate_reconstruction.py",
        "reconstruction_uniqueness": "validate_reconstruction_uniqueness.py",
        "rc001_derivation_closure": "validate_rc001_derivation_closure.py",
        "rc001_step02_derivation_supported": "validate_rc001_step02_derivation_supported.py",
        "rc001_proof_candidate_gap_audit": "validate_rc001_proof_candidate_gap_audit.py",
        "proof_candidate_review_infrastructure": "validate_proof_candidate_review_infrastructure.py",
        "proof_candidate_stress_testing": "validate_proof_candidate_stress_tests.py",
        "asymptotic_incompleteness_mapping": "validate_asymptotic_incompleteness_mapping.py",
        "hidden_proof_blocker_discovery": "validate_hidden_proof_blocker_discovery.py",
        "structural_incompleteness_classification": "validate_structural_incompleteness_classification.py",
        "irreducible_incompleteness_analysis": "validate_irreducible_incompleteness_analysis.py",
        "global_closure_impossibility_analysis": "validate_global_closure_impossibility_analysis.py",
        "continuation_reconstruction_asymmetry": "validate_continuation_reconstruction_asymmetry.py",
        "xi_reconstruction_bounds": "validate_xi_reconstruction_bounds.py",
        "information_loss_geometry": "validate_information_loss_geometry.py",
        "recursive_loss_accumulation": "validate_recursive_loss_accumulation.py",
        "reconstruction_equivalence_geometry": "validate_reconstruction_equivalence_geometry.py",
        "orientation_sensitive_equivalence_geometry": "validate_orientation_sensitive_equivalence_geometry.py",
        "strict_preimage_uniqueness_constraints": "validate_strict_preimage_uniqueness_constraints.py",
        "admissibility_boundary_geometry": "validate_admissibility_boundary_geometry.py",
        "admissibility_topology_transitions": "validate_admissibility_topology_transitions.py",
        "rc002_derivation_closure": "validate_rc002_derivation_closure.py",
        "rc002_counterexample_obligation": "validate_rc002_counterexample_obligation.py",
        "rc003_recursive_fixed_point_scaffold": "validate_rc003_recursive_fixed_point_scaffold.py",
        "rc004_recurrence_basin_stability": "validate_rc004_recurrence_basin_stability.py",
        "rc005_selection_stability_under_recursion": "validate_rc005_selection_stability_under_recursion.py",
        "rc006_degenerate_minima_resolution": "validate_rc006_degenerate_minima_resolution.py",
        "rc007_nonlocal_transport_closure": "validate_rc007_nonlocal_transport_closure.py",
        "rc008_orientation_sensitivity_representation": "validate_rc008_orientation_sensitivity_representation.py",
        "rc009_residue_transport_conservation": "validate_rc009_residue_transport_conservation.py",
        "rc010_selection_reconstruction_limits": "validate_rc010_selection_reconstruction_limits.py",
        "rc011_branch_explosion_limits": "validate_rc011_branch_explosion_limits.py",
        "rc012_epsilon_null_stability": "validate_rc012_epsilon_null_stability.py",
        "rc013_delta_composition_closure": "validate_rc013_delta_composition_closure.py",
        "rc014_selection_drift_minimization": "validate_rc014_selection_drift_minimization.py",
        "rc015_participation_measure_structure": "validate_rc015_participation_measure_structure.py",
        "rc016_local_selection_uniqueness": "validate_rc016_local_selection_uniqueness.py",
        "rc017_csi_metric_decay_structure": "validate_rc017_csi_metric_decay_structure.py",
        "rc018_residue_update_legality": "validate_rc018_residue_update_legality.py",
        "rc019_selection_retention_interaction": "validate_rc019_selection_retention_interaction.py",
        "rc020_infinite_iteration_stability": "validate_rc020_infinite_iteration_stability.py",
        "rc021_explicit_delta_functional_form": "validate_rc021_explicit_delta_functional_form.py",
        "rc022_nonlocal_transport_closure_limits": "validate_rc022_nonlocal_transport_closure_limits.py",
        "rc023_preimage_uniqueness_constraints": "validate_rc023_preimage_uniqueness_constraints.py",
        "rc024_window_perturbation_flux_bounds": "validate_rc024_window_perturbation_flux_bounds.py",
        "rc025_recursive_class_membership_drift": "validate_rc025_recursive_class_membership_drift.py",
        "rc026_degenerate_minima_tiebreak_dynamics": "validate_rc026_degenerate_minima_tiebreak_dynamics.py",
        "rc027_residue_transport_dissipation_bounds": "validate_rc027_residue_transport_dissipation_bounds.py",
        "rc028_orientation_sensitivity_explicitness": "validate_rc028_orientation_sensitivity_explicitness.py",
        "rc029_selection_drift_horizon_bounds": "validate_rc029_selection_drift_horizon_bounds.py",
        "rc030_branch_pruning_scale_sensitivity": "validate_rc030_branch_pruning_scale_sensitivity.py",
        "rc031_delta_multi_branch_composition": "validate_rc031_delta_multi_branch_composition.py",
        "selection_reconstruction": "validate_selection_reconstruction.py",
        "reduction_chains": "validate_reduction_chains.py",
        "pi_a_idempotence": "validate_pi_a_idempotence.py",
        "navt_identity": "validate_navt_identity.py",
        "continuation_nonempty_image": "validate_continuation_nonempty_image.py",
        "minimal_theorems": "validate_minimal_theorems.py",
        "sum_operator_convergence": "validate_sum_operator_convergence.py",
        "formal_derivation_step_elevation": "validate_formal_derivation_step_elevation.py",
        "rc020_infinite_iteration_strengthening": "validate_rc020_infinite_iteration_strengthening.py",
        "rc002_symbolic_support_elevation": "validate_rc002_symbolic_support_elevation.py",
        "rc002_derivation_supported": "validate_rc002_derivation_supported.py",
        "rc002_proof_candidate_review_ready": "validate_rc002_proof_candidate_review_ready.py",
        "audit001_numerical_correctness_triage": "validate_audit001_numerical_correctness_triage.py",
        "audit002_dependency_reproducibility_lock": "validate_audit002_dependency_reproducibility_lock.py",
        "audit003_tda_adjacency_threshold": "validate_audit003_tda_adjacency_threshold.py",
        "audit004_rd_boundary_scaling_policy": "validate_audit004_rd_boundary_scaling_policy.py",
        "audit005_poisson_sign_convention": "validate_audit005_poisson_sign_convention.py",
        "audit006_structural_euler_stability_bounds": "validate_audit006_structural_euler_stability_bounds.py",
        "audit007_implementation_triage_closure": "validate_audit007_implementation_triage_closure.py",
        "law001_explicit_delta_functional_form": "validate_law001_explicit_delta_functional_form.py",
        "law002_pi_a_admissibility_projection_law": "validate_law002_pi_a_admissibility_projection_law.py",
        "law003_navt_transport_operator_law": "validate_law003_navt_transport_operator_law.py",
        "law004_csi_summation_finite_flux_law": "validate_law004_csi_summation_finite_flux_law.py",
        "law005_admissibility_boundary_transition_law": "validate_law005_admissibility_boundary_transition_law.py",
        "law006_orientation_array_distinction_law": "validate_law006_orientation_array_distinction_law.py",
        "law007_recursion_density_ordering_law": "validate_law007_recursion_density_ordering_law.py",
        "law008_array_topology_accessibility_law": "validate_law008_array_topology_accessibility_law.py",
        "law009_apparent_temporality_projection_law": "validate_law009_apparent_temporality_projection_law.py",
        "law010_apparent_geometry_projection_law": "validate_law010_apparent_geometry_projection_law.py",
        "law011_stabilized_reconciliation_basin_law": "validate_law011_stabilized_reconciliation_basin_law.py",
        "law012_lawlike_persistence_channel_law": "validate_law012_lawlike_persistence_channel_law.py",
        "law013_channel_fracture_transition_law": "validate_law013_channel_fracture_transition_law.py",
        "law014_channel_competition_selection_law": "validate_law014_channel_competition_selection_law.py",
        "law015_channel_memory_reinforcement_history_law": "validate_law015_channel_memory_reinforcement_history_law.py",
        "law016_channel_reconstruction_asymmetry_law": "validate_law016_channel_reconstruction_asymmetry_law.py",
        "law017_continuation_compression_equivalence_law": "validate_law017_continuation_compression_equivalence_law.py",
        "law018_accessibility_horizon_reachability_limit_law": "validate_law018_accessibility_horizon_reachability_limit_law.py",
        "law019_local_causality_accessibility_order_law": "validate_law019_local_causality_accessibility_order_law.py",
        "law020_identity_persistence_under_mutation_law": "validate_law020_identity_persistence_under_mutation_law.py",
        "law021_finite_admissibility_budget_law": "validate_law021_finite_admissibility_budget_law.py",
        "law022_perturbation_error_dynamics_law": "validate_law022_perturbation_error_dynamics_law.py",
        "law023_reconstruction_limited_observability_law": "validate_law023_reconstruction_limited_observability_law.py",
        "law024_competitive_basin_ecology_law": "validate_law024_competitive_basin_ecology_law.py",
        "law025_persistence_decay_forgetting_law": "validate_law025_persistence_decay_forgetting_law.py",
        "law026_metastability_temporary_lawlike_regime_law": "validate_law026_metastability_temporary_lawlike_regime_law.py",
        "law027_admissibility_phase_transition_law": "validate_law027_admissibility_phase_transition_law.py",
        "law028_topological_invariants_under_continuation_law": "validate_law028_topological_invariants_under_continuation_law.py",
        "law029_recursive_arbitration_conflict_resolution_law": "validate_law029_recursive_arbitration_conflict_resolution_law.py",
        "law030_multiscale_coherence_transfer_law": "validate_law030_multiscale_coherence_transfer_law.py",
        "law031_discrete_continuous_transition_mechanics_law": "validate_law031_discrete_continuous_transition_mechanics_law.py",
        "law032_recursive_failure_mode_taxonomy_law": "validate_law032_recursive_failure_mode_taxonomy_law.py",
        "law033_hidden_topology_inaccessible_continuation_domains_law": "validate_law033_hidden_topology_inaccessible_continuation_domains_law.py",
        "law034_continuation_grammar_compositional_structure_law": "validate_law034_continuation_grammar_compositional_structure_law.py",
        "meta005_law_program_consolidation_atlas": "validate_meta005_law_program_consolidation_atlas.py",
        "meta006_theorem_target_selection": "validate_meta006_theorem_target_selection.py",
        "mt_law_a_foundation": "validate_mt_law_a_definition_tightening.py",
        "mt_law_a_counterexamples": "validate_mt_law_a_counterexample_obligations.py",
        "mt_law_a_semantic_integrity": "validate_mt_law_a_semantic_integrity.py",
        "mt_law_a_primitive_detection": "detect_mt_law_a_forbidden_primitives.py",
        "mt_law_a_reference_models": "validate_mt_law_a_reference_models.py",
        "mt_law_a_multi_seed_stability": "validate_mt_law_a_multi_seed_stability.py",
        "mt_law_a_threshold_sensitivity": "validate_mt_law_a_threshold_sensitivity.py",
        "mt_law_a_cross_mechanism_equivalence": "validate_mt_law_a_cross_mechanism_equivalence.py",
        "mt_law_a_scaffold": "validate_mt_law_a_formal_lemma_scaffold.py",
        "mt_law_a_obligations": "validate_mt_law_a_proof_obligation_mapping.py",
        "mt_law_a_sketch": "validate_mt_law_a_local_proof_sketch.py",
        "mt_law_a_stress": "validate_mt_law_a_counterexample_stress_domains.py",
        "mt_law_a_discharge_candidates": "validate_mt_law_a_obligation_discharge_candidate.py",
        "mt_law_a_local_validation": "validate_mt_law_a_local_discharge_validation.py",
        "mt_law_a_restricted_domain": "validate_mt_law_a_restricted_domain_lemma_candidate.py",
        "mt_law_a_excluded_domains": "validate_mt_law_a_excluded_domains.py",
        "mt_law_a_reentry_conditions": "validate_mt_law_a_reentry_conditions.py",
        "mt_law_a_boundary_consistency": "validate_mt_law_a_scope_boundary_consistency.py",
        "mt_law_a_restricted_review": "validate_mt_law_a_restricted_lemma_review.py",
        "mt_law_a_stability_consolidation": "validate_mt_law_a_restricted_domain_stability.py",
        "mt_law_a_local_readiness": "validate_mt_law_a_local_theorem_readiness.py",
        "mt_law_a_ts4_review_gate": "validate_mt_law_a_ts4_review_gate.py",
        "mt_law_a_ts4_restricted_review": "validate_mt_law_a_ts4_restricted_domain_review.py",
        "mt_law_a_ts4_stability_reconciliation": "validate_mt_law_a_ts4_stability_reconciliation.py",
        "mt_law_a_ts4_boundary_hardening": "validate_mt_law_a_ts4_boundary_hardening.py",
        "mt_law_a_foundations_audit": "validate_mt_law_a_foundations_dependency_audit.py",
        "operator_discipline": "validate_operator_discipline.py",
        "ltc_selection_gate": "validate_local_theorem_candidate_selection_gate.py",
        "pi_a_persistence_scaffold": "validate_pi_a_local_persistence_proof_scaffold.py",
        "pi_a_boundary_mapping": "validate_pi_a_proof_obligation_boundary_mapping.py",
        "mt_law_a_foundations_resolution": "validate_mt_law_a_foundations_resolution.py",
        "pi_a_proof_attempt": "validate_pi_a_local_proof_attempt.py",
        "pi_a_counterexample_campaign": "validate_pi_a_counterexample_injection_campaign.py",
        "pi_a_reconciliation_atlas": "validate_pi_a_counterexample_reconciliation_atlas.py",
        "recursive_basin_classification": "validate_recursive_stability_basin_classification.py",
        "stable_basin_eligibility": "validate_stable_basin_proof_eligibility_filter.py",
        "restricted_proof_segment": "validate_restricted_local_proof_segment.py",
        "restricted_proof_consistency": "validate_restricted_local_proof_consistency_audit.py",
        "restricted_stability_consolidation": "validate_restricted_local_stability_consolidation.py",
        "local_theorem_readiness": "validate_local_theorem_readiness_audit.py",
        "ts4_review_gate": "validate_ts4_review_gate.py",
        "ts4_restricted_review": "validate_ts4_restricted_local_review.py",
        "ts4_stability_reconciliation": "validate_ts4_stability_reconciliation.py",
        "ts4_boundary_hardening": "validate_ts4_boundary_hardening.py",
        "mpf_sim_001_stability": "validate_mpf_sim_001.py",
        "mpf_sim_002_boundary_inflation": "validate_mpf_sim_002_boundary_inflation.py",
        "mpf_sim_003_metastability": "validate_mpf_sim_003_metastability_oscillation.py",
        "mpf_sim_004_lambda": "validate_mpf_sim_004_lambda_fixed_point.py",
        "mpf_sim_005_phase_transition": "validate_mpf_sim_005_admissibility_phase_transition.py",
        "mpf_sim_006_atlas": "validate_mpf_sim_006_cross_simulation_evidence_atlas.py",
        "mpf_sim_007_repair_queue": "validate_mpf_sim_007_evidence_reconciliation_queue.py",
        "mpf_sim_008_recovery": "validate_mpf_sim_008_admissibility_recovery.py",
        "mpf_sim_009_memory": "validate_mpf_sim_009_recursive_constraint_memory.py",
        "mpf_sim_011_hysteresis": "validate_mpf_sim_011_admissibility_hysteresis.py",
        "mpf_sim_012_geology": "validate_mpf_sim_012_constraint_geology_atlas.py",
        "mpf_sim_013_impact_audit": "validate_mpf_sim_013_constraint_geology_proof_impact.py",
        "mpf_dep_001_reconciliation": "validate_interrupted_series_dependency_reconciliation.py",
        "mpf_dep_002_rc_map": "validate_rc_series_recovery_closure_map.py",
        "mpf_dep_003_rc_repair": "validate_rc_repair_queue_execution.py",
        "mpf_dep_004_firewall": "validate_recursive_inheritance_firewall.py",
        "mpf_dep_005_admission": "validate_recursive_dependency_admission_gate.py",
        "mpf_dep_006_closure_audit": "validate_dependency_repair_closure_audit.py",
        "mpf_res_001_taxonomy": "validate_unresolved_structure_taxonomy.py",
        "mpf_res_002_queue": "validate_unresolved_structure_resolution_queue.py",
        "mpf_res_003_lifecycle": "validate_resolution_lifecycle_governance.py",
        "mpf_res_005_drift_audit": "validate_recursive_governance_drift_registry.py",
        "mpf_res_006_containment_stress": "validate_recursive_containment_registry.py",
        "mpf_res_006_failure_geometry": "validate_failure_geometry_registry.py",
        "mpf_res_006_boundary_isolation": "validate_boundary_object_isolation.py",
        "mpf_res_006_quarantine_integrity": "validate_recursive_quarantine_integrity.py",
        "mpf_res_006_cross_lane_containment": "validate_cross_lane_containment.py",
        "mpf_res_007_adaptive_incompleteness": "validate_adaptive_incompleteness_registry.py",
        "mpf_res_007_irreducible_preservation": "validate_irreducible_preservation_policy.py",
        "mpf_res_008_ecology_registry": "validate_recursive_boundary_ecology_registry.py",
        "mpf_res_008_topology": "validate_boundary_interaction_topology.py",
        "mpf_res_008_pressure_fields": "validate_epistemic_pressure_fields.py",
        "mpf_res_009_climate_registry": "validate_epistemic_climate_registry.py",
        "mpf_res_009_climate_thresholds": "validate_climate_thresholds.py",
        "mpf_res_010_resumption_gate": "validate_governed_resumption_readiness_gate.py",
        "mpf_res_010_topology_constraints": "validate_topology_resumption_constraints.py",
        "mpf_topo_001_restart": "validate_restricted_local_topology_registry.py",
        "mpf_topo_001_constraints": "validate_local_topology_constraints.py",
        "mpf_topo_002_bounded_transition": "validate_bounded_transition_registry.py",
        "mpf_topo_002_transition_constraints": "validate_local_transition_constraints.py",
        "mpf_topo_003_reconfiguration": "validate_constraint_reconfiguration_registry.py",
        "mpf_topo_003_reconfig_constraints": "validate_reconfiguration_constraints.py",
        "mpf_topo_003_topology_maps": "validate_local_constraint_topology_maps.py",
        "mpf_topo_004_orientation_field": "validate_orientation_field_registry.py",
        "mpf_topo_004_orientation_constraints": "validate_orientation_constraints.py",
        "mpf_topo_004_gradient_maps": "validate_orientation_gradient_maps.py",
        "mpf_topo_005_corridor_analysis": "validate_admissibility_corridor_registry.py",
        "mpf_topo_005_corridor_constraints": "validate_corridor_constraints.py",
        "mpf_topo_005_pathway_maps": "validate_admissibility_pathway_maps.py",
        "mpf_topo_006_basin_formation": "validate_constraint_basin_registry.py",
        "mpf_topo_006_basin_constraints": "validate_basin_constraints.py",
        "mpf_topo_006_basin_maps": "validate_constraint_basin_maps.py",
        "mpf_topo_core_001_primitives": "validate_topology_primitives.py",
        "mpf_topo_bound_001_boundaries": "validate_topology_boundary_conditions.py",
        "mpf_topo_trans_001_transitions": "validate_topology_transition_mapping.py",
        "mpf_topo_reconfig_001_audit": "validate_topology_reconfiguration.py",
        "mpf_topo_dist_001_distinctions": "validate_topology_behavioral_distinctions.py",
        "mpf_topo_007_flow": "validate_constraint_flow_registry.py",
        "mpf_topo_007_flow_constraints": "validate_flow_constraints.py",
        "mpf_topo_007_flow_mapping": "validate_flow_mapping.py",
        "mpf_palg_001_phase": "validate_process_algebra_phase.py",
        "mpf_palg_002_bc_equivalence": "validate_residue_bound_equivalence_operator.py",
        "mpf_palg_003_exclusion": "validate_exclusion_admissibility_operator.py",
        "mpf_palg_004_polarity_preservation": "validate_recursive_polarity_preservation_law.py",
        "mpf_palg_005_non_separability": "validate_aspect_non_separability_principle.py",
        "mpf_palg_006_projection_governance": "validate_projection_boundary_governance.py",
        "mpf_palg_007_aspect_trace": "validate_aspect_relation_trace_schema.py",
        "mpf_palg_008_whole_relation_gate": "validate_whole_relation_gate.py",
        "mpf_palg_009_minimal_expressions": "validate_process_algebra_minimal_expression_set.py",
        "mpf_palg_010_expansion_queue": "validate_process_algebra_expansion_review_queue.py",
        "mpf_palg_011_nested_review": "validate_nested_whole_relation_candidate_review.py",
        "mpf_palg_012_semantics_governance": "validate_nested_relation_semantics_governance.py",
        "mpf_palg_013_projected_equality": "validate_projection_derived_equality.py",
        "mpf_palg_014_projected_implication": "validate_projection_derived_implication.py",
        "mpf_palg_015_projected_composition": "validate_projection_derived_composition.py",
        "mpf_palg_016_projected_biconditional": "validate_projection_derived_biconditional.py",
        "mpf_palg_017_loss_matrix": "validate_projection_loss_accounting_matrix.py",
        "mpf_palg_018_simultaneity": "validate_recursive_aspect_simultaneity.py",
        "mpf_palg_019_flattening_risk": "validate_whole_relation_flattening_risk_audit.py",
        "mpf_palg_021_projection_operators": "validate_projection_operator_formalization.py",
        "mpf_palg_022_projection_depth": "validate_projection_depth_taxonomy.py",
        "mpf_palg_023_recoverability_limits": "validate_projection_recoverability_limits.py",
        "mpf_palg_024_multi_projection_coherence": "validate_multi_projection_coherence.py",
        "mpf_palg_025_projection_geometry": "validate_projection_induced_geometry.py",
        "mpf_palg_026_persistence_dynamics": "validate_projection_persistence_dynamics.py",
        "mpf_palg_027_orientation_dynamics": "validate_projection_induced_orientation_dynamics.py",
        "mpf_palg_028_failure_atlas": "validate_projection_failure_mode_atlas.py",
        "mpf_palg_029_stress_scaffold": "validate_projection_coherence_stress_test_scaffold.py",
        "mpf_palg_030_consolidation_review": "validate_projection_mechanics_consolidation_review.py",
        "mpf_palg_031_bridge_phase": "validate_restricted_projection_bridge_phase.py",
        "mpf_palg_032_qm_domain": "validate_qm_like_projection_domain.py"
    }

    report = {
        "math_program_validation": {
            "status": "pass",
            "timestamp": datetime.now().isoformat(),
            "validators_run": [],
            "domain_status": {},
            "readiness_summary": {
                "ready_for_local_theorem_work": False,
                "ready_for_global_closure_claims": False,
                "ready_for_physics_claims": False
            },
            "closure_gaps": [],
            "open_questions": [],
            "warnings": []
        }
    }

    all_pass = True
    for domain, script in validators.items():
        report["math_program_validation"]["validators_run"].append(script)
        res = run_math_validator(script)
        
        # Determine specific result key (scripts return nested dicts)
        # e.g. "formal_object_validation"
        sub_key = None
        for k in res.keys():
            if "_validation" in k:
                sub_key = k
                break
        
        domain_res = res[sub_key] if sub_key else res
        report["math_program_validation"]["domain_status"][domain] = domain_res
        
        if domain_res.get("status") == "fail":
            all_pass = False
            report["math_program_validation"]["status"] = "fail"
        elif domain_res.get("status") == "warning" and report["math_program_validation"]["status"] == "pass":
            report["math_program_validation"]["status"] = "warning"

        # Collect gaps/questions
        report["math_program_validation"]["closure_gaps"].extend(domain_res.get("closure_gaps", []))
        report["math_program_validation"]["open_questions"].extend(domain_res.get("open_questions", []))
        report["math_program_validation"]["warnings"].extend(domain_res.get("warnings", []))

    # Calculate readiness
    # ready_for_local_theorem_work: True if status is pass or warning (no fails)
    if report["math_program_validation"]["status"] in ["pass", "warning"]:
        report["math_program_validation"]["readiness_summary"]["ready_for_local_theorem_work"] = True
    
    # Other readiness fields remain False by default per patch mandates

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consolidated Math Program Validation.")
    parser.add_argument("--out", help="Path to save validation report.")
    args = parser.parse_args()
    
    report = validate_math_program()
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Validation report saved to {args.out}")
    else:
        print(json.dumps(report, indent=2))
