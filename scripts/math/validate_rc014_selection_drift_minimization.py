import json
import os
import argparse

def validate_rc014_selection_drift_minimization(drift_reg):
    results = {
        "rc014_selection_drift_minimization_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "drift_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(drift_reg, 'r') as f: drift_data = json.load(f)
    except Exception as e:
        results["rc014_selection_drift_minimization_validation"]["status"] = "fail"
        results["rc014_selection_drift_minimization_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in drift_data.get("drift_minimization_entries", []):
        results["rc014_selection_drift_minimization_validation"]["entry_count"] += 1
        
        # Governance check: no global optimization, deterministic selection, or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_trajectory_optimization_claimed") or 
            gov.get("deterministic_selection_claimed") or 
            gov.get("unique_drift_minima_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc014_selection_drift_minimization_validation"]["status"] = "fail"
             results["rc014_selection_drift_minimization_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global optimization, deterministic selection, or global closure.")

        # Check dependencies
        if "RC-013" not in entry.get("depends_on", []):
             results["rc014_selection_drift_minimization_validation"]["status"] = "warning"
             results["rc014_selection_drift_minimization_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-013.")

        results["rc014_selection_drift_minimization_validation"]["condition_count"] = len(entry.get("drift_minimization_conditions", []))
        results["rc014_selection_drift_minimization_validation"]["drift_mode_count"] = len(entry.get("candidate_drift_modes", []))
        results["rc014_selection_drift_minimization_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-014 selection drift minimization registry.")
    parser.add_argument("--drift", default="registry/math/rc014_selection_drift_minimization_registry.json")
    
    args = parser.parse_args()
    res = validate_rc014_selection_drift_minimization(args.drift)
    print(json.dumps(res, indent=2))
