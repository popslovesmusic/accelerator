import json
import os
import argparse

def validate_selection_uniqueness(uniqueness_reg, tie_reg, failure_reg, op_reg, law_regs):
    results = {
        "selection_uniqueness_validation": {
            "status": "pass",
            "uniqueness_count": 0,
            "tie_resolution_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(uniqueness_reg, 'r') as f: uniqueness_data = json.load(f)
        with open(tie_reg, 'r') as f: tie_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["selection_uniqueness_validation"]["status"] = "fail"
        results["selection_uniqueness_validation"]["errors"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection", "reconstruction_uniqueness"])
    
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    uniqueness_classes = [c["class"] for c in uniqueness_data.get("selection_uniqueness_classes", [])]
    tie_classes = [c["class"] for c in tie_data.get("tie_resolution_classes", [])]

    # Validate Uniqueness Entries
    for entry in uniqueness_data.get("uniqueness_entries", []):
        results["selection_uniqueness_validation"]["uniqueness_count"] += 1
        
        # Check target
        target = entry.get("target")
        if target not in op_symbols and target not in law_ids:
             results["selection_uniqueness_validation"]["status"] = "warning"
             results["selection_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown target: {target}")
        
        # Check uniqueness class
        if entry.get("uniqueness_class") not in uniqueness_classes:
             results["selection_uniqueness_validation"]["status"] = "warning"
             results["selection_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown class: {entry['uniqueness_class']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["selection_uniqueness_validation"]["status"] = "warning"
                results["selection_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown failure mode: {fm}")

    # Validate Tie Resolution Entries
    for entry in tie_data.get("tie_resolution_entries", []):
        results["selection_uniqueness_validation"]["tie_resolution_count"] += 1
        
        # Check target
        target = entry.get("target")
        if target not in op_symbols and target not in law_ids:
             results["selection_uniqueness_validation"]["status"] = "warning"
             results["selection_uniqueness_validation"]["warnings"].append(f"Tie resolution entry {entry['entry_id']} references unknown target: {target}")
        
        # Check class
        if entry.get("tie_resolution_class") not in tie_classes:
             results["selection_uniqueness_validation"]["status"] = "warning"
             results["selection_uniqueness_validation"]["warnings"].append(f"Tie resolution entry {entry['entry_id']} references unknown class: {entry['tie_resolution_class']}")

    results["selection_uniqueness_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate selection uniqueness and tie-resolution registries.")
    parser.add_argument("--uniqueness", default="registry/math/selection_uniqueness_registry.json")
    parser.add_argument("--tie", default="registry/math/selection_tie_resolution_registry.json")
    parser.add_argument("--failures", default="registry/math/selection_uniqueness_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    
    args = parser.parse_args()
    res = validate_selection_uniqueness(args.uniqueness, args.tie, args.failures, args.operators, args.laws)
    print(json.dumps(res, indent=2))
