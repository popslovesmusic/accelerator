import json
import os
import argparse

def trace_operational_stability_baseline(query_id, baseline_reg):
    try:
        with open(baseline_reg, 'r') as f: baseline_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id or target
    entries = [e for e in baseline_data.get("baseline_entries", []) if e["entry_id"] == query_id or e["target"] == query_id]
    
    if not entries:
        return {"error": f"Stability baseline data for {query_id} not found."}

    trace = {
        "operational_stability_baseline_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        trace["operational_stability_baseline_trace"]["associated_entries"].append({
            "entry_id": entry["entry_id"],
            "target": entry["target"],
            "expected_class": entry["expected_class"],
            "metrics": entry["associated_metrics"],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace operational stability baseline dependencies.")
    parser.add_argument("--query", required=True, help="Target ID or Entry ID (e.g., NavT or SB-001)")
    parser.add_argument("--baseline", default="registry/math/operational_stability_baseline_registry.json")
    
    args = parser.parse_args()
    res = trace_operational_stability_baseline(args.query, args.baseline)
    print(json.dumps(res, indent=2))
