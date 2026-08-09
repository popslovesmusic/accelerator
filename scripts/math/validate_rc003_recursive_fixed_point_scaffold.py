import json
import os
import argparse

def validate_rc003_fixed_point_scaffold(scaffold_reg):
    results = {
        "rc003_recursive_fixed_point_scaffold_validation": {
            "status": "pass",
            "scaffold_count": 0,
            "condition_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(scaffold_reg, 'r') as f: scaffold_data = json.load(f)
    except Exception as e:
        results["rc003_recursive_fixed_point_scaffold_validation"]["status"] = "fail"
        results["rc003_recursive_fixed_point_scaffold_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in scaffold_data.get("scaffold_entries", []):
        results["rc003_recursive_fixed_point_scaffold_validation"]["scaffold_count"] += 1
        
        # Check explicit bounded recursion scope
        if "bounded_iteration_domain" not in entry.get("candidate_conditions", []):
             results["rc003_recursive_fixed_point_scaffold_validation"]["status"] = "warning"
             results["rc003_recursive_fixed_point_scaffold_validation"]["warnings"].append(f"Entry {entry['id']} missing explicit bounded_iteration_domain condition.")

        # Governance check: no infinite convergence or global fixed point
        if entry["governance_constraints"].get("infinite_convergence_claimed") or entry["governance_constraints"].get("global_fixed_point_claimed"):
             results["rc003_recursive_fixed_point_scaffold_validation"]["status"] = "fail"
             results["rc003_recursive_fixed_point_scaffold_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming infinite convergence or global fixed points.")

        # Check dependencies
        if "RC-002" not in entry.get("depends_on", []):
             results["rc003_recursive_fixed_point_scaffold_validation"]["status"] = "warning"
             results["rc003_recursive_fixed_point_scaffold_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-002.")

        results["rc003_recursive_fixed_point_scaffold_validation"]["condition_count"] = len(entry.get("candidate_conditions", []))
        results["rc003_recursive_fixed_point_scaffold_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-003 recursive fixed-point scaffolding.")
    parser.add_argument("--scaffold", default="registry/math/rc003_recursive_fixed_point_scaffold_registry.json")
    
    args = parser.parse_args()
    res = validate_rc003_fixed_point_scaffold(args.scaffold)
    print(json.dumps(res, indent=2))
