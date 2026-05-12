import json
import os
import argparse

def validate_residue_coupling_laws(law_reg, val_reg, obj_reg, op_reg, pv_reg, cv_reg):
    results = {
        "residue_coupling_law_validation": {
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
        
        # Check prerequisite registries existence
        if not os.path.exists(pv_reg):
            results["residue_coupling_law_validation"]["status"] = "fail"
            results["residue_coupling_law_validation"]["warnings"].append(f"Prerequisite registry missing: {pv_reg}")
        if not os.path.exists(cv_reg):
            results["residue_coupling_law_validation"]["status"] = "fail"
            results["residue_coupling_law_validation"]["warnings"].append(f"Prerequisite registry missing: {cv_reg}")
            
    except Exception as e:
        results["residue_coupling_law_validation"]["status"] = "fail"
        results["residue_coupling_law_validation"]["warnings"].append(f"Load error: {e}")
        return results

    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]
    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]

    # Validate Laws
    for law in law_data.get("laws", []):
        results["residue_coupling_law_validation"]["law_count"] += 1
        
        # Check source expression
        if not law.get("source_expression"):
             results["residue_coupling_law_validation"]["status"] = "warning"
             results["residue_coupling_law_validation"]["warnings"].append(f"Law {law['law_id']} missing source_expression.")

        # Check input/output objects
        for obj in law.get("input_objects", []):
            if obj not in obj_classes:
                results["residue_coupling_law_validation"]["status"] = "warning"
                results["residue_coupling_law_validation"]["warnings"].append(f"Law {law['law_id']} references unknown input object: {obj}")
        for obj in law.get("output_objects", []):
            if obj not in obj_classes:
                results["residue_coupling_law_validation"]["status"] = "warning"
                results["residue_coupling_law_validation"]["warnings"].append(f"Law {law['law_id']} references unknown output object: {obj}")
        
        # Check operators
        for op in law.get("operators", []):
            if op not in op_symbols:
                results["residue_coupling_law_validation"]["status"] = "warning"
                results["residue_coupling_law_validation"]["warnings"].append(f"Law {law['law_id']} references unknown operator: {op}")

        results["residue_coupling_law_validation"]["open_questions"].extend(law.get("open_questions", []))

    # Validate Validators
    for validator in val_data.get("validators", []):
        results["residue_coupling_law_validation"]["validator_count"] += 1
        # Check law reference
        law_ids = [l["law_id"] for l in law_data.get("laws", [])]
        if validator.get("law_reference") not in law_ids:
             results["residue_coupling_law_validation"]["status"] = "warning"
             results["residue_coupling_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown law: {validator['law_reference']}")
        
        # Check input types
        for input_spec in validator.get("inputs", []):
            if input_spec["type"] not in obj_classes and input_spec["type"] not in ["float", "int", "string", "bool"]:
                results["residue_coupling_law_validation"]["status"] = "warning"
                results["residue_coupling_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown input type: {input_spec['type']}")
        
        # Check output types
        for output_spec in validator.get("outputs", []):
            if output_spec["type"] not in obj_classes:
                results["residue_coupling_law_validation"]["status"] = "warning"
                results["residue_coupling_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} references unknown output type: {output_spec['type']}")

        # Ensure success condition present
        if not validator.get("success_conditions"):
            results["residue_coupling_law_validation"]["status"] = "warning"
            results["residue_coupling_law_validation"]["warnings"].append(f"Validator {validator['validator_id']} missing success_conditions.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate residue coupling law registries.")
    parser.add_argument("--laws", default="registry/math/residue_coupling_law_registry.json")
    parser.add_argument("--validators", default="registry/math/residue_coupling_validator_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--pv_reg", default="registry/math/participation_law_registry.json")
    parser.add_argument("--cv_reg", default="registry/math/continuation_law_registry.json")
    
    args = parser.parse_args()
    res = validate_residue_coupling_laws(args.laws, args.validators, args.objects, args.operators, args.pv_reg, args.cv_reg)
    print(json.dumps(res, indent=2))
