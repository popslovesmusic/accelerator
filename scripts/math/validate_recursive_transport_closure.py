import json
import os
import argparse

def validate_recursive_transport_closure(closure_reg, metric_reg, failure_reg, op_reg, law_regs):
    results = {
        "recursive_transport_closure_validation": {
            "status": "pass",
            "closure_entry_count": 0,
            "metric_class_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(closure_reg, 'r') as f: closure_data = json.load(f)
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
        results["recursive_transport_closure_validation"]["status"] = "fail"
        results["recursive_transport_closure_validation"]["errors"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    # Add abstract targets used in initial entries
    op_symbols.extend(["infinite_recursive_transport"])
    
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    closure_classes = [c["class"] for c in closure_data.get("transport_closure_classes", [])]
    metric_classes = [m["class"] for m in metric_data.get("transport_metric_classes", [])]

    # Validate Closure Entries
    for entry in closure_data.get("closure_entries", []):
        results["recursive_transport_closure_validation"]["closure_entry_count"] += 1
        
        # Check target
        target = entry.get("target")
        if target not in op_symbols and target not in law_ids:
             results["recursive_transport_closure_validation"]["status"] = "warning"
             results["recursive_transport_closure_validation"]["warnings"].append(f"Closure entry {entry['entry_id']} references unknown target: {target}")
        
        # Check closure class
        if entry.get("closure_class") not in closure_classes:
             results["recursive_transport_closure_validation"]["status"] = "warning"
             results["recursive_transport_closure_validation"]["warnings"].append(f"Closure entry {entry['entry_id']} references unknown class: {entry['closure_class']}")

        # Check metric class
        if entry.get("metric_class") not in metric_classes:
             results["recursive_transport_closure_validation"]["status"] = "warning"
             results["recursive_transport_closure_validation"]["warnings"].append(f"Closure entry {entry['entry_id']} references unknown metric class: {entry['metric_class']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["recursive_transport_closure_validation"]["status"] = "warning"
                results["recursive_transport_closure_validation"]["warnings"].append(f"Closure entry {entry['entry_id']} references unknown failure mode: {fm}")

    results["recursive_transport_closure_validation"]["metric_class_count"] = len(metric_classes)
    results["recursive_transport_closure_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate recursive transport-closure registries.")
    parser.add_argument("--closure", default="registry/math/recursive_transport_closure_registry.json")
    parser.add_argument("--metrics", default="registry/math/transport_distance_metric_registry.json")
    parser.add_argument("--failures", default="registry/math/transport_iteration_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    
    args = parser.parse_args()
    res = validate_recursive_transport_closure(args.closure, args.metrics, args.failures, args.operators, args.laws)
    print(json.dumps(res, indent=2))
