import json
import os
import argparse

def validate_rc025_class_drift(drift_reg):
    results = {
        "rc025_recursive_class_membership_drift_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "classification_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(drift_reg, 'r') as f: drift_data = json.load(f)
    except Exception as e:
        results["rc025_recursive_class_membership_drift_validation"]["status"] = "fail"
        results["rc025_recursive_class_membership_drift_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in drift_data.get("recursive_class_drift_entries", []):
        results["rc025_recursive_class_membership_drift_validation"]["entry_count"] += 1
        
        # Governance check: no global invariance, deterministic classification, or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_classification_invariance_claimed") or 
            gov.get("deterministic_recursive_classification_claimed") or 
            gov.get("exact_recursive_equivalence_identity_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc025_recursive_class_membership_drift_validation"]["status"] = "fail"
             results["rc025_recursive_class_membership_drift_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global invariance, deterministic classification, or global closure.")

        # Check dependencies
        if "RC-024" not in entry.get("depends_on", []):
             results["rc025_recursive_class_membership_drift_validation"]["status"] = "warning"
             results["rc025_recursive_class_membership_drift_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-024.")

        results["rc025_recursive_class_membership_drift_validation"]["condition_count"] = len(entry.get("class_membership_conditions", []))
        results["rc025_recursive_class_membership_drift_validation"]["classification_mode_count"] = len(entry.get("candidate_classification_modes", []))
        results["rc025_recursive_class_membership_drift_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-025 recursive class membership drift registry.")
    parser.add_argument("--drift", default="registry/math/rc025_recursive_class_membership_drift_registry.json")
    
    args = parser.parse_args()
    res = validate_rc025_class_drift(args.drift)
    print(json.dumps(res, indent=2))
