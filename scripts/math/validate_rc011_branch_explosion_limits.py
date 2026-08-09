import json
import os
import argparse

def validate_rc011_branch_explosion_limits(limits_reg):
    results = {
        "rc011_branch_explosion_limits_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "control_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(limits_reg, 'r') as f: limits_data = json.load(f)
    except Exception as e:
        results["rc011_branch_explosion_limits_validation"]["status"] = "fail"
        results["rc011_branch_explosion_limits_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in limits_data.get("branch_explosion_limit_entries", []):
        results["rc011_branch_explosion_limits_validation"]["entry_count"] += 1
        
        # Governance check: no unique survival, total elimination, or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("unique_branch_survival_claimed") or 
            gov.get("total_branch_elimination_claimed") or 
            gov.get("infinite_recursive_scaling_stability_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc011_branch_explosion_limits_validation"]["status"] = "fail"
             results["rc011_branch_explosion_limits_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming unique survival, total elimination, or global closure.")

        # Check dependencies
        if "RC-010" not in entry.get("depends_on", []):
             results["rc011_branch_explosion_limits_validation"]["status"] = "warning"
             results["rc011_branch_explosion_limits_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-010.")

        results["rc011_branch_explosion_limits_validation"]["condition_count"] = len(entry.get("branch_limit_conditions", []))
        results["rc011_branch_explosion_limits_validation"]["control_mode_count"] = len(entry.get("candidate_branch_control_modes", []))
        results["rc011_branch_explosion_limits_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-011 branch explosion limits registry.")
    parser.add_argument("--limits", default="registry/math/rc011_branch_explosion_limits_registry.json")
    
    args = parser.parse_args()
    res = validate_rc011_branch_explosion_limits(args.limits)
    print(json.dumps(res, indent=2))
