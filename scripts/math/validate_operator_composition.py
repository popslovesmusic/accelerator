import json
import os
import argparse

def validate_operator_composition(comp_reg, comm_reg, failure_reg, op_reg):
    results = {
        "operator_composition_validation": {
            "status": "pass",
            "composition_count": 0,
            "commutation_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(comp_reg, 'r') as f: comp_data = json.load(f)
        with open(comm_reg, 'r') as f: comm_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
    except Exception as e:
        results["operator_composition_validation"]["status"] = "fail"
        results["operator_composition_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    # Add non-primitive "operators" referenced in composition
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection"])
    
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    comp_classes = [cc["class"] for cc in comp_data.get("composition_classes", [])]
    comm_statuses = comm_data.get("commutation_statuses", [])

    # Validate Composition Entries
    for entry in comp_data.get("composition_entries", []):
        results["operator_composition_validation"]["composition_count"] += 1
        
        # Check operators
        for op in entry.get("operators", []):
            if op not in op_symbols:
                results["operator_composition_validation"]["status"] = "warning"
                results["operator_composition_validation"]["warnings"].append(f"Composition entry {entry['entry_id']} references unknown operator: {op}")
        
        # Check composition class
        if entry.get("composition_class") not in comp_classes:
             results["operator_composition_validation"]["status"] = "warning"
             results["operator_composition_validation"]["warnings"].append(f"Composition entry {entry['entry_id']} references unknown class: {entry['composition_class']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["operator_composition_validation"]["status"] = "warning"
                results["operator_composition_validation"]["warnings"].append(f"Composition entry {entry['entry_id']} references unknown failure mode: {fm}")

    # Validate Commutation Entries
    for entry in comm_data.get("commutation_entries", []):
        results["operator_composition_validation"]["commutation_count"] += 1
        
        # Check operator pair
        for op in entry.get("operator_pair", []):
            if op not in op_symbols:
                results["operator_composition_validation"]["status"] = "warning"
                results["operator_composition_validation"]["warnings"].append(f"Commutation entry {entry['entry_id']} references unknown operator: {op}")
        
        # Check commutation status
        if entry.get("commutation_status") not in comm_statuses:
             results["operator_composition_validation"]["status"] = "warning"
             results["operator_composition_validation"]["warnings"].append(f"Commutation entry {entry['entry_id']} references unknown status: {entry['commutation_status']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["operator_composition_validation"]["status"] = "warning"
                results["operator_composition_validation"]["warnings"].append(f"Commutation entry {entry['entry_id']} references unknown failure mode: {fm}")

        if not entry.get("reason"):
             results["operator_composition_validation"]["status"] = "warning"
             results["operator_composition_validation"]["warnings"].append(f"Commutation entry {entry['entry_id']} missing reason.")

    results["operator_composition_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate operator composition and commutation registries.")
    parser.add_argument("--composition", default="registry/math/operator_composition_registry.json")
    parser.add_argument("--commutation", default="registry/math/operator_commutation_registry.json")
    parser.add_argument("--failures", default="registry/math/composition_failure_mode_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    
    args = parser.parse_args()
    res = validate_operator_composition(args.composition, args.commutation, args.failures, args.operators)
    print(json.dumps(res, indent=2))
