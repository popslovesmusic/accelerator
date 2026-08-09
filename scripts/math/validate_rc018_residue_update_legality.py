import json
import os
import argparse

def validate_rc018_residue_legality(legality_reg):
    results = {
        "rc018_residue_update_legality_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "legality_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(legality_reg, 'r') as f: leg_data = json.load(f)
    except Exception as e:
        results["rc018_residue_update_legality_validation"]["status"] = "fail"
        results["rc018_residue_update_legality_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in leg_data.get("residue_update_legality_entries", []):
        results["rc018_residue_update_legality_validation"]["entry_count"] += 1
        
        # Governance check: no global legality closure, exact residue conservation, or deterministic stabilization
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_legality_closure_claimed") or 
            gov.get("exact_residue_conservation_claimed") or 
            gov.get("deterministic_stabilization_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc018_residue_update_legality_validation"]["status"] = "fail"
             results["rc018_residue_update_legality_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global closure, exact conservation, or deterministic stabilization.")

        # Check dependencies
        if "RC-017" not in entry.get("depends_on", []):
             results["rc018_residue_update_legality_validation"]["status"] = "warning"
             results["rc018_residue_update_legality_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-017.")

        results["rc018_residue_update_legality_validation"]["condition_count"] = len(entry.get("residue_update_conditions", []))
        results["rc018_residue_update_legality_validation"]["legality_mode_count"] = len(entry.get("candidate_legality_modes", []))
        results["rc018_residue_update_legality_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-018 residue update legality registry.")
    parser.add_argument("--legality", default="registry/math/rc018_residue_update_legality_registry.json")
    
    args = parser.parse_args()
    res = validate_rc018_residue_legality(args.legality)
    print(json.dumps(res, indent=2))
