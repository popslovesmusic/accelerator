import json
import os
import argparse

def validate_operator_functional_forms(form_reg, symbol_reg, failure_reg, op_reg):
    results = {
        "operator_functional_form_validation": {
            "status": "pass",
            "entry_count": 0,
            "symbolic_form_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(form_reg, 'r') as f: form_data = json.load(f)
        with open(symbol_reg, 'r') as f: symbol_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
    except Exception as e:
        results["operator_functional_form_validation"]["status"] = "fail"
        results["operator_functional_form_validation"]["errors"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    form_ids = [s["form_id"] for s in symbol_data.get("symbolic_forms", [])]

    # Validate Entries
    for entry in form_data.get("functional_form_entries", []):
        results["operator_functional_form_validation"]["entry_count"] += 1
        
        # Check operator
        if entry.get("operator") not in op_symbols:
             results["operator_functional_form_validation"]["status"] = "warning"
             results["operator_functional_form_validation"]["warnings"].append(f"Functional entry references unknown operator: {entry['operator']}")
        
        # Check primary candidate
        if entry.get("primary_candidate") not in form_ids:
             results["operator_functional_form_validation"]["status"] = "warning"
             results["operator_functional_form_validation"]["warnings"].append(f"Entry {entry['operator']} references unknown candidate: {entry['primary_candidate']}")

    results["operator_functional_form_validation"]["symbolic_form_count"] = len(form_ids)
    results["operator_functional_form_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate operator functional form registries.")
    parser.add_argument("--form", default="registry/math/operator_functional_form_registry.json")
    parser.add_argument("--symbol", default="registry/math/candidate_symbolic_form_registry.json")
    parser.add_argument("--failures", default="registry/math/functional_form_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    
    args = parser.parse_args()
    res = validate_operator_functional_forms(args.form, args.symbol, args.failures, args.operators)
    print(json.dumps(res, indent=2))
