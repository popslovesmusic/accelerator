import json
import os
import argparse

def validate_residue_behavior(behavior_reg, balance_reg, failure_reg, op_reg, law_regs):
    results = {
        "residue_behavior_validation": {
            "status": "pass",
            "behavior_count": 0,
            "balance_condition_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(behavior_reg, 'r') as f: behavior_data = json.load(f)
        with open(balance_reg, 'r') as f: balance_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["residue_behavior_validation"]["status"] = "fail"
        results["residue_behavior_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    behavior_classes = [bc["class"] for bc in behavior_data.get("behavior_classes", [])]
    stability_implications = balance_data.get("stability_implications", [])
    convergence_implications = balance_data.get("convergence_implications", [])

    # Validate Behavior Entries
    for entry in behavior_data.get("behavior_entries", []):
        results["residue_behavior_validation"]["behavior_count"] += 1
        
        # Check target operator
        if entry.get("target_operator") not in op_symbols:
             results["residue_behavior_validation"]["status"] = "warning"
             results["residue_behavior_validation"]["warnings"].append(f"Residue behavior {entry['entry_id']} references unknown operator: {entry['target_operator']}")
        
        # Check target law
        if entry.get("target_law") != "none" and entry.get("target_law") not in law_ids:
             results["residue_behavior_validation"]["status"] = "warning"
             results["residue_behavior_validation"]["warnings"].append(f"Residue behavior {entry['entry_id']} references unknown law: {entry['target_law']}")

        # Check behavior class
        if entry.get("behavior_class") not in behavior_classes:
             results["residue_behavior_validation"]["status"] = "warning"
             results["residue_behavior_validation"]["warnings"].append(f"Residue behavior {entry['entry_id']} references unknown class: {entry['behavior_class']}")

        # Check stability implication
        if entry.get("stability_implication") not in stability_implications:
             results["residue_behavior_validation"]["status"] = "warning"
             results["residue_behavior_validation"]["warnings"].append(f"Residue behavior {entry['entry_id']} references unknown stability implication: {entry['stability_implication']}")

        # Check convergence implication
        if entry.get("convergence_implication") not in convergence_implications:
             results["residue_behavior_validation"]["status"] = "warning"
             results["residue_behavior_validation"]["warnings"].append(f"Residue behavior {entry['entry_id']} references unknown convergence implication: {entry['convergence_implication']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["residue_behavior_validation"]["status"] = "warning"
                results["residue_behavior_validation"]["warnings"].append(f"Residue behavior {entry['entry_id']} references unknown failure mode: {fm}")

        results["residue_behavior_validation"]["open_questions"].extend(entry.get("open_questions", []))

    results["residue_behavior_validation"]["balance_condition_count"] = len(balance_data.get("balance_conditions", []))
    results["residue_behavior_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate residue behavior registries.")
    parser.add_argument("--behavior", default="registry/math/residue_transport_behavior_registry.json")
    parser.add_argument("--balance", default="registry/math/residue_balance_condition_registry.json")
    parser.add_argument("--failures", default="registry/math/residue_behavior_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    
    args = parser.parse_args()
    res = validate_residue_behavior(args.behavior, args.balance, args.failures, args.operators, args.laws)
    print(json.dumps(res, indent=2))
