import json
import os
import argparse

def trace_recursive_transport_closure(query_id, closure_reg, metric_reg):
    try:
        with open(closure_reg, 'r') as f: closure_data = json.load(f)
        with open(metric_reg, 'r') as f: metric_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in closure entries
    entries = [e for e in closure_data.get("closure_entries", []) if query_id == e.get("entry_id") or query_id == e.get("target") or query_id == e.get("closure_class")]
    
    if not entries:
        return {"error": f"Recursive transport-closure data for {query_id} not found."}

    trace = {
        "recursive_transport_closure_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        closure_class = next((c for c in closure_data["transport_closure_classes"] if c["class"] == entry["closure_class"]), {"meaning": "unknown"})
        metric_class = next((m for m in metric_data["transport_metric_classes"] if m["class"] == entry["metric_class"]), {"meaning": "unknown"})
        
        trace["recursive_transport_closure_trace"]["associated_entries"].append({
            "entry_id": entry["entry_id"],
            "target": entry["target"],
            "closure_class": entry["closure_class"],
            "closure_meaning": closure_class["meaning"],
            "metric_class": entry["metric_class"],
            "metric_meaning": metric_class["meaning"],
            "iteration_scope": entry["iteration_scope"],
            "conditions": entry["conditions"],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace recursive transport-closure dependencies.")
    parser.add_argument("--query", required=True, help="Target ID or Entry ID (e.g., NavT or RTC-001)")
    parser.add_argument("--closure", default="registry/math/recursive_transport_closure_registry.json")
    parser.add_argument("--metrics", default="registry/math/transport_distance_metric_registry.json")
    
    args = parser.parse_args()
    res = trace_recursive_transport_closure(args.query, args.closure, args.metrics)
    print(json.dumps(res, indent=2))
