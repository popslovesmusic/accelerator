import json
import os
import argparse

def trace_delta_selection(query_id, selection_reg):
    try:
        with open(selection_reg, 'r') as f: selection_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by selection_id or selection_class
    rules = [r for r in selection_data.get("selection_rules", []) if r["selection_id"] == query_id or r["selection_class"] == query_id]
    
    if not rules:
        return {"error": f"Selection data for {query_id} not found in {selection_reg}"}

    trace = {
        "delta_selection_trace": {
            "query_id": query_id,
            "associated_rules": []
        }
    }

    for rule in rules:
        rule_trace = {
            "selection_id": rule["selection_id"],
            "selection_class": rule["selection_class"],
            "ambiguity_behavior": rule["ambiguity_behavior"],
            "expected_behavior": rule["expected_behavior"],
            "dependencies": {
                "inputs": rule["input_objects"],
                "stability": rule["stability_dependency"]
            },
            "failure_risks": rule["failure_modes"]
        }
        trace["delta_selection_trace"]["associated_rules"].append(rule_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace delta selection dependencies.")
    parser.add_argument("--query", required=True, help="Selection ID or Class ID (e.g., DSR-001 or orientation_minimization)")
    parser.add_argument("--selection", default="registry/math/delta_selection_registry.json")
    
    args = parser.parse_args()
    res = trace_delta_selection(args.query, args.selection)
    print(json.dumps(res, indent=2))
