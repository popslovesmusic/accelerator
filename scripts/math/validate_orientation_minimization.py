import json
import os
import argparse

def validate_orientation_minimization(minimization_reg, metric_reg, failure_reg, op_reg, law_regs):
    results = {
        "orientation_minimization_validation": {
            "status": "pass",
            "minimization_count": 0,
            "metric_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(minimization_reg, 'r') as f: min_data = json.load(f)
        with open(metric_reg, 'r') as f: metric_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["orientation_minimization_validation"]["status"] = "fail"
        results["orientation_minimization_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    metric_names = [m["name"] for m in metric_data.get("metrics", [])]
    rule_classes = [rc["class"] for rc in min_data.get("rule_classes", [])]
    tie_behaviors = ["unique", "multi_minimum", "weighted", "undefined"]
    stability_implications = ["stabilizing", "destabilizing", "neutral", "conditional", "undefined"]

    # Validate Minimization Entries
    for entry in min_data.get("minimization_entries", []):
        results["orientation_minimization_validation"]["minimization_count"] += 1
        
        # Check target operator
        if entry.get("target_operator") not in op_symbols:
             results["orientation_minimization_validation"]["status"] = "warning"
             results["orientation_minimization_validation"]["warnings"].append(f"Orientation minimization {entry['entry_id']} references unknown operator: {entry['target_operator']}")
        
        # Check target law
        if entry.get("target_law") != "none" and entry.get("target_law") not in law_ids:
             results["orientation_minimization_validation"]["status"] = "warning"
             results["orientation_minimization_validation"]["warnings"].append(f"Orientation minimization {entry['entry_id']} references unknown law: {entry['target_law']}")

        # Check rule class
        if entry.get("rule_class") not in rule_classes:
             results["orientation_minimization_validation"]["status"] = "warning"
             results["orientation_minimization_validation"]["warnings"].append(f"Orientation minimization {entry['entry_id']} references unknown class: {entry['rule_class']}")

        # Check orientation metric
        if entry.get("orientation_metric") not in metric_names:
             results["orientation_minimization_validation"]["status"] = "warning"
             results["orientation_minimization_validation"]["warnings"].append(f"Orientation minimization {entry['entry_id']} references unknown metric: {entry['orientation_metric']}")

        # Check tie behavior
        if entry.get("tie_behavior") not in tie_behaviors:
             results["orientation_minimization_validation"]["status"] = "warning"
             results["orientation_minimization_validation"]["warnings"].append(f"Orientation minimization {entry['entry_id']} references unknown tie behavior: {entry['tie_behavior']}")

        # Check stability implication
        if entry.get("stability_implication") not in stability_implications:
             results["orientation_minimization_validation"]["status"] = "warning"
             results["orientation_minimization_validation"]["warnings"].append(f"Orientation minimization {entry['entry_id']} references unknown stability implication: {entry['stability_implication']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["orientation_minimization_validation"]["status"] = "warning"
                results["orientation_minimization_validation"]["warnings"].append(f"Orientation minimization {entry['entry_id']} references unknown failure mode: {fm}")

        results["orientation_minimization_validation"]["open_questions"].extend(entry.get("open_questions", []))

    results["orientation_minimization_validation"]["metric_count"] = len(metric_data.get("metrics", []))
    results["orientation_minimization_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate orientation minimization registries.")
    parser.add_argument("--minimization", default="registry/math/orientation_minimization_registry.json")
    parser.add_argument("--metrics", default="registry/math/orientation_metric_registry.json")
    parser.add_argument("--failures", default="registry/math/orientation_failure_mode_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    
    args = parser.parse_args()
    res = validate_orientation_minimization(args.minimization, args.metrics, args.failures, args.operators, args.laws)
    print(json.dumps(res, indent=2))
