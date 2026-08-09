import json
import os
import argparse

def validate_rc028_orientation_sensitivity(orientation_reg):
    results = {
        "rc028_orientation_sensitivity_explicitness_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "orientation_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(orientation_reg, 'r') as f: ori_data = json.load(f)
    except Exception as e:
        results["rc028_orientation_sensitivity_explicitness_validation"]["status"] = "fail"
        results["rc028_orientation_sensitivity_explicitness_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in ori_data.get("orientation_explicitness_entries", []):
        results["rc028_orientation_sensitivity_explicitness_validation"]["entry_count"] += 1
        
        # Governance check: no global alignment, deterministic minimization, or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_orientation_alignment_claimed") or 
            gov.get("deterministic_directional_minimization_claimed") or 
            gov.get("exact_orientation_transport_identity_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc028_orientation_sensitivity_explicitness_validation"]["status"] = "fail"
             results["rc028_orientation_sensitivity_explicitness_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global alignment, deterministic minimization, or global closure.")

        # Check dependencies
        if "RC-027" not in entry.get("depends_on", []):
             results["rc028_orientation_sensitivity_explicitness_validation"]["status"] = "warning"
             results["rc028_orientation_sensitivity_explicitness_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-027.")

        results["rc028_orientation_sensitivity_explicitness_validation"]["condition_count"] = len(entry.get("orientation_explicitness_conditions", []))
        results["rc028_orientation_sensitivity_explicitness_validation"]["orientation_mode_count"] = len(entry.get("candidate_orientation_modes", []))
        results["rc028_orientation_sensitivity_explicitness_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-028 orientation sensitivity explicitness registry.")
    parser.add_argument("--orientation", default="registry/math/rc028_orientation_sensitivity_explicitness_registry.json")
    
    args = parser.parse_args()
    res = validate_rc028_orientation_sensitivity(args.orientation)
    print(json.dumps(res, indent=2))
