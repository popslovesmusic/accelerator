import json
import os
import argparse

def validate_participation_laws(law_reg, val_reg, obj_reg):
    results = {
        "participation_law_validation": {
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
    except Exception as e:
        results["participation_law_validation"]["status"] = "fail"
        results["participation_law_validation"]["warnings"].append(f"Load error: {e}")
        return results

    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]

    # Validate Laws
    for law in law_data.get("laws", []):
        results["participation_law_validation"]["law_count"] += 1
        # Check input/output objects
        for obj in law.get("input_objects", []):
            if obj not in obj_classes:
                results["participation_law_validation"]["status"] = "warning"
                results["participation_law_validation"]["warnings"].append(f"Law {law['law_id']} references unknown input object: {obj}")
        for obj in law.get("output_objects", []):
            if obj not in obj_classes:
                results["participation_law_validation"]["status"] = "warning"
                results["participation_law_validation"]["warnings"].append(f"Law {law['law_id']} references unknown output object: {obj}")
        
        results["participation_law_validation"]["open_questions"].extend(law.get("open_questions", []))

    # Validate Validators
    for validator in val_data.get("validators", []):
        results["participation_law_validation"]["validator_count"] += 1
        # Check law reference
        law_ids = [l["law_id"] for l in law_data.get("laws", [])]
        if validator.get("law_reference") not in law_ids:
             results["participation_law_validation"]["status"] = "warning"
             results["participation_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown law: {validator['law_reference']}")
        
        # Check input/output types
        for input_spec in validator.get("inputs", []):
            if input_spec["type"] not in obj_classes and input_spec["type"] not in ["float", "int", "string", "bool"]:
                results["participation_law_validation"]["status"] = "warning"
                results["participation_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown input type: {input_spec['type']}")
        for output_spec in validator.get("outputs", []):
            if output_spec["type"] not in obj_classes:
                results["participation_law_validation"]["status"] = "warning"
                results["participation_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown output type: {output_spec['type']}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate participation law registries.")
    parser.add_argument("--laws", default="registry/math/participation_law_registry.json")
    parser.add_argument("--validators", default="registry/math/participation_validator_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    
    args = parser.parse_args()
    res = validate_participation_laws(args.laws, args.validators, args.objects)
    print(json.dumps(res, indent=2))
