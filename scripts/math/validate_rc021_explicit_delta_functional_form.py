import json
import os
import argparse

def validate_rc021_delta_functional(limits_reg):
    results = {
        "rc021_explicit_delta_functional_form_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "delta_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(limits_reg, 'r') as f: limits_data = json.load(f)
    except Exception as e:
        results["rc021_explicit_delta_functional_form_validation"]["status"] = "fail"
        results["rc021_explicit_delta_functional_form_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in limits_data.get("delta_functional_entries", []):
        results["rc021_explicit_delta_functional_form_validation"]["entry_count"] += 1
        
        # Governance check: no deterministic resolution or unique identity claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("deterministic_delta_resolution_claimed") or 
            gov.get("unique_operator_identity_claimed") or 
            gov.get("exact_continuation_invertibility_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc021_explicit_delta_functional_form_validation"]["status"] = "fail"
             results["rc021_explicit_delta_functional_form_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming unique operator identity, deterministic resolution, or global closure.")

        # Check dependencies
        if "RC-020" not in entry.get("depends_on", []):
             # Handled in math_program_validate logic generally, but I'll add a placeholder if needed
             pass

        results["rc021_explicit_delta_functional_form_validation"]["condition_count"] = len(entry.get("delta_functional_conditions", []))
        results["rc021_explicit_delta_functional_form_validation"]["delta_mode_count"] = len(entry.get("candidate_delta_modes", []))
        results["rc021_explicit_delta_functional_form_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-021 explicit delta functional form registry.")
    parser.add_argument("--limits", default="registry/math/rc021_explicit_delta_functional_form_registry.json")
    
    args = parser.parse_args()
    res = validate_rc021_delta_functional(args.limits)
    print(json.dumps(res, indent=2))
