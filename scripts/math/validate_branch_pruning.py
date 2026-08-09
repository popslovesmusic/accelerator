import json
import os
import argparse

def validate_branch_pruning(pruning_reg, stability_reg, failure_reg, op_reg, law_regs, dsr_reg, om_reg, rb_reg):
    results = {
        "branch_pruning_validation": {
            "status": "pass",
            "pruning_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(pruning_reg, 'r') as f: pruning_data = json.load(f)
        with open(stability_reg, 'r') as f: stability_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(dsr_reg, 'r') as f: dsr_data = json.load(f)
        with open(om_reg, 'r') as f: om_data = json.load(f)
        with open(rb_reg, 'r') as f: rb_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["branch_pruning_validation"]["status"] = "fail"
        results["branch_pruning_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    pruning_classes = [pc["class"] for pc in pruning_data.get("pruning_classes", [])]
    branch_bounds = stability_data.get("branch_bounds", [])
    stability_implications = stability_data.get("stability_implications", [])
    convergence_implications = stability_data.get("convergence_implications", [])
    dsr_ids = [r["selection_id"] for r in dsr_data.get("selection_rules", [])]
    om_ids = [e["entry_id"] for e in om_data.get("minimization_entries", [])]
    rb_ids = [e["entry_id"] for e in rb_data.get("behavior_entries", [])]

    # Validate Pruning Entries
    for entry in pruning_data.get("pruning_entries", []):
        results["branch_pruning_validation"]["pruning_count"] += 1
        
        # Check target operator
        if entry.get("target_operator") not in op_symbols:
             results["branch_pruning_validation"]["status"] = "warning"
             results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown operator: {entry['target_operator']}")
        
        # Check target law
        if entry.get("target_law") not in law_ids:
             results["branch_pruning_validation"]["status"] = "warning"
             results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown law: {entry['target_law']}")

        # Check pruning class
        if entry.get("pruning_class") not in pruning_classes:
             results["branch_pruning_validation"]["status"] = "warning"
             results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown class: {entry['pruning_class']}")

        # Check branch bound
        if entry.get("branch_bound") not in branch_bounds:
             results["branch_pruning_validation"]["status"] = "warning"
             results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown bound: {entry['branch_bound']}")

        # Check selection dependency
        for dsr in entry.get("selection_dependency", []):
            if dsr not in dsr_ids:
                results["branch_pruning_validation"]["status"] = "warning"
                results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown selection rule: {dsr}")

        # Check orientation dependency
        for om in entry.get("orientation_dependency", []):
            if om not in om_ids:
                results["branch_pruning_validation"]["status"] = "warning"
                results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown orientation rule: {om}")

        # Check residue dependency
        for rb in entry.get("residue_dependency", []):
            if rb not in rb_ids:
                results["branch_pruning_validation"]["status"] = "warning"
                results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown residue behavior: {rb}")

        # Check stability implication
        if entry.get("stability_implication") not in stability_implications:
             results["branch_pruning_validation"]["status"] = "warning"
             results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown stability implication: {entry['stability_implication']}")

        # Check convergence implication
        if entry.get("convergence_implication") not in convergence_implications:
             results["branch_pruning_validation"]["status"] = "warning"
             results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown convergence implication: {entry['convergence_implication']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["branch_pruning_validation"]["status"] = "warning"
                results["branch_pruning_validation"]["warnings"].append(f"Branch pruning {entry['entry_id']} references unknown failure mode: {fm}")

        results["branch_pruning_validation"]["open_questions"].extend(entry.get("open_questions", []))

    results["branch_pruning_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate branch pruning registries.")
    parser.add_argument("--pruning", default="registry/math/branch_pruning_registry.json")
    parser.add_argument("--stability", default="registry/math/branch_stability_registry.json")
    parser.add_argument("--failures", default="registry/math/branch_failure_mode_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    parser.add_argument("--dsr", default="registry/math/delta_selection_registry.json")
    parser.add_argument("--om", default="registry/math/orientation_minimization_registry.json")
    parser.add_argument("--rb", default="registry/math/residue_transport_behavior_registry.json")
    
    args = parser.parse_args()
    res = validate_branch_pruning(args.pruning, args.stability, args.failures, args.operators, args.laws, args.dsr, args.om, args.rb)
    print(json.dumps(res, indent=2))
