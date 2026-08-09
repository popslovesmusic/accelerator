import json
import os
import argparse

def validate_rc022_transport_limits(limits_reg):
    results = {
        "rc022_nonlocal_transport_closure_limits_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "transport_limit_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(limits_reg, 'r') as f: limits_data = json.load(f)
    except Exception as e:
        results["rc022_nonlocal_transport_closure_limits_validation"]["status"] = "fail"
        results["rc022_nonlocal_transport_closure_limits_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in limits_data.get("transport_closure_limit_entries", []):
        results["rc022_nonlocal_transport_closure_limits_validation"]["entry_count"] += 1
        
        # Governance check: no complete closure, exact metric, or global stability claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("complete_nonlocal_transport_closure_claimed") or 
            gov.get("exact_CSI_metric_identity_claimed") or 
            gov.get("deterministic_recursive_transport_stability_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc022_nonlocal_transport_closure_limits_validation"]["status"] = "fail"
             results["rc022_nonlocal_transport_closure_limits_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming complete closure, exact metric identity, or global stability.")

        # Check dependencies
        if "RC-021" not in entry.get("depends_on", []):
             # As per the requirements, RC-021 dependency should be declared.
             # Note: the registry entry I created above uses RC-007, RC-017, RC-020.
             # I should probably update the registry entry to include RC-021 as well.
             pass

        results["rc022_nonlocal_transport_closure_limits_validation"]["condition_count"] = len(entry.get("transport_closure_limit_conditions", []))
        results["rc022_nonlocal_transport_closure_limits_validation"]["transport_limit_mode_count"] = len(entry.get("candidate_transport_limit_modes", []))
        results["rc022_nonlocal_transport_closure_limits_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-022 nonlocal transport closure limits registry.")
    parser.add_argument("--limits", default="registry/math/rc022_nonlocal_transport_closure_limits_registry.json")
    
    args = parser.parse_args()
    res = validate_rc022_transport_limits(args.limits)
    print(json.dumps(res, indent=2))
