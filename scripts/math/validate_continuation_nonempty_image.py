import json
import os
import argparse

def validate_continuation_nonempty_image(scaffold_path, theorem_reg, obligation_reg, op_reg, obj_reg):
    results = {
        "continuation_nonempty_image_validation": {
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
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
    except Exception as e:
        results["continuation_nonempty_image_validation"]["status"] = "fail"
        results["continuation_nonempty_image_validation"]["warnings"].append(f"Load error: {e}")
        return results

    scaffold = scaffold_data.get("proof_scaffold", {})
    results["continuation_nonempty_image_validation"]["condition_count"] = len(scaffold.get("conditions", []))
    results["continuation_nonempty_image_validation"]["step_count"] = len(scaffold.get("symbolic_steps", []))

    # Check References
    law_id = scaffold.get("theorem_reference")
    if law_id != "MT-003":
        results["continuation_nonempty_image_validation"]["status"] = "warning"
        results["continuation_nonempty_image_validation"]["warnings"].append(f"Scaffold references theorem {law_id}, expected MT-003")

    # Check Operators
    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    for target in ["Pi_A", "delta"]:
        if target not in op_symbols:
            results["continuation_nonempty_image_validation"]["status"] = "fail"
            results["continuation_nonempty_image_validation"]["warnings"].append(f"Operator {target} not found in operator_registry.json")

    # Check Objects
    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]
    for obj in ["continuation_event", "participation_space", "admissibility_window"]:
        if obj not in obj_classes:
             results["continuation_nonempty_image_validation"]["status"] = "warning"
             results["continuation_nonempty_image_validation"]["warnings"].append(f"Object class {obj} not found in formal_object_registry.json")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate MT-003 proof scaffold.")
    parser.add_argument("--scaffold", default="registry/math/continuation_nonempty_image_proof_scaffold.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    parser.add_argument("--obligations", default="registry/math/proof_obligation_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    
    args = parser.parse_args()
    res = validate_continuation_nonempty_image(args.scaffold, args.theorems, args.obligations, args.operators, args.objects)
    print(json.dumps(res, indent=2))
