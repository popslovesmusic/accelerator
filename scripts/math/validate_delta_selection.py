import json
import os
import argparse

def validate_delta_selection(selection_reg, failure_reg, obj_reg, op_reg):
    results = {
        "delta_selection_validation": {
            "status": "pass",
            "rule_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(selection_reg, 'r') as f: selection_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
    except Exception as e:
        results["delta_selection_validation"]["status"] = "fail"
        results["delta_selection_validation"]["warnings"].append(f"Load error: {e}")
        return results

    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]
    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    selection_classes = [sc["selection_class"] for sc in selection_data.get("selection_classes", [])]

    # Validate Rules
    for rule in selection_data.get("selection_rules", []):
        results["delta_selection_validation"]["rule_count"] += 1
        
        # Check target operator
        if rule.get("target_operator") not in op_symbols:
             results["delta_selection_validation"]["status"] = "warning"
             results["delta_selection_validation"]["warnings"].append(f"Selection rule {rule['selection_id']} references unknown operator: {rule['target_operator']}")
        
        # Check selection class
        if rule.get("selection_class") not in selection_classes:
             results["delta_selection_validation"]["status"] = "warning"
             results["delta_selection_validation"]["warnings"].append(f"Selection rule {rule['selection_id']} references unknown selection class: {rule['selection_class']}")

        # Check input objects
        for obj in rule.get("input_objects", []):
            if obj not in obj_classes:
                results["delta_selection_validation"]["status"] = "warning"
                results["delta_selection_validation"]["warnings"].append(f"Selection rule {rule['selection_id']} references unknown input object: {obj}")
        
        # Check failure modes
        for fm in rule.get("failure_modes", []):
            if fm not in fm_ids:
                results["delta_selection_validation"]["status"] = "warning"
                results["delta_selection_validation"]["warnings"].append(f"Selection rule {rule['selection_id']} references unknown failure mode: {fm}")

        results["delta_selection_validation"]["open_questions"].extend(rule.get("open_questions", []))

    results["delta_selection_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate delta selection registries.")
    parser.add_argument("--selection", default="registry/math/delta_selection_registry.json")
    parser.add_argument("--failures", default="registry/math/delta_selection_failure_modes.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    
    args = parser.parse_args()
    res = validate_delta_selection(args.selection, args.failures, args.objects, args.operators)
    print(json.dumps(res, indent=2))
