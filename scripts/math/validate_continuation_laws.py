import json
import os
import argparse

def validate_continuation_laws(law_reg, val_reg, obj_reg, op_reg):
    results = {
        "continuation_law_validation": {
            "status": "pass",
            "law_count": 0,
            "validator_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(law_reg, 'r') as f: law_data = json.load(f)
        with open(val_reg, 'r') as f: val_data = json.load(f)
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
    except Exception as e:
        results["continuation_law_validation"]["status"] = "fail"
        results["continuation_law_validation"]["warnings"].append(f"Load error: {e}")
        return results

    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]
    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]

    # Validate Laws
    for law in law_data.get("laws", []):
        results["continuation_law_validation"]["law_count"] += 1
        # Check source expression
        if not law.get("source_expression"):
             results["continuation_law_validation"]["status"] = "warning"
             results["continuation_law_validation"]["warnings"].append(f"Law {law['law_id']} missing source_expression.")

        # Check input/output objects
        for obj in law.get("input_objects", []):
            if obj not in obj_classes:
                results["continuation_law_validation"]["status"] = "warning"
                results["continuation_law_validation"]["warnings"].append(f"Law {law['law_id']} references unknown input object: {obj}")
        for obj in law.get("output_objects", []):
            if obj not in obj_classes:
                results["continuation_law_validation"]["status"] = "warning"
                results["continuation_law_validation"]["warnings"].append(f"Law {law['law_id']} references unknown output object: {obj}")
        
        # Check operators
        for op in law.get("operators", []):
            if op not in op_symbols:
                results["continuation_law_validation"]["status"] = "warning"
                results["continuation_law_validation"]["warnings"].append(f"Law {law['law_id']} references unknown operator: {op}")

        results["continuation_law_validation"]["open_questions"].extend(law.get("open_questions", []))

    # Validate Validators
    for validator in val_data.get("validators", []):
        results["continuation_law_validation"]["validator_count"] += 1
        # Check law reference
        law_ids = [l["law_id"] for l in law_data.get("laws", [])]
        if validator.get("law_reference") not in law_ids:
             results["continuation_law_validation"]["status"] = "warning"
             results["continuation_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown law: {validator['law_reference']}")
        
        # Check input types
        for input_spec in validator.get("inputs", []):
            if input_spec["type"] not in obj_classes and input_spec["type"] not in ["float", "int", "string", "bool"]:
                results["continuation_law_validation"]["status"] = "warning"
                results["continuation_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown input type: {input_spec['type']}")
        
        # Check output types
        for output_spec in validator.get("outputs", []):
            if output_spec["type"] not in obj_classes:
                results["continuation_law_validation"]["status"] = "warning"
                results["continuation_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown output type: {output_spec['type']}")

        # Ensure success condition present
        if not validator.get("success_conditions"):
            results["continuation_law_validation"]["status"] = "warning"
            results["continuation_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} missing success_conditions.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate continuation law registries.")
    parser.add_argument("--laws", default="registry/math/continuation_law_registry.json")
    parser.add_argument("--validators", default="registry/math/continuation_validator_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    
    args = parser.parse_args()
    res = validate_continuation_laws(args.laws, args.validators, args.objects, args.operators)
    print(json.dumps(res, indent=2))
