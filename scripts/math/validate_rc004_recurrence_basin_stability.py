import json
import os
import argparse

def validate_rc004_basin_stability(stability_reg):
    results = {
        "rc004_recurrence_basin_stability_validation": {
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
        results["rc004_recurrence_basin_stability_validation"]["status"] = "fail"
        results["rc004_recurrence_basin_stability_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in stability_data.get("stability_entries", []):
        results["rc004_recurrence_basin_stability_validation"]["entry_count"] += 1
        
        # Check explicit local scope
        if not entry["governance_constraints"].get("basin_stability_is_local_only"):
             results["rc004_recurrence_basin_stability_validation"]["status"] = "fail"
             results["rc004_recurrence_basin_stability_validation"]["errors"].append(f"Entry {entry['id']} fails to specify local_only constraint.")

        # Governance check: no infinite convergence or global fixed point
        if entry["governance_constraints"].get("infinite_convergence_claimed") or entry["governance_constraints"].get("global_fixed_point_claimed"):
             results["rc004_recurrence_basin_stability_validation"]["status"] = "fail"
             results["rc004_recurrence_basin_stability_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming infinite convergence or global fixed points.")

        # Check dependencies
        if "RC-003" not in entry.get("depends_on", []):
             results["rc004_recurrence_basin_stability_validation"]["status"] = "warning"
             results["rc004_recurrence_basin_stability_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-003.")

        results["rc004_recurrence_basin_stability_validation"]["condition_count"] = len(entry.get("stability_conditions", []))
        results["rc004_recurrence_basin_stability_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-004 recurrence-basin stability registry.")
    parser.add_argument("--stability", default="registry/math/rc004_recurrence_basin_stability_registry.json")
    
    args = parser.parse_args()
    res = validate_rc004_basin_stability(args.stability)
    print(json.dumps(res, indent=2))
