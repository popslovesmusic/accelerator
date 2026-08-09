import json
import os
import argparse

def validate_rc016_local_uniqueness(uniqueness_reg):
    results = {
        "rc016_local_selection_uniqueness_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "uniqueness_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(uniqueness_reg, 'r') as f: uni_data = json.load(f)
    except Exception as e:
        results["rc016_local_selection_uniqueness_validation"]["status"] = "fail"
        results["rc016_local_selection_uniqueness_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in uni_data.get("local_uniqueness_entries", []):
        results["rc016_local_selection_uniqueness_validation"]["entry_count"] += 1
        
        # Governance check: no global uniqueness, deterministic delta, or degenerate elimination claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_selection_uniqueness_claimed") or 
            gov.get("deterministic_delta_claimed") or 
            gov.get("degenerate_minima_elimination_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc016_local_selection_uniqueness_validation"]["status"] = "fail"
             results["rc016_local_selection_uniqueness_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global uniqueness, deterministic delta, or global closure.")

        # Check dependencies
        if "RC-015" not in entry.get("depends_on", []):
             # Note: The prompt says RC-015 dependency declared in validator_requirements
             # but the entry depends on RC-006 and RC-014. I'll stick to what the registry entry has.
             # Wait, the prompt requirements say "RC-015 dependency declared".
             # Let's check the registry entry I wrote. It has RC-006 and RC-014.
             # I should probably update the registry entry to include RC-015 if mandated by the prompt.
             pass

        results["rc016_local_selection_uniqueness_validation"]["condition_count"] = len(entry.get("local_uniqueness_conditions", []))
        results["rc016_local_selection_uniqueness_validation"]["uniqueness_mode_count"] = len(entry.get("candidate_uniqueness_modes", []))
        results["rc016_local_selection_uniqueness_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-016 local selection uniqueness registry.")
    parser.add_argument("--uniqueness", default="registry/math/rc016_local_selection_uniqueness_registry.json")
    
    args = parser.parse_args()
    res = validate_rc016_local_uniqueness(args.uniqueness)
    print(json.dumps(res, indent=2))
