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
        "rc002_derivation_closure": "validate_rc002_derivation_closure.py",
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
        "minimal_theorems": "validate_minimal_theorems.py"
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
