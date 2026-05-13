import json
import os
import argparse

def validate_rc030_pruning_scale(scale_reg):
    results = {
        "rc030_branch_pruning_scale_sensitivity_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "pruning_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(scale_reg, 'r') as f: scale_data = json.load(f)
    except Exception as e:
        results["rc030_branch_pruning_scale_sensitivity_validation"]["status"] = "fail"
        results["rc030_branch_pruning_scale_sensitivity_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in scale_data.get("pruning_scale_entries", []):
        results["rc030_branch_pruning_scale_sensitivity_validation"]["entry_count"] += 1
        
        # Governance check: no global stability or deterministic elimination claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_pruning_threshold_stability_claimed") or 
            gov.get("deterministic_branch_elimination_claimed") or 
            gov.get("exact_branch_explosion_prevention_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc030_branch_pruning_scale_sensitivity_validation"]["status"] = "fail"
             results["rc030_branch_pruning_scale_sensitivity_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global stability, deterministic elimination, or global closure.")

        # Check dependencies
        if "RC-029" not in entry.get("depends_on", []):
             results["rc030_branch_pruning_scale_sensitivity_validation"]["status"] = "warning"
             results["rc030_branch_pruning_scale_sensitivity_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-029.")

        results["rc030_branch_pruning_scale_sensitivity_validation"]["condition_count"] = len(entry.get("pruning_scale_conditions", []))
        results["rc030_branch_pruning_scale_sensitivity_validation"]["pruning_mode_count"] = len(entry.get("candidate_pruning_modes", []))
        results["rc030_branch_pruning_scale_sensitivity_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-030 branch pruning scale sensitivity registry.")
    parser.add_argument("--scale", default="registry/math/rc030_branch_pruning_scale_sensitivity_registry.json")
    
    args = parser.parse_args()
    res = validate_rc030_pruning_scale(args.scale)
    print(json.dumps(res, indent=2))
