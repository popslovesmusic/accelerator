import json
import os
import argparse

def validate_operational_stability_baseline(baseline_reg, metric_reg, failure_reg, op_reg, theorem_reg):
    results = {
        "operational_stability_baseline_validation": {
            "status": "pass",
            "entry_count": 0,
            "metric_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(baseline_reg, 'r') as f: baseline_data = json.load(f)
        with open(metric_reg, 'r') as f: metric_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
    except Exception as e:
        results["operational_stability_baseline_validation"]["status"] = "fail"
        results["operational_stability_baseline_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    # Add non-primitive targets
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection"])
    
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    metric_ids = [m["metric_id"] for m in metric_data.get("stability_metrics", [])]
    stability_classes = [sc["class"] for sc in baseline_data.get("stability_classes", [])]

    # Validate Baseline Entries
    for entry in baseline_data.get("baseline_entries", []):
        results["operational_stability_baseline_validation"]["entry_count"] += 1
        
        # Check target (operator or theorem)
        target = entry.get("target")
        if target not in op_symbols and target not in theorem_ids:
             results["operational_stability_baseline_validation"]["status"] = "warning"
             results["operational_stability_baseline_validation"]["warnings"].append(f"Baseline entry {entry['entry_id']} references unknown target: {target}")
        
        # Check expected class
        if entry.get("expected_class") not in stability_classes:
             results["operational_stability_baseline_validation"]["status"] = "warning"
             results["operational_stability_baseline_validation"]["warnings"].append(f"Baseline entry {entry['entry_id']} references unknown class: {entry['expected_class']}")

        # Check associated metrics
        for mid in entry.get("associated_metrics", []):
            if mid not in metric_ids:
                results["operational_stability_baseline_validation"]["status"] = "warning"
                results["operational_stability_baseline_validation"]["warnings"].append(f"Baseline entry {entry['entry_id']} references unknown metric: {mid}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["operational_stability_baseline_validation"]["status"] = "warning"
                results["operational_stability_baseline_validation"]["warnings"].append(f"Baseline entry {entry['entry_id']} references unknown failure mode: {fm}")

    results["operational_stability_baseline_validation"]["metric_count"] = len(metric_ids)
    results["operational_stability_baseline_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate operational stability baseline registries.")
    parser.add_argument("--baseline", default="registry/math/operational_stability_baseline_registry.json")
    parser.add_argument("--metrics", default="registry/math/stability_metric_registry.json")
    parser.add_argument("--failures", default="registry/math/stability_failure_mode_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    
    args = parser.parse_args()
    res = validate_operational_stability_baseline(args.baseline, args.metrics, args.failures, args.operators, args.theorems)
    print(json.dumps(res, indent=2))
