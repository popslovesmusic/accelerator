import json
import os
import argparse

def validate_rc002_symbolic_support_elevation(elevation_reg, readiness_reg, closure_reg):
    results = {
        "rc002_symbolic_support_elevation_validation": {
            "status": "pass",
            "entry_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(elevation_reg, 'r') as f: e_data = json.load(f).get("rc002_symbolic_support_elevation", {})
        with open(readiness_reg, 'r') as f: r_data = json.load(f).get("rc002_derivation_readiness", {})
        with open(closure_reg, 'r') as f: c_data = json.load(f)
    except Exception as e:
        results["rc002_symbolic_support_elevation_validation"]["status"] = "fail"
        results["rc002_symbolic_support_elevation_validation"]["errors"].append(f"Load error: {e}")
        return results

    # Check target
    if e_data.get("target") != "RC-002":
        results["rc002_symbolic_support_elevation_validation"]["status"] = "fail"
        results["rc002_symbolic_support_elevation_validation"]["errors"].append("Target mismatch: expected RC-002.")

    # Check status promotion
    if e_data.get("elevation_status") == "derivation_supported":
         # Per core_rule, the patch reviews for elevation, but should not finalize global closure.
         # The elevation_status in the registry should reflect the current state (symbolic_supported) 
         # until the patch is verified and status is updated.
         pass

    # Check entries against readiness
    readiness_reqs = [r["requirement"] for r in r_data.get("readiness_criteria", [])]
    for entry in e_data.get("elevation_entries", []):
        results["rc002_symbolic_support_elevation_validation"]["entry_count"] += 1
        for req in entry.get("requirements_satisfied", []):
            if req not in readiness_reqs:
                 results["rc002_symbolic_support_elevation_validation"]["status"] = "warning"
                 results["rc002_symbolic_support_elevation_validation"]["warnings"].append(f"Entry {entry['step_id']} references unknown requirement: {req}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-002 symbolic support elevation.")
    parser.add_argument("--elevation", default="registry/math/rc002_symbolic_support_elevation_registry.json")
    parser.add_argument("--readiness", default="registry/math/rc002_derivation_readiness_registry.json")
    parser.add_argument("--closure", default="registry/math/rc002_derivation_closure_registry.json")
    
    args = parser.parse_args()
    res = validate_rc002_symbolic_support_elevation(args.elevation, args.readiness, args.closure)
    print(json.dumps(res, indent=2))
