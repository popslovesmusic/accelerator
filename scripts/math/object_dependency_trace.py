import json
import os
import argparse

def trace_object_dependencies(query, obj_reg, op_reg):
    try:
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
    except Exception as e:
        return {"error": str(e)}

    trace = {
        "query": query,
        "matching_objects": [],
        "dependent_operators": [],
        "provisional_warnings": []
    }

    # Find objects
    for obj in obj_data.get("object_classes", []):
        if query.lower() in obj["class"].lower() or query.lower() in obj["description"].lower():
            trace["matching_objects"].append(obj)
            if obj.get("provisional_status"):
                trace["provisional_warnings"].append(f"Object {obj['class']} is provisional.")

    # Find operators using these objects
    matched_classes = [o["class"] for o in trace["matching_objects"]]
    for op in op_data.get("operators", []):
        if any(d in matched_classes for d in op.get("domain", [])) or \
           any(c in matched_classes for c in op.get("codomain", [])) or \
           query.lower() in op["symbol"].lower() or query.lower() in op["name"].lower():
            trace["dependent_operators"].append(op)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace formal object dependencies.")
    parser.add_argument("--query", required=True, help="Object or operator to trace.")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    
    args = parser.parse_args()
    res = trace_object_dependencies(args.query, args.objects, args.operators)
    print(json.dumps(res, indent=2))
