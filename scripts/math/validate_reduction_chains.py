import json
import os
import argparse

def validate_reduction_chains(rc_reg, gap_reg, obj_reg, op_reg, rel_reg):
    results = {
        "reduction_chain_validation": {
            "status": "pass",
            "chain_count": 0,
            "step_count": 0,
            "unresolved_dependencies": [],
            "nonformal_steps": [],
            "closure_gaps": [],
            "open_questions": [],
            "warnings": []
        }
    }

    try:
        with open(rc_reg, 'r') as f: rc_data = json.load(f)
        with open(gap_reg, 'r') as f: gap_data = json.load(f)
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(rel_reg, 'r') as f: rel_data = json.load(f)
    except Exception as e:
        results["reduction_chain_validation"]["status"] = "fail"
        results["reduction_chain_validation"]["warnings"].append(f"Load error: {e}")
        return results

    # Gather valid symbols
    valid_objs = [o["class"] for o in obj_data.get("object_classes", [])]
    valid_ops = [o["symbol"] for o in op_data.get("operators", [])]
    valid_rels = [r["name"] for r in rel_data.get("relations", [])]
    valid_gaps = [g["id"] for g in gap_data.get("gaps", [])]

    for entry in rc_data.get("entries", []):
        results["reduction_chain_validation"]["chain_count"] += 1
        symbol = entry["entry_id"]

        # Validate dependencies
        for op in entry.get("operator_dependencies", []):
            if op not in valid_ops:
                results["reduction_chain_validation"]["unresolved_dependencies"].append(f"Chain {symbol} references unknown operator: {op}")
        for obj in entry.get("object_dependencies", []):
            if obj not in valid_objs:
                results["reduction_chain_validation"]["unresolved_dependencies"].append(f"Chain {symbol} references unknown object: {obj}")

        # Validate steps
        for step in entry.get("reduction_steps", []):
            results["reduction_chain_validation"]["step_count"] += 1
            if step.get("status") != "formal":
                results["reduction_chain_validation"]["nonformal_steps"].append(step["step_id"])
            
            for gap in step.get("known_gaps", []):
                if gap not in valid_gaps:
                    results["reduction_chain_validation"]["warnings"].append(f"Step {step['step_id']} references unknown gap: {gap}")

        if entry.get("closure_status") in ["undefined", "partial"]:
            results["reduction_chain_validation"]["closure_gaps"].append(symbol)

    if results["reduction_chain_validation"]["unresolved_dependencies"] or results["reduction_chain_validation"]["warnings"]:
        results["reduction_chain_validation"]["status"] = "warning"

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate formal reduction chains.")
    parser.add_argument("--rc", default="registry/math/reduction_chain_registry.json")
    parser.add_argument("--gaps", default="registry/math/reduction_gap_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--relations", default="registry/math/relation_registry.json")
    
    args = parser.parse_args()
    res = validate_reduction_chains(args.rc, args.gaps, args.objects, args.operators, args.relations)
    print(json.dumps(res, indent=2))
