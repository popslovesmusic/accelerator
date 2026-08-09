import json
import os
import argparse

def validate_reconstruction_uniqueness(uniqueness_reg, constraint_reg, failure_reg, op_reg, law_regs, om_reg, rb_reg, ntc_reg, bp_reg):
    results = {
        "reconstruction_uniqueness_validation": {
            "status": "pass",
            "entry_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(uniqueness_reg, 'r') as f: uni_data = json.load(f)
        with open(constraint_reg, 'r') as f: con_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(om_reg, 'r') as f: om_data = json.load(f)
        with open(rb_reg, 'r') as f: rb_data = json.load(f)
        with open(ntc_reg, 'r') as f: ntc_data = json.load(f)
        with open(bp_reg, 'r') as f: bp_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["reconstruction_uniqueness_validation"]["status"] = "fail"
        results["reconstruction_uniqueness_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    # Include observable_projection as a valid target even if not a primitive operator
    op_symbols.append("observable_projection")
    
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    uniqueness_classes = [c["class"] for c in uni_data.get("uniqueness_classes", [])]
    constraint_classes = [c["class"] for c in con_data.get("constraint_classes", [])]
    ambiguity_behaviors = ["none", "bounded", "equivalence_class", "branching", "undefined"]
    
    om_ids = [e["entry_id"] for e in om_data.get("minimization_entries", [])]
    rb_ids = [e["entry_id"] for e in rb_data.get("behavior_entries", [])]
    ntc_ids = [e["entry_id"] for e in ntc_data.get("transport_entries", [])]
    bp_ids = [e["entry_id"] for e in bp_data.get("pruning_entries", [])]

    # Validate Uniqueness Entries
    for entry in uni_data.get("uniqueness_entries", []):
        results["reconstruction_uniqueness_validation"]["entry_count"] += 1
        
        # Check target operator
        if entry.get("target_operator") not in op_symbols:
             results["reconstruction_uniqueness_validation"]["status"] = "warning"
             results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown operator: {entry['target_operator']}")
        
        # Check target law
        if entry.get("target_law") != "none" and entry.get("target_law") not in law_ids:
             results["reconstruction_uniqueness_validation"]["status"] = "warning"
             results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown law: {entry['target_law']}")

        # Check uniqueness class
        if entry.get("uniqueness_class") not in uniqueness_classes:
             results["reconstruction_uniqueness_validation"]["status"] = "warning"
             results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown uniqueness class: {entry['uniqueness_class']}")

        # Check constraint classes
        for cc in entry.get("constraint_classes", []):
            if cc not in constraint_classes:
                results["reconstruction_uniqueness_validation"]["status"] = "warning"
                results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown constraint class: {cc}")

        # Check ambiguity behavior
        if entry.get("ambiguity_behavior") not in ambiguity_behaviors:
             results["reconstruction_uniqueness_validation"]["status"] = "warning"
             results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown ambiguity behavior: {entry['ambiguity_behavior']}")

        # Check dependencies
        for om in entry.get("orientation_dependency", []):
            if om not in om_ids:
                results["reconstruction_uniqueness_validation"]["status"] = "warning"
                results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown orientation rule: {om}")
        
        for rb in entry.get("residue_dependency", []):
            if rb not in rb_ids:
                results["reconstruction_uniqueness_validation"]["status"] = "warning"
                results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown residue behavior: {rb}")

        for ntc in entry.get("transport_dependency", []):
            if ntc not in ntc_ids:
                results["reconstruction_uniqueness_validation"]["status"] = "warning"
                results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown transport closure: {ntc}")

        for bp in entry.get("branch_dependency", []):
            if bp not in bp_ids:
                results["reconstruction_uniqueness_validation"]["status"] = "warning"
                results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown branch pruning: {bp}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["reconstruction_uniqueness_validation"]["status"] = "warning"
                results["reconstruction_uniqueness_validation"]["warnings"].append(f"Uniqueness entry {entry['entry_id']} references unknown failure mode: {fm}")

        results["reconstruction_uniqueness_validation"]["open_questions"].extend(entry.get("open_questions", []))

    results["reconstruction_uniqueness_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate reconstruction uniqueness registries.")
    parser.add_argument("--uniqueness", default="registry/math/reconstruction_uniqueness_registry.json")
    parser.add_argument("--constraints", default="registry/math/preimage_constraint_registry.json")
    parser.add_argument("--failures", default="registry/math/reconstruction_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    parser.add_argument("--om", default="registry/math/orientation_minimization_registry.json")
    parser.add_argument("--rb", default="registry/math/residue_transport_behavior_registry.json")
    parser.add_argument("--ntc", default="registry/math/nonlocal_transport_registry.json")
    parser.add_argument("--bp", default="registry/math/branch_pruning_registry.json")
    
    args = parser.parse_args()
    res = validate_reconstruction_uniqueness(args.uniqueness, args.constraints, args.failures, args.operators, args.laws, args.om, args.rb, args.ntc, args.bp)
    print(json.dumps(res, indent=2))
