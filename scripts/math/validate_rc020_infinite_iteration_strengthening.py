import json
import os
import argparse

def validate_rc020_infinite_iteration_strengthening(strengthen_reg, failure_reg, base_reg):
    results = {
        "rc020_infinite_iteration_strengthening_validation": {
            "status": "pass",
            "entry_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(strengthen_reg, 'r') as f: s_data = json.load(f).get("rc020_infinite_iteration_strengthening", {})
        with open(failure_reg, 'r') as f: f_data = json.load(f).get("rc020_asymptotic_failure_modes", {})
        with open(base_reg, 'r') as f: b_data = json.load(f)
    except Exception as e:
        results["rc020_infinite_iteration_strengthening_validation"]["status"] = "fail"
        results["rc020_infinite_iteration_strengthening_validation"]["warnings"].append(f"Load error: {e}")
        return results

    fm_ids = [fm["id"] for fm in f_data.get("failure_modes", [])]
    
    # Get condition IDs from base registry
    base_entry = next((e for e in b_data.get("asymptotic_stability_entries", []) if e["id"] == "RC-020"), None)
    if not base_entry:
        results["rc020_infinite_iteration_strengthening_validation"]["status"] = "fail"
        results["rc020_infinite_iteration_strengthening_validation"]["warnings"].append("Base RC-020 entry not found.")
        return results
        
    cond_ids = [c["id"] for c in base_entry.get("infinite_iteration_conditions", [])]
    classes = [c["class"] for c in s_data.get("asymptotic_classes", [])]

    # Validate Entries
    for entry in s_data.get("strengthening_entries", []):
        results["rc020_infinite_iteration_strengthening_validation"]["entry_count"] += 1
        
        # Check conditions
        for cond in entry.get("conditions", []):
            if cond not in cond_ids:
                 results["rc020_infinite_iteration_strengthening_validation"]["status"] = "warning"
                 results["rc020_infinite_iteration_strengthening_validation"]["warnings"].append(f"Entry {entry['entry_id']} references unknown condition: {cond}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["rc020_infinite_iteration_strengthening_validation"]["status"] = "warning"
                results["rc020_infinite_iteration_strengthening_validation"]["warnings"].append(f"Entry {entry['entry_id']} references unknown failure mode: {fm}")

    # Humility Check: Global convergence claimed?
    if s_data.get("strengthening_status") == "globally_convergent":
         results["rc020_infinite_iteration_strengthening_validation"]["status"] = "fail"
         results["rc020_infinite_iteration_strengthening_validation"]["warnings"].append("OVERREACH: globally_convergent status claimed for RC-020.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-020 infinite iteration strengthening.")
    parser.add_argument("--strengthen", default="registry/math/rc020_infinite_iteration_strengthening_registry.json")
    parser.add_argument("--failures", default="registry/math/rc020_asymptotic_failure_modes.json")
    parser.add_argument("--base", default="registry/math/rc020_infinite_iteration_stability_registry.json")
    
    args = parser.parse_args()
    res = validate_rc020_infinite_iteration_strengthening(args.strengthen, args.failures, args.base)
    print(json.dumps(res, indent=2))
