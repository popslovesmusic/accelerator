import json
import os
import argparse

def validate_rc013_delta_composition_closure(composition_reg):
    results = {
        "rc013_delta_composition_closure_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "composition_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(composition_reg, 'r') as f: comp_data = json.load(f)
    except Exception as e:
        results["rc013_delta_composition_closure_validation"]["status"] = "fail"
        results["rc013_delta_composition_closure_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in comp_data.get("delta_composition_closure_entries", []):
        results["rc013_delta_composition_closure_validation"]["entry_count"] += 1
        
        # Governance check: no exact closure or deterministic claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("exact_operator_identity_claimed") or 
            gov.get("exact_operator_closure_claimed") or 
            gov.get("deterministic_delta_claimed") or
            gov.get("unique_continuation_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc013_delta_composition_closure_validation"]["status"] = "fail"
             results["rc013_delta_composition_closure_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming exact closure, identity, or determinism.")

        # Check dependencies
        if "RC-010" not in entry.get("depends_on", []):
             results["rc013_delta_composition_closure_validation"]["status"] = "warning"
             results["rc013_delta_composition_closure_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-010.")

        results["rc013_delta_composition_closure_validation"]["condition_count"] = len(entry.get("composition_conditions", []))
        results["rc013_delta_composition_closure_validation"]["composition_mode_count"] = len(entry.get("candidate_composition_modes", []))
        results["rc013_delta_composition_closure_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-013 delta composition closure registry.")
    parser.add_argument("--composition", default="registry/math/rc013_delta_composition_closure_registry.json")
    
    args = parser.parse_args()
    res = validate_rc013_delta_composition_closure(args.composition)
    print(json.dumps(res, indent=2))
