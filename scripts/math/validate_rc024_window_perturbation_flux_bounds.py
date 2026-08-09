import json
import os
import argparse

def validate_rc024_window_perturbation(limits_reg):
    results = {
        "rc024_window_perturbation_flux_bounds_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "flux_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(limits_reg, 'r') as f: limits_data = json.load(f)
    except Exception as e:
        results["rc024_window_perturbation_flux_bounds_validation"]["status"] = "fail"
        results["rc024_window_perturbation_flux_bounds_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in limits_data.get("window_perturbation_entries", []):
        results["rc024_window_perturbation_flux_bounds_validation"]["entry_count"] += 1
        
        # Governance check: no global flux-boundedness or deterministic stability claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_flux_boundedness_claimed") or 
            gov.get("deterministic_window_stability_claimed") or 
            gov.get("exact_boundary_continuity_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc024_window_perturbation_flux_bounds_validation"]["status"] = "fail"
             results["rc024_window_perturbation_flux_bounds_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global flux boundedness, deterministic window stability, or global closure.")

        # Check dependencies
        if "RC-023" not in entry.get("depends_on", []):
             results["rc024_window_perturbation_flux_bounds_validation"]["status"] = "warning"
             results["rc024_window_perturbation_flux_bounds_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-023.")

        results["rc024_window_perturbation_flux_bounds_validation"]["condition_count"] = len(entry.get("window_perturbation_conditions", []))
        results["rc024_window_perturbation_flux_bounds_validation"]["flux_mode_count"] = len(entry.get("candidate_flux_modes", []))
        results["rc024_window_perturbation_flux_bounds_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-024 window perturbation flux bounds registry.")
    parser.add_argument("--limits", default="registry/math/rc024_window_perturbation_flux_bounds_registry.json")
    
    args = parser.parse_args()
    res = validate_rc024_window_perturbation(args.limits)
    print(json.dumps(res, indent=2))
