import json
import os
import argparse
import subprocess
import sys
from datetime import datetime

def run_math_validator(script_name):
    try:
        # Construct absolute path to handle execution from root
        script_path = os.path.join("scripts/math", script_name)
        if not os.path.exists(script_path):
            return {"status": "fail", "warnings": [f"Validator script missing: {script_name}"]}
            
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode != 0:
             return {"status": "fail", "warnings": [f"Script crashed: {result.stderr}"]}
        return json.loads(result.stdout)
    except Exception as e:
        return {"status": "fail", "warnings": [str(e)]}

def validate_math_program():
    validators = {
        "formal_objects": "validate_formal_objects.py",
        "participation_laws": "validate_participation_laws.py",
        "epsilon_null_measure": "validate_epsilon_null_measure.py",
        "continuation_laws": "validate_continuation_laws.py",
        "residue_coupling_laws": "validate_residue_coupling_laws.py",
        "operational_stability": "validate_operational_stability.py",
        "delta_selection": "validate_delta_selection.py",
        "transition_flux_convergence": "validate_transition_flux_convergence.py",
        "residue_behavior": "validate_residue_behavior.py",
        "orientation_minimization": "validate_orientation_minimization.py",
        "branch_pruning": "validate_branch_pruning.py",
        "nonlocal_transport": "validate_nonlocal_transport.py",
        "theory_induction_template": "validate_theory_induction_template.py",
        "well_posedness": "validate_well_posedness.py",
        "reconstruction": "validate_reconstruction.py",
        "reconstruction_uniqueness": "validate_reconstruction_uniqueness.py",
        "reduction_chains": "validate_reduction_chains.py",
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
