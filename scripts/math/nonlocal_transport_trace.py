import json
import os
import argparse

def trace_nonlocal_transport(query_id, transport_reg):
    try:
        with open(transport_reg, 'r') as f: transport_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id, target_operator, or target_law
    entries = [e for e in transport_data.get("transport_entries", []) if e["entry_id"] == query_id or e["target_operator"] == query_id or e["target_law"] == query_id]
    
    if not entries:
        return {"error": f"Non-local transport data for {query_id} not found in {transport_reg}"}

    trace = {
        "nonlocal_transport_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        entry_trace = {
            "entry_id": entry["entry_id"],
            "target_operator": entry["target_operator"],
            "target_law": entry["target_law"],
            "transport_class": entry["transport_class"],
            "closure_class": entry["closure_class"],
            "dependencies": {
                "orientation": entry["orientation_conditions"],
                "residue": entry["residue_conditions"],
                "branch": entry["branch_conditions"],
                "admissibility": entry["admissibility_conditions"]
            },
            "implications": {
                "reconstruction": entry["reconstruction_implication"],
                "stability": entry["stability_implication"],
                "convergence": entry["convergence_implication"]
            },
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        }
        trace["nonlocal_transport_trace"]["associated_entries"].append(entry_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace non-local transport dependencies.")
    parser.add_argument("--query", required=True, help="Entry ID, Operator ID, or Law ID (e.g., NTC-001 or NavT)")
    parser.add_argument("--transport", default="registry/math/nonlocal_transport_registry.json")
    
    args = parser.parse_args()
    res = trace_nonlocal_transport(args.query, args.transport)
    print(json.dumps(res, indent=2))
