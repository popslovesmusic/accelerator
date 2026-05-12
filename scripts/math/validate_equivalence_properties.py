import json
import os
import argparse

def validate_equivalence_properties(prop_reg, pres_reg, failure_reg, op_reg, theorem_reg):
    results = {
        "equivalence_property_validation": {
            "status": "pass",
            "property_entry_count": 0,
            "preservation_entry_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(prop_reg, 'r') as f: prop_data = json.load(f)
        with open(pres_reg, 'r') as f: pres_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
    except Exception as e:
        results["equivalence_property_validation"]["status"] = "fail"
        results["equivalence_property_validation"]["errors"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection"])
    
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    
    status_values = prop_data.get("property_status_values", [])
    pres_values = pres_data.get("operator_preservation_status_values", [])

    # Validate Property Entries
    for entry in prop_data.get("property_entries", []):
        results["equivalence_property_validation"]["property_entry_count"] += 1
        for status_key in ["reflexive_status", "symmetric_status", "transitive_status"]:
            if entry.get(status_key) not in status_values:
                results["equivalence_property_validation"]["status"] = "warning"
                results["equivalence_property_validation"]["warnings"].append(f"Entry {entry['entry_id']} has unknown {status_key}: {entry.get(status_key)}")
        
        for tid in entry.get("supported_theorems", []):
            if tid not in theorem_ids:
                results["equivalence_property_validation"]["status"] = "warning"
                results["equivalence_property_validation"]["warnings"].append(f"Entry {entry['entry_id']} references unknown theorem: {tid}")

    # Validate Preservation Entries
    for entry in pres_data.get("preservation_entries", []):
        results["equivalence_property_validation"]["preservation_entry_count"] += 1
        if entry.get("operator") not in op_symbols:
            results["equivalence_property_validation"]["status"] = "warning"
            results["equivalence_property_validation"]["warnings"].append(f"Preservation entry {entry['entry_id']} references unknown operator: {entry['operator']}")
        
        if entry.get("preservation_status") not in pres_values:
            results["equivalence_property_validation"]["status"] = "warning"
            results["equivalence_property_validation"]["warnings"].append(f"Preservation entry {entry['entry_id']} has unknown status: {entry['preservation_status']}")

    results["equivalence_property_validation"]["failure_mode_count"] = len(fm_ids)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate equivalence property registries.")
    parser.add_argument("--prop", default="registry/math/equivalence_property_registry.json")
    parser.add_argument("--pres", default="registry/math/equivalence_preservation_registry.json")
    parser.add_argument("--failures", default="registry/math/equivalence_property_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    
    args = parser.parse_args()
    res = validate_equivalence_properties(args.prop, args.pres, args.failures, args.operators, args.theorems)
    print(json.dumps(res, indent=2))
