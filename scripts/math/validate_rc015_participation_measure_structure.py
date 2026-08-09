import json
import os
import argparse

def validate_rc015_participation_measure(measure_reg):
    results = {
        "rc015_participation_measure_structure_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "measure_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(measure_reg, 'r') as f: measure_data = json.load(f)
    except Exception as e:
        results["rc015_participation_measure_structure_validation"]["status"] = "fail"
        results["rc015_participation_measure_structure_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in measure_data.get("participation_measure_entries", []):
        results["rc015_participation_measure_structure_validation"]["entry_count"] += 1
        
        # Governance check: no unique structure, completeness, or collapse claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("unique_measure_structure_claimed") or 
            gov.get("measure_completeness_claimed") or 
            gov.get("participation_continuation_equivalence_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc015_participation_measure_structure_validation"]["status"] = "fail"
             results["rc015_participation_measure_structure_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming unique measure, completeness, or participation collapse.")

        results["rc015_participation_measure_structure_validation"]["condition_count"] = len(entry.get("participation_measure_conditions", []))
        results["rc015_participation_measure_structure_validation"]["measure_mode_count"] = len(entry.get("candidate_measure_modes", []))
        results["rc015_participation_measure_structure_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-015 participation measure structure registry.")
    parser.add_argument("--measure", default="registry/math/rc015_participation_measure_structure_registry.json")
    
    args = parser.parse_args()
    res = validate_rc015_participation_measure(args.measure)
    print(json.dumps(res, indent=2))
