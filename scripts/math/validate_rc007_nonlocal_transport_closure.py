import json
import os
import argparse

def validate_rc007_nonlocal_transport_closure(closure_reg):
    results = {
        "rc007_nonlocal_transport_closure_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "transport_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(closure_reg, 'r') as f: closure_data = json.load(f)
    except Exception as e:
        results["rc007_nonlocal_transport_closure_validation"]["status"] = "fail"
        results["rc007_nonlocal_transport_closure_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in closure_data.get("transport_closure_entries", []):
        results["rc007_nonlocal_transport_closure_validation"]["entry_count"] += 1
        
        # Governance check: no global closure, infinite convergence, or invertibility claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_transport_closure_claimed") or 
            gov.get("infinite_transport_convergence_claimed") or 
            gov.get("transport_invertibility_claimed") or
            gov.get("unique_reconstruction_claimed") or
            gov.get("global_closure_claimed")):
             results["rc007_nonlocal_transport_closure_validation"]["status"] = "fail"
             results["rc007_nonlocal_transport_closure_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global closure, infinite convergence, or invertibility.")

        # Check dependencies
        if "RC-006" not in entry.get("depends_on", []):
             results["rc007_nonlocal_transport_closure_validation"]["status"] = "warning"
             results["rc007_nonlocal_transport_closure_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-006.")

        results["rc007_nonlocal_transport_closure_validation"]["condition_count"] = len(entry.get("transport_closure_conditions", []))
        results["rc007_nonlocal_transport_closure_validation"]["transport_mode_count"] = len(entry.get("candidate_transport_modes", []))
        results["rc007_nonlocal_transport_closure_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-007 nonlocal transport closure registry.")
    parser.add_argument("--closure", default="registry/math/rc007_nonlocal_transport_closure_registry.json")
    
    args = parser.parse_args()
    res = validate_rc007_nonlocal_transport_closure(args.closure)
    print(json.dumps(res, indent=2))
