import json
import os
import argparse

def validate_rc020_asymptotic_stability(asymptotic_reg):
    results = {
        "rc020_infinite_iteration_stability_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "asymptotic_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(asymptotic_reg, 'r') as f: asy_data = json.load(f)
    except Exception as e:
        results["rc020_infinite_iteration_stability_validation"]["status"] = "fail"
        results["rc020_infinite_iteration_stability_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in asy_data.get("asymptotic_stability_entries", []):
        results["rc020_infinite_iteration_stability_validation"]["entry_count"] += 1
        
        # Governance check: no global convergence, exact closure, or deterministic claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_recursive_convergence_claimed") or 
            gov.get("exact_asymptotic_identity_claimed") or 
            gov.get("deterministic_infinite_iteration_behavior_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc020_infinite_iteration_stability_validation"]["status"] = "fail"
             results["rc020_infinite_iteration_stability_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global convergence, exact closure, or determinism.")

        # Check dependencies
        if "RC-019" not in entry.get("depends_on", []):
             results["rc020_infinite_iteration_stability_validation"]["status"] = "warning"
             results["rc020_infinite_iteration_stability_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-019.")

        results["rc020_infinite_iteration_stability_validation"]["condition_count"] = len(entry.get("infinite_iteration_conditions", []))
        results["rc020_infinite_iteration_stability_validation"]["asymptotic_mode_count"] = len(entry.get("candidate_asymptotic_modes", []))
        results["rc020_infinite_iteration_stability_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-020 infinite iteration stability registry.")
    parser.add_argument("--asymptotic", default="registry/math/rc020_infinite_iteration_stability_registry.json")
    
    args = parser.parse_args()
    res = validate_rc020_asymptotic_stability(args.asymptotic)
    print(json.dumps(res, indent=2))
