import json
import os
import argparse

def validate_rc029_drift_horizon(limits_reg):
    results = {
        "rc029_selection_drift_horizon_bounds_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "horizon_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(limits_reg, 'r') as f: limits_data = json.load(f)
    except Exception as e:
        results["rc029_selection_drift_horizon_bounds_validation"]["status"] = "fail"
        results["rc029_selection_drift_horizon_bounds_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in limits_data.get("selection_drift_horizon_entries", []):
        results["rc029_selection_drift_horizon_bounds_validation"]["entry_count"] += 1
        
        # Governance check: no global optimization or deterministic convergence claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_drift_optimization_claimed") or 
            gov.get("deterministic_horizon_convergence_claimed") or 
            gov.get("exact_recursive_drift_elimination_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc029_selection_drift_horizon_bounds_validation"]["status"] = "fail"
             results["rc029_selection_drift_horizon_bounds_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global optimization, deterministic horizon convergence, or global closure.")

        # Check dependencies
        if "RC-028" not in entry.get("depends_on", []):
             results["rc029_selection_drift_horizon_bounds_validation"]["status"] = "warning"
             results["rc029_selection_drift_horizon_bounds_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-028.")

        results["rc029_selection_drift_horizon_bounds_validation"]["condition_count"] = len(entry.get("selection_drift_horizon_conditions", []))
        results["rc029_selection_drift_horizon_bounds_validation"]["horizon_mode_count"] = len(entry.get("candidate_horizon_modes", []))
        results["rc029_selection_drift_horizon_bounds_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-029 selection drift horizon bounds registry.")
    parser.add_argument("--limits", default="registry/math/rc029_selection_drift_horizon_bounds_registry.json")
    
    args = parser.parse_args()
    res = validate_rc029_drift_horizon(args.limits)
    print(json.dumps(res, indent=2))
