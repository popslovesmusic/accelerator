import json
import os
import argparse

def trace_recursive_convergence(query_id, conv_reg, basin_reg):
    try:
        with open(conv_reg, 'r') as f: conv_data = json.load(f)
        with open(basin_reg, 'r') as f: basin_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id or target
    entries = [e for e in conv_data.get("convergence_entries", []) if e["entry_id"] == query_id or e["target"] == query_id]
    
    if not entries:
        return {"error": f"Recursive convergence data for {query_id} not found."}

    trace = {
        "recursive_convergence_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        conv_class = next((c for c in conv_data["convergence_classes"] if c["class"] == entry["convergence_class"]), {"meaning": "unknown"})
        
        trace["recursive_convergence_trace"]["associated_entries"].append({
            "entry_id": entry["entry_id"],
            "target": entry["target"],
            "convergence_class": entry["convergence_class"],
            "class_meaning": conv_class["meaning"],
            "conditions": entry["conditions"],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace recursive convergence dependencies.")
    parser.add_argument("--query", required=True, help="Target ID or Entry ID (e.g., MPF-RCV-001 or RCNV-001)")
    parser.add_argument("--conv", default="registry/math/recursive_convergence_registry.json")
    parser.add_argument("--basin", default="registry/math/recurrence_basin_registry.json")
    
    args = parser.parse_args()
    res = trace_recursive_convergence(args.query, args.conv, args.basin)
    print(json.dumps(res, indent=2))
