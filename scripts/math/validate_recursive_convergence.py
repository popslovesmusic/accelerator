import json
import os
import argparse

def validate_recursive_convergence(conv_reg, basin_reg, failure_reg, op_reg, law_regs):
    results = {
        "recursive_convergence_validation": {
            "status": "pass",
            "convergence_count": 0,
            "basin_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(conv_reg, 'r') as f: conv_data = json.load(f)
        with open(basin_reg, 'r') as f: basin_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["recursive_convergence_validation"]["status"] = "fail"
        results["recursive_convergence_validation"]["errors"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection", "residue_update", "NavT", "Pi_A", "delta", "symbolic_reduction_chains"])
    
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    conv_classes = [cc["class"] for cc in conv_data.get("convergence_classes", [])]

    # Validate Convergence Entries
    for entry in conv_data.get("convergence_entries", []):
        results["recursive_convergence_validation"]["convergence_count"] += 1
        
        # Check target
        target = entry.get("target")
        if target not in op_symbols and target not in law_ids:
             results["recursive_convergence_validation"]["status"] = "warning"
             results["recursive_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown target: {target}")
        
        # Check convergence class
        if entry.get("convergence_class") not in conv_classes:
             results["recursive_convergence_validation"]["status"] = "warning"
             results["recursive_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown class: {entry['convergence_class']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["recursive_convergence_validation"]["status"] = "warning"
                results["recursive_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown failure mode: {fm}")

    results["recursive_convergence_validation"]["basin_count"] = len(basin_data.get("basin_classes", []))
    results["recursive_convergence_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate recursive convergence registries.")
    parser.add_argument("--conv", default="registry/math/recursive_convergence_registry.json")
    parser.add_argument("--basin", default="registry/math/recurrence_basin_registry.json")
    parser.add_argument("--failures", default="registry/math/recursive_divergence_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    
    args = parser.parse_args()
    res = validate_recursive_convergence(args.conv, args.basin, args.failures, args.operators, args.laws)
    print(json.dumps(res, indent=2))
