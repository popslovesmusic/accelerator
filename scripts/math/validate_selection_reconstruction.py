import json
import os
import argparse

def validate_selection_reconstruction(reconstruction_reg, inverse_reg, failure_reg, op_reg):
    results = {
        "selection_reconstruction_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(reconstruction_reg, 'r') as f: rec_data = json.load(f)
        with open(inverse_reg, 'r') as f: inv_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
    except Exception as e:
        results["selection_reconstruction_validation"]["status"] = "fail"
        results["selection_reconstruction_validation"]["errors"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    op_symbols.extend(["observable_projection", "selection_trace"])
    
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    rec_classes = [rc["class"] for rc in rec_data.get("reconstruction_classes", [])]

    # Validate Entries
    for entry in rec_data.get("reconstruction_entries", []):
        results["selection_reconstruction_validation"]["entry_count"] += 1
        
        # Check target
        if entry.get("target") not in op_symbols:
             results["selection_reconstruction_validation"]["status"] = "warning"
             results["selection_reconstruction_validation"]["warnings"].append(f"Reconstruction entry references unknown target: {entry['target']}")
        
        # Check class
        if entry.get("reconstruction_class") not in rec_classes:
             results["selection_reconstruction_validation"]["status"] = "warning"
             results["selection_reconstruction_validation"]["warnings"].append(f"Entry {entry['target']} has unknown reconstruction class: {entry['reconstruction_class']}")

    results["selection_reconstruction_validation"]["condition_count"] = len(inv_data.get("inverse_conditions", []))
    results["selection_reconstruction_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate selection reconstruction registries.")
    parser.add_argument("--reconstruction", default="registry/math/selection_reconstruction_registry.json")
    parser.add_argument("--inverse", default="registry/math/inverse_selection_condition_registry.json")
    parser.add_argument("--failures", default="registry/math/selection_reconstruction_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    
    args = parser.parse_args()
    res = validate_selection_reconstruction(args.reconstruction, args.inverse, args.failures, args.operators)
    print(json.dumps(res, indent=2))
