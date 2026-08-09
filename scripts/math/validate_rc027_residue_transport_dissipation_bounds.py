import json
import os
import argparse

def validate_rc027_residue_dissipation(dissipation_reg):
    results = {
        "rc027_residue_transport_dissipation_bounds_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "dissipation_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(dissipation_reg, 'r') as f: diss_data = json.load(f)
    except Exception as e:
        results["rc027_residue_transport_dissipation_bounds_validation"]["status"] = "fail"
        results["rc027_residue_transport_dissipation_bounds_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in diss_data.get("residue_dissipation_entries", []):
        results["rc027_residue_transport_dissipation_bounds_validation"]["entry_count"] += 1
        
        # Governance check: no exact global conservation or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("exact_global_residue_conservation_claimed") or 
            gov.get("deterministic_residue_persistence_claimed") or 
            gov.get("complete_nonlocal_transport_closure_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc027_residue_transport_dissipation_bounds_validation"]["status"] = "fail"
             results["rc027_residue_transport_dissipation_bounds_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming exact conservation, complete closure, or global closure.")

        # Check dependencies
        if "RC-026" not in entry.get("depends_on", []):
             results["rc027_residue_transport_dissipation_bounds_validation"]["status"] = "warning"
             results["rc027_residue_transport_dissipation_bounds_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-026.")

        results["rc027_residue_transport_dissipation_bounds_validation"]["condition_count"] = len(entry.get("residue_dissipation_conditions", []))
        results["rc027_residue_transport_dissipation_bounds_validation"]["dissipation_mode_count"] = len(entry.get("candidate_dissipation_modes", []))
        results["rc027_residue_transport_dissipation_bounds_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-027 residue transport dissipation bounds registry.")
    parser.add_argument("--dissipation", default="registry/math/rc027_residue_transport_dissipation_bounds_registry.json")
    
    args = parser.parse_args()
    res = validate_rc027_residue_dissipation(args.dissipation)
    print(json.dumps(res, indent=2))
