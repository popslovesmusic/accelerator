import json
import os
import argparse

def trace_reconstruction(query, rec_reg, rfm_reg):
    try:
        with open(rec_reg, 'r') as f: rec_data = json.load(f)
        with open(rfm_reg, 'r') as f: rfm_data = json.load(f)
    except Exception as e:
        return {"error": str(e)}

    trace = {
        "query": query,
        "matching_entries": [],
        "associated_failure_modes": [],
        "information_loss": [],
        "warnings": []
    }

    # Find entries
    for entry in rec_data.get("entries", []):
        if query.lower() in entry["target_symbol"].lower():
            trace["matching_entries"].append(entry)
            trace["information_loss"].extend(entry.get("information_loss_notes", []))
            
            # Resolve failure modes
            for fm_id in entry.get("known_failure_modes", []):
                for fm in rfm_data.get("failure_modes", []):
                    if fm["id"] == fm_id:
                        trace["associated_failure_modes"].append(fm)

    if not trace["matching_entries"]:
        trace["warnings"].append(f"No reconstruction entries found for query: {query}")

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace reconstruction assumptions.")
    parser.add_argument("--query", required=True, help="Symbol to trace (e.g., Pi_A, observable_projection).")
    parser.add_argument("--rec", default="registry/math/reconstruction_registry.json")
    parser.add_argument("--rfm", default="registry/math/reconstruction_failure_registry.json")
    
    args = parser.parse_args()
    res = trace_reconstruction(args.query, args.rec, args.rfm)
    print(json.dumps(res, indent=2))
