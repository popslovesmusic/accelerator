import json
import os
import argparse

def validate_formal_objects(obj_reg, op_reg, rel_reg):
    results = {
        "formal_object_validation": {
            "status": "pass",
            "object_count": 0,
            "operator_count": 0,
            "relation_count": 0,
            "warnings": [],
            "open_questions": [],
            "closure_gaps": []
        }
    }

    try:
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(rel_reg, 'r') as f: rel_data = json.load(f)
    except Exception as e:
        results["formal_object_validation"]["status"] = "fail"
        results["formal_object_validation"]["warnings"].append(f"Load error: {e}")
        return results

    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]
    results["formal_object_validation"]["object_count"] = len(obj_classes)

    # Validate Operators
    for op in op_data.get("operators", []):
        results["formal_object_validation"]["operator_count"] += 1
        # Check domain/codomain
        for d in op.get("domain", []):
            if d not in obj_classes:
                results["formal_object_validation"]["status"] = "warning"
                results["formal_object_validation"]["warnings"].append(f"Operator {op['symbol']} references unknown domain object: {d}")
        for c in op.get("codomain", []):
            if c not in obj_classes:
                results["formal_object_validation"]["status"] = "warning"
                results["formal_object_validation"]["warnings"].append(f"Operator {op['symbol']} references unknown codomain object: {c}")
        
        if op.get("closure_status") == "undefined":
            results["formal_object_validation"]["closure_gaps"].append(f"Operator {op['symbol']} has undefined closure.")
        
        results["formal_object_validation"]["open_questions"].extend(op.get("open_questions", []))

    # Validate Relations
    for rel in rel_data.get("relations", []):
        results["formal_object_validation"]["relation_count"] += 1
        if not rel.get("provisional_status"):
            results["formal_object_validation"]["warnings"].append(f"Relation {rel['name']} missing provisional_status label.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate formal object registries.")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--relations", default="registry/math/relation_registry.json")
    
    args = parser.parse_args()
    res = validate_formal_objects(args.objects, args.operators, args.relations)
    print(json.dumps(res, indent=2))
