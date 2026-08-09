import json
import os
import argparse

def validate_rc012_epsilon_null_stability(stability_reg):
    results = {
        "rc012_epsilon_null_stability_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "threshold_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(stability_reg, 'r') as f: stability_data = json.load(f)
    except Exception as e:
        results["rc012_epsilon_null_stability_validation"]["status"] = "fail"
        results["rc012_epsilon_null_stability_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in stability_data.get("epsilon_null_stability_entries", []):
        results["rc012_epsilon_null_stability_validation"]["entry_count"] += 1
        
        # Governance check: no exact null resolution or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("exact_null_resolution_claimed") or 
            gov.get("infinitely_sharp_thresholds_claimed") or 
            gov.get("global_boundary_stability_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc012_epsilon_null_stability_validation"]["status"] = "fail"
             results["rc012_epsilon_null_stability_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming exact null resolution, global boundary stability, or global closure.")

        # Check dependencies
        if "RC-011" not in entry.get("depends_on", []):
             results["rc012_epsilon_null_stability_validation"]["status"] = "warning"
             results["rc012_epsilon_null_stability_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-011.")

        results["rc012_epsilon_null_stability_validation"]["condition_count"] = len(entry.get("epsilon_null_conditions", []))
        results["rc012_epsilon_null_stability_validation"]["threshold_mode_count"] = len(entry.get("candidate_threshold_modes", []))
        results["rc012_epsilon_null_stability_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-012 epsilon-null stability registry.")
    parser.add_argument("--stability", default="registry/math/rc012_epsilon_null_stability_registry.json")
    
    args = parser.parse_args()
    res = validate_rc012_epsilon_null_stability(args.stability)
    print(json.dumps(res, indent=2))
