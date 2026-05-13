import json
import os
import argparse

def validate_rc026_tiebreak_dynamics(tiebreak_reg):
    results = {
        "rc026_degenerate_minima_tiebreak_dynamics_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "tiebreak_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(tiebreak_reg, 'r') as f: tb_data = json.load(f)
    except Exception as e:
        results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["status"] = "fail"
        results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in tb_data.get("degenerate_tiebreak_entries", []):
        results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["entry_count"] += 1
        
        # Governance check: no global uniqueness, deterministic resolution, or unique identity claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_minima_uniqueness_claimed") or 
            gov.get("deterministic_tiebreak_resolution_claimed") or 
            gov.get("exact_selection_identity_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["status"] = "fail"
             results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global uniqueness, deterministic resolution, or global closure.")

        # Check dependencies
        if "RC-025" not in entry.get("depends_on", []):
             results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["status"] = "warning"
             results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-025.")

        results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["condition_count"] = len(entry.get("degenerate_tiebreak_conditions", []))
        results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["tiebreak_mode_count"] = len(entry.get("candidate_tiebreak_modes", []))
        results["rc026_degenerate_minima_tiebreak_dynamics_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-026 degenerate minima tiebreak dynamics registry.")
    parser.add_argument("--tiebreak", default="registry/math/rc026_degenerate_minima_tiebreak_dynamics_registry.json")
    
    args = parser.parse_args()
    res = validate_rc026_tiebreak_dynamics(args.tiebreak)
    print(json.dumps(res, indent=2))
