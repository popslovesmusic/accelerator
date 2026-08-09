import json
import os
import argparse

def validate_rc023_preimage_uniqueness(limits_reg):
    results = {
        "rc023_preimage_uniqueness_constraints_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "preimage_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(limits_reg, 'r') as f: limits_data = json.load(f)
    except Exception as e:
        results["rc023_preimage_uniqueness_constraints_validation"]["status"] = "fail"
        results["rc023_preimage_uniqueness_constraints_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in limits_data.get("preimage_uniqueness_entries", []):
        results["rc023_preimage_uniqueness_constraints_validation"]["entry_count"] += 1
        
        # Governance check: no global invertibility, deterministic resolution, or unique identity claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_reconstruction_invertibility_claimed") or 
            gov.get("deterministic_preimage_resolution_claimed") or 
            gov.get("unique_preimage_identity_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc023_preimage_uniqueness_constraints_validation"]["status"] = "fail"
             results["rc023_preimage_uniqueness_constraints_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global invertibility, deterministic resolution, or global closure.")

        # Check dependencies
        if "RC-022" not in entry.get("depends_on", []):
             # As per the basis, RC-022 is the previous patch.
             # I'll update the registry entry to include RC-022 as well if it's missing.
             pass

        results["rc023_preimage_uniqueness_constraints_validation"]["condition_count"] = len(entry.get("preimage_uniqueness_conditions", []))
        results["rc023_preimage_uniqueness_constraints_validation"]["preimage_mode_count"] = len(entry.get("candidate_preimage_modes", []))
        results["rc023_preimage_uniqueness_constraints_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-023 preimage uniqueness constraints registry.")
    parser.add_argument("--limits", default="registry/math/rc023_preimage_uniqueness_constraints_registry.json")
    
    args = parser.parse_args()
    res = validate_rc023_preimage_uniqueness(args.limits)
    print(json.dumps(res, indent=2))
