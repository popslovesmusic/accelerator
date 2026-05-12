import json
import os
import argparse

def trace_selection_uniqueness(query_id, uniqueness_reg, tie_reg):
    try:
        with open(uniqueness_reg, 'r') as f: uniqueness_data = json.load(f)
        with open(tie_reg, 'r') as f: tie_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in uniqueness entries
    entries = [e for e in uniqueness_data.get("uniqueness_entries", []) if query_id == e.get("entry_id") or query_id == e.get("target") or query_id == e.get("uniqueness_class")]
    
    # Search in tie resolution entries
    ties = [t for t in tie_data.get("tie_resolution_entries", []) if query_id == t.get("entry_id") or query_id == t.get("target") or query_id == t.get("tie_resolution_class")]

    if not entries and not ties:
        return {"error": f"Selection uniqueness data for {query_id} not found."}

    trace = {
        "selection_uniqueness_trace": {
            "query_id": query_id,
            "associated_uniqueness_entries": [],
            "associated_tie_resolution_entries": []
        }
    }

    for entry in entries:
        trace["selection_uniqueness_trace"]["associated_uniqueness_entries"].append({
            "entry_id": entry["entry_id"],
            "target": entry["target"],
            "uniqueness_class": entry["uniqueness_class"],
            "conditions": entry["conditions"],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        })

    for entry in ties:
        trace["selection_uniqueness_trace"]["associated_tie_resolution_entries"].append({
            "entry_id": entry["entry_id"],
            "target": entry["target"],
            "tie_resolution_class": entry["tie_resolution_class"],
            "meaning": entry["meaning"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace selection uniqueness dependencies.")
    parser.add_argument("--query", required=True, help="Target ID or Entry ID (e.g., delta or SU-001)")
    parser.add_argument("--uniqueness", default="registry/math/selection_uniqueness_registry.json")
    parser.add_argument("--tie", default="registry/math/selection_tie_resolution_registry.json")
    
    args = parser.parse_args()
    res = trace_selection_uniqueness(args.query, args.uniqueness, args.tie)
    print(json.dumps(res, indent=2))
