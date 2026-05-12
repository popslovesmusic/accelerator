import json
import os
import argparse

def trace_selection_reconstruction(query_id, reconstruction_reg, inverse_reg):
    try:
        with open(reconstruction_reg, 'r') as f: rec_data = json.load(f)
        with open(inverse_reg, 'r') as f: inv_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id or target
    entries = [e for e in rec_data.get("reconstruction_entries", []) if query_id == e.get("entry_id") or query_id == e.get("target")]
    
    if not entries:
        return {"error": f"Selection reconstruction data for {query_id} not found."}

    trace = {
        "selection_reconstruction_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        rec_class = next((c for c in rec_data["reconstruction_classes"] if c["class"] == entry["reconstruction_class"]), {"meaning": "unknown"})
        
        trace["selection_reconstruction_trace"]["associated_entries"].append({
            "entry_id": entry["entry_id"],
            "target": entry["target"],
            "reconstruction_class": entry["reconstruction_class"],
            "class_meaning": rec_class["meaning"],
            "constraints": entry["constraints"],
            "provisional_status": entry["provisional_status"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace selection reconstruction dependencies.")
    parser.add_argument("--query", required=True, help="Target ID or Entry ID (e.g., delta or SR-001)")
    parser.add_argument("--reconstruction", default="registry/math/selection_reconstruction_registry.json")
    parser.add_argument("--inverse", default="registry/math/inverse_selection_condition_registry.json")
    
    args = parser.parse_args()
    res = trace_selection_reconstruction(args.query, args.reconstruction, args.inverse)
    print(json.dumps(res, indent=2))
