import json
import os
import argparse

def validate_rc008_orientation_sensitivity(orientation_reg):
    results = {
        "rc008_orientation_sensitivity_representation_validation": {
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
        results["rc008_orientation_sensitivity_representation_validation"]["status"] = "fail"
        results["rc008_orientation_sensitivity_representation_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in ori_data.get("orientation_sensitivity_entries", []):
        results["rc008_orientation_sensitivity_representation_validation"]["entry_count"] += 1
        
        # Governance check: no absolute frame, unique resolution, or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("absolute_reference_frame_claimed") or 
            gov.get("unique_orientation_resolution_claimed") or 
            gov.get("infinite_recursive_alignment_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc008_orientation_sensitivity_representation_validation"]["status"] = "fail"
             results["rc008_orientation_sensitivity_representation_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming absolute frames, unique resolution, or global closure.")

        # Check dependencies
        if "RC-007" not in entry.get("depends_on", []):
             results["rc008_orientation_sensitivity_representation_validation"]["status"] = "warning"
             results["rc008_orientation_sensitivity_representation_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-007.")

        results["rc008_orientation_sensitivity_representation_validation"]["condition_count"] = len(entry.get("orientation_conditions", []))
        results["rc008_orientation_sensitivity_representation_validation"]["orientation_mode_count"] = len(entry.get("candidate_orientation_modes", []))
        results["rc008_orientation_sensitivity_representation_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-008 orientation sensitivity registry.")
    parser.add_argument("--orientation", default="registry/math/rc008_orientation_sensitivity_representation_registry.json")
    
    args = parser.parse_args()
    res = validate_rc008_orientation_sensitivity(args.orientation)
    print(json.dumps(res, indent=2))
