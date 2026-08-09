import json
import os
import argparse

def validate_rc005_selection_stability(stability_reg):
    results = {
        "rc005_selection_stability_under_recursion_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(stability_reg, 'r') as f: stability_data = json.load(f)
    except Exception as e:
        results["rc005_selection_stability_under_recursion_validation"]["status"] = "fail"
        results["rc005_selection_stability_under_recursion_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in stability_data.get("selection_stability_entries", []):
        results["rc005_selection_stability_under_recursion_validation"]["entry_count"] += 1
        
        # Check explicit delta nondeterminism preservation
        conditions = [c["name"] for c in entry.get("selection_stability_conditions", [])]
        if "delta_nondeterminism_preserved" not in conditions:
             results["rc005_selection_stability_under_recursion_validation"]["status"] = "warning"
             results["rc005_selection_stability_under_recursion_validation"]["warnings"].append(f"Entry {entry['id']} missing explicit delta_nondeterminism_preserved condition.")

        # Governance check: no deterministic selection or global convergence
        gov = entry.get("governance_constraints", {})
        if gov.get("deterministic_selection_claimed") or gov.get("global_convergence_claimed"):
             results["rc005_selection_stability_under_recursion_validation"]["status"] = "fail"
             results["rc005_selection_stability_under_recursion_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming deterministic selection or global convergence.")

        # Check dependencies
        if "RC-004" not in entry.get("depends_on", []):
             results["rc005_selection_stability_under_recursion_validation"]["status"] = "warning"
             results["rc005_selection_stability_under_recursion_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-004.")

        results["rc005_selection_stability_under_recursion_validation"]["condition_count"] = len(entry.get("selection_stability_conditions", []))
        results["rc005_selection_stability_under_recursion_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-005 recursive selection stability registry.")
    parser.add_argument("--stability", default="registry/math/rc005_selection_stability_under_recursion_registry.json")
    
    args = parser.parse_args()
    res = validate_rc005_selection_stability(args.stability)
    print(json.dumps(res, indent=2))
