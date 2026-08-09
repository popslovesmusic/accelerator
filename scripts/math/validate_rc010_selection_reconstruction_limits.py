import json
import os
import argparse

def validate_rc010_reconstruction_limits(limits_reg):
    results = {
        "rc010_selection_reconstruction_limits_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "reconstruction_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(limits_reg, 'r') as f: limits_data = json.load(f)
    except Exception as e:
        results["rc010_selection_reconstruction_limits_validation"]["status"] = "fail"
        results["rc010_selection_reconstruction_limits_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in limits_data.get("reconstruction_limit_entries", []):
        results["rc010_selection_reconstruction_limits_validation"]["entry_count"] += 1
        
        # Governance check: no unique preimage recovery or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("unique_preimage_recovery_claimed") or 
            gov.get("deterministic_inversion_claimed") or 
            gov.get("exact_observable_reconstruction_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc010_selection_reconstruction_limits_validation"]["status"] = "fail"
             results["rc010_selection_reconstruction_limits_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming unique preimage, deterministic inversion, or global closure.")

        # Check dependencies
        if "RC-009" not in entry.get("depends_on", []):
             results["rc010_selection_reconstruction_limits_validation"]["status"] = "warning"
             results["rc010_selection_reconstruction_limits_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-009.")

        results["rc010_selection_reconstruction_limits_validation"]["condition_count"] = len(entry.get("reconstruction_conditions", []))
        results["rc010_selection_reconstruction_limits_validation"]["reconstruction_mode_count"] = len(entry.get("candidate_reconstruction_modes", []))
        results["rc010_selection_reconstruction_limits_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-010 selection reconstruction limits registry.")
    parser.add_argument("--limits", default="registry/math/rc010_selection_reconstruction_limits_registry.json")
    
    args = parser.parse_args()
    res = validate_rc010_reconstruction_limits(args.limits)
    print(json.dumps(res, indent=2))
