import json
import os
import argparse

def validate_rc019_retention_interaction(interaction_reg):
    results = {
        "rc019_selection_retention_interaction_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "retention_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(interaction_reg, 'r') as f: interaction_data = json.load(f)
    except Exception as e:
        results["rc019_selection_retention_interaction_validation"]["status"] = "fail"
        results["rc019_selection_retention_interaction_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in interaction_data.get("selection_retention_interaction_entries", []):
        results["rc019_selection_retention_interaction_validation"]["entry_count"] += 1
        
        # Governance check: no deterministic pruning, unique survival, or global closure claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("deterministic_branch_pruning_claimed") or 
            gov.get("unique_branch_survival_claimed") or 
            gov.get("global_retention_stability_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc019_selection_retention_interaction_validation"]["status"] = "fail"
             results["rc019_selection_retention_interaction_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming unique branch survival, deterministic pruning, or global closure.")

        # Check dependencies
        if "RC-018" not in entry.get("depends_on", []):
             results["rc019_selection_retention_interaction_validation"]["status"] = "warning"
             results["rc019_selection_retention_interaction_validation"]["warnings"].append(f"Entry {entry['id']} missing recommended dependency on RC-018.")

        results["rc019_selection_retention_interaction_validation"]["condition_count"] = len(entry.get("selection_retention_conditions", []))
        results["rc019_selection_retention_interaction_validation"]["retention_mode_count"] = len(entry.get("candidate_retention_modes", []))
        results["rc019_selection_retention_interaction_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-019 selection-retention interaction registry.")
    parser.add_argument("--interaction", default="registry/math/rc019_selection_retention_interaction_registry.json")
    
    args = parser.parse_args()
    res = validate_rc019_retention_interaction(args.interaction)
    print(json.dumps(res, indent=2))
