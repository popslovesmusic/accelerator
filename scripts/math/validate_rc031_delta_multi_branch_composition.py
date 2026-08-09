import json
import os
import argparse

def validate_rc031_multi_branch_composition(composition_reg):
    results = {
        "rc031_delta_multi_branch_composition_validation": {
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
        results["rc031_delta_multi_branch_composition_validation"]["status"] = "fail"
        results["rc031_delta_multi_branch_composition_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in comp_data.get("multi_branch_composition_entries", []):
        results["rc031_delta_multi_branch_composition_validation"]["entry_count"] += 1
        
        # Governance check: no deterministic operator composition or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("deterministic_operator_composition_claimed") or 
            gov.get("global_continuation_chain_uniqueness_claimed") or 
            gov.get("exact_compositional_invertibility_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc031_delta_multi_branch_composition_validation"]["status"] = "fail"
             results["rc031_delta_multi_branch_composition_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming deterministic operator composition, global uniqueness, or global closure.")

        # Check dependencies
        if "RC-030" not in entry.get("depends_on", []):
             results["rc031_delta_multi_branch_composition_validation"]["status"] = "warning"
             results["rc031_delta_multi_branch_composition_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-030.")

        results["rc031_delta_multi_branch_composition_validation"]["condition_count"] = len(entry.get("multi_branch_composition_conditions", []))
        results["rc031_delta_multi_branch_composition_validation"]["composition_mode_count"] = len(entry.get("candidate_composition_modes", []))
        results["rc031_delta_multi_branch_composition_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-031 multi-branch delta composition registry.")
    parser.add_argument("--composition", default="registry/math/rc031_delta_multi_branch_composition_registry.json")
    
    args = parser.parse_args()
    res = validate_rc031_multi_branch_composition(args.composition)
    print(json.dumps(res, indent=2))
