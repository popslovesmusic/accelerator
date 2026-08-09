import json
import os
import argparse

def validate_navt_identity(scaffold_path, theorem_reg, obligation_reg, op_reg):
    results = {
        "navt_identity_validation": {
            "status": "pass",
            "condition_count": 0,
            "step_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(scaffold_path, 'r') as f: scaffold_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
        with open(obligation_reg, 'r') as f: obligation_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
    except Exception as e:
        results["navt_identity_validation"]["status"] = "fail"
        results["navt_identity_validation"]["warnings"].append(f"Load error: {e}")
        return results

    scaffold = scaffold_data.get("proof_scaffold", {})
    results["navt_identity_validation"]["condition_count"] = len(scaffold.get("conditions", []))
    results["navt_identity_validation"]["step_count"] = len(scaffold.get("symbolic_steps", []))

    # Check References
    law_id = scaffold.get("theorem_reference")
    if law_id != "MT-002":
        results["navt_identity_validation"]["status"] = "warning"
        results["navt_identity_validation"]["warnings"].append(f"Scaffold references theorem {law_id}, expected MT-002")

    # Check NavT presence
    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    if "NavT" not in op_symbols:
        results["navt_identity_validation"]["status"] = "fail"
        results["navt_identity_validation"]["warnings"].append("Operator NavT not found in operator_registry.json")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate NavT identity proof scaffold.")
    parser.add_argument("--scaffold", default="registry/math/navt_identity_proof_scaffold.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    parser.add_argument("--obligations", default="registry/math/proof_obligation_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    
    args = parser.parse_args()
    res = validate_navt_identity(args.scaffold, args.theorems, args.obligations, args.operators)
    print(json.dumps(res, indent=2))
