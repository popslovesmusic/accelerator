import json
import os
import argparse

def validate_rc009_residue_transport_conservation(residue_reg):
    results = {
        "rc009_residue_transport_conservation_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "conservation_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(residue_reg, 'r') as f: res_data = json.load(f)
    except Exception as e:
        results["rc009_residue_transport_conservation_validation"]["status"] = "fail"
        results["rc009_residue_transport_conservation_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in res_data.get("residue_transport_conservation_entries", []):
        results["rc009_residue_transport_conservation_validation"]["entry_count"] += 1
        
        # Governance check: no exact global conservation or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("exact_global_conservation_claimed") or 
            gov.get("lossless_transport_identity_claimed") or 
            gov.get("infinite_recursive_stability_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc009_residue_transport_conservation_validation"]["status"] = "fail"
             results["rc009_residue_transport_conservation_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming exact conservation, lossless transport, or global closure.")

        # Check dependencies
        if "RC-008" not in entry.get("depends_on", []):
             results["rc009_residue_transport_conservation_validation"]["status"] = "warning"
             results["rc009_residue_transport_conservation_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-008.")

        results["rc009_residue_transport_conservation_validation"]["condition_count"] = len(entry.get("residue_transport_conditions", []))
        results["rc009_residue_transport_conservation_validation"]["conservation_mode_count"] = len(entry.get("candidate_conservation_modes", []))
        results["rc009_residue_transport_conservation_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-009 residue transport conservation registry.")
    parser.add_argument("--residue", default="registry/math/rc009_residue_transport_conservation_registry.json")
    
    args = parser.parse_args()
    res = validate_rc009_residue_transport_conservation(args.residue)
    print(json.dumps(res, indent=2))
