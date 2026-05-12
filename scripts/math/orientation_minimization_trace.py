import json
import os
import argparse

def trace_orientation_minimization(query_id, minimization_reg):
    try:
        with open(minimization_reg, 'r') as f: min_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id, target_operator, or target_law
    entries = [e for e in min_data.get("minimization_entries", []) if e["entry_id"] == query_id or e["target_operator"] == query_id or e["target_law"] == query_id]
    
    if not entries:
        return {"error": f"Orientation minimization data for {query_id} not found in {minimization_reg}"}

    trace = {
        "orientation_minimization_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        entry_trace = {
            "entry_id": entry["entry_id"],
            "target_operator": entry["target_operator"],
            "target_law": entry["target_law"],
            "rule_class": entry["rule_class"],
            "orientation_metric": entry["orientation_metric"],
            "tie_behavior": entry["tie_behavior"],
            "implications": {
                "stability": entry["stability_implication"]
            },
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        }
        trace["orientation_minimization_trace"]["associated_entries"].append(entry_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace orientation minimization dependencies.")
    parser.add_argument("--query", required=True, help="Entry ID, Operator ID, or Law ID (e.g., OMR-001 or delta)")
    parser.add_argument("--minimization", default="registry/math/orientation_minimization_registry.json")
    
    args = parser.parse_args()
    res = trace_orientation_minimization(args.query, args.minimization)
    print(json.dumps(res, indent=2))
