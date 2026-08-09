import json
import os
import argparse

def validate_sum_operator_convergence(convergence_reg, failure_reg, bound_reg):
    results = {
        "sum_operator_convergence_validation": {
            "status": "pass",
            "entry_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(convergence_reg, 'r') as f: conv_data = json.load(f).get("sum_operator_convergence_registry", {})
        with open(failure_reg, 'r') as f: failure_data = json.load(f).get("sum_operator_failure_modes", {})
        with open(bound_reg, 'r') as f: bound_data = json.load(f).get("nonlocal_sum_bound_registry", {})
    except Exception as e:
        results["sum_operator_convergence_validation"]["status"] = "fail"
        results["sum_operator_convergence_validation"]["warnings"].append(f"Load error: {e}")
        return results

    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    bound_ids = [b["bound_id"] for b in bound_data.get("bounds", [])]
    conv_classes = conv_data.get("convergence_classes", [])

    # Validate Entries
    for entry in conv_data.get("convergence_entries", []):
        results["sum_operator_convergence_validation"]["entry_count"] += 1
        
        # Check convergence class
        if entry.get("convergence_class") not in conv_classes:
             results["sum_operator_convergence_validation"]["status"] = "warning"
             results["sum_operator_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown class: {entry['convergence_class']}")

        # Check bound/condition dependencies
        for cond in entry.get("conditions", []):
            if cond not in bound_ids:
                results["sum_operator_convergence_validation"]["status"] = "warning"
                results["sum_operator_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown condition: {cond}")
        
        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["sum_operator_convergence_validation"]["status"] = "warning"
                results["sum_operator_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown failure mode: {fm}")

        if entry.get("status") == "gap_open":
            results["sum_operator_convergence_validation"]["closure_gaps"].append(f"GAP-001: {entry['target']} ({entry['entry_id']})")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate sum operator convergence registries.")
    parser.add_argument("--convergence", default="registry/math/sum_operator_convergence_registry.json")
    parser.add_argument("--failures", default="registry/math/sum_operator_failure_modes.json")
    parser.add_argument("--bounds", default="registry/math/nonlocal_sum_bound_registry.json")
    
    args = parser.parse_args()
    res = validate_sum_operator_convergence(args.convergence, args.failures, args.bounds)
    print(json.dumps(res, indent=2))
