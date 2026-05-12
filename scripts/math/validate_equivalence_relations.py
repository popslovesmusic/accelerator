import json
import os
import argparse

def validate_equivalence_relations(equiv_reg, class_reg, failure_reg, op_reg, law_regs, theorem_reg):
    results = {
        "equivalence_relation_validation": {
            "status": "pass",
            "relation_count": 0,
            "class_type_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(equiv_reg, 'r') as f: equiv_data = json.load(f)
        with open(class_reg, 'r') as f: class_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["equivalence_relation_validation"]["status"] = "fail"
        results["equivalence_relation_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection", "residue_update", "NavT", "Pi_A", "delta"])
    
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    relation_classes = [rc["class"] for rc in equiv_data.get("equivalence_relation_classes", [])]

    # Validate Equivalence Entries
    for entry in equiv_data.get("equivalence_relation_entries", []):
        results["equivalence_relation_validation"]["relation_count"] += 1
        
        # Check relation class
        if entry.get("relation_class") not in relation_classes:
             results["equivalence_relation_validation"]["status"] = "warning"
             results["equivalence_relation_validation"]["warnings"].append(f"Equivalence entry {entry['entry_id']} references unknown class: {entry['relation_class']}")

        # Check supported theorems
        for tid in entry.get("supports_theorems", []):
            if tid not in theorem_ids:
                results["equivalence_relation_validation"]["status"] = "warning"
                results["equivalence_relation_validation"]["warnings"].append(f"Equivalence entry {entry['entry_id']} references unknown theorem: {tid}")

        # Check supported operators
        for op in entry.get("supports_operators", []):
            if op not in op_symbols:
                results["equivalence_relation_validation"]["status"] = "warning"
                results["equivalence_relation_validation"]["warnings"].append(f"Equivalence entry {entry['entry_id']} references unknown operator: {op}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["equivalence_relation_validation"]["status"] = "warning"
                results["equivalence_relation_validation"]["warnings"].append(f"Equivalence entry {entry['entry_id']} references unknown failure mode: {fm}")

        results["equivalence_relation_validation"]["open_questions"].extend(entry.get("open_questions", []))

    results["equivalence_relation_validation"]["class_type_count"] = len(class_data.get("equivalence_class_types", []))
    results["equivalence_relation_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate equivalence relation registries.")
    parser.add_argument("--equivalence", default="registry/math/equivalence_relation_registry.json")
    parser.add_argument("--classes", default="registry/math/equivalence_class_registry.json")
    parser.add_argument("--failures", default="registry/math/equivalence_failure_mode_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    
    args = parser.parse_args()
    res = validate_equivalence_relations(args.equivalence, args.classes, args.failures, args.operators, args.laws, args.theorems)
    print(json.dumps(res, indent=2))
