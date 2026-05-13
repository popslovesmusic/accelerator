import json
import os
import argparse

def validate_rc006_degenerate_minima_resolution(resolution_reg):
    results = {
        "rc006_degenerate_minima_resolution_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "resolution_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(resolution_reg, 'r') as f: res_data = json.load(f)
    except Exception as e:
        results["rc006_degenerate_minima_resolution_validation"]["status"] = "fail"
        results["rc006_degenerate_minima_resolution_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in res_data.get("degenerate_resolution_entries", []):
        results["rc006_degenerate_minima_resolution_validation"]["entry_count"] += 1
        
        # Governance check: no deterministic tie-resolution or global unique resolution
        gov = entry.get("governance_constraints", {})
        if gov.get("deterministic_delta_claimed") or gov.get("unique_resolution_claimed") or gov.get("global_resolution_claimed"):
             results["rc006_degenerate_minima_resolution_validation"]["status"] = "fail"
             results["rc006_degenerate_minima_resolution_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming unique or deterministic resolution.")

        # Check dependencies
        if "RC-005" not in entry.get("depends_on", []):
             results["rc006_degenerate_minima_resolution_validation"]["status"] = "warning"
             results["rc006_degenerate_minima_resolution_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-005.")

        results["rc006_degenerate_minima_resolution_validation"]["condition_count"] = len(entry.get("degenerate_resolution_conditions", []))
        results["rc006_degenerate_minima_resolution_validation"]["resolution_mode_count"] = len(entry.get("candidate_resolution_modes", []))
        results["rc006_degenerate_minima_resolution_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-006 degenerate minima resolution registry.")
    parser.add_argument("--resolution", default="registry/math/rc006_degenerate_minima_resolution_registry.json")
    
    args = parser.parse_args()
    res = validate_rc006_degenerate_minima_resolution(args.resolution)
    print(json.dumps(res, indent=2))
