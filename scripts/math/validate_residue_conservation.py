import json
import os
import argparse

def validate_residue_conservation(rcon_reg, inv_reg, failure_reg, op_reg, law_regs):
    results = {
        "residue_conservation_validation": {
            "status": "pass",
            "balance_entry_count": 0,
            "invariant_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(rcon_reg, 'r') as f: rcon_data = json.load(f)
        with open(inv_reg, 'r') as f: inv_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["residue_conservation_validation"]["status"] = "fail"
        results["residue_conservation_validation"]["errors"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection", "residue_update", "NavT", "Pi_A", "delta", "symbolic_reduction_chains", "recursive_convergence"])
    
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    balance_classes = [bc["class"] for bc in rcon_data.get("residue_balance_classes", [])]

    # Validate Balance Entries
    for entry in rcon_data.get("balance_entries", []):
        results["residue_conservation_validation"]["balance_entry_count"] += 1
        
        # Check target
        target = entry.get("target")
        if target not in op_symbols and target not in law_ids:
             results["residue_conservation_validation"]["status"] = "warning"
             results["residue_conservation_validation"]["warnings"].append(f"Balance entry {entry['entry_id']} references unknown target: {target}")
        
        # Check balance class
        if entry.get("balance_class") not in balance_classes:
             results["residue_conservation_validation"]["status"] = "warning"
             results["residue_conservation_validation"]["warnings"].append(f"Balance entry {entry['entry_id']} references unknown class: {entry['balance_class']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["residue_conservation_validation"]["status"] = "warning"
                results["residue_conservation_validation"]["warnings"].append(f"Balance entry {entry['entry_id']} references unknown failure mode: {fm}")

    results["residue_conservation_validation"]["invariant_count"] = len(inv_data.get("candidate_invariants", []))
    results["residue_conservation_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate residue conservation registries.")
    parser.add_argument("--rcon", default="registry/math/residue_conservation_registry.json")
    parser.add_argument("--inv", default="registry/math/residue_transport_invariant_registry.json")
    parser.add_argument("--failures", default="registry/math/residue_balance_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    
    args = parser.parse_args()
    res = validate_residue_conservation(args.rcon, args.inv, args.failures, args.operators, args.laws)
    print(json.dumps(res, indent=2))
