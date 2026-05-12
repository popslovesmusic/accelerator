import json
import os
import argparse

def trace_reconstruction_uniqueness(query_id, uniqueness_reg):
    try:
        with open(uniqueness_reg, 'r') as f: uni_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id, target_operator, or target_law
    entries = [e for e in uni_data.get("uniqueness_entries", []) if e["entry_id"] == query_id or e["target_operator"] == query_id or e["target_law"] == query_id]
    
    if not entries:
        return {"error": f"Reconstruction uniqueness data for {query_id} not found in {uniqueness_reg}"}

    trace = {
        "reconstruction_uniqueness_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        entry_trace = {
            "entry_id": entry["entry_id"],
            "target_operator": entry["target_operator"],
            "target_law": entry["target_law"],
            "uniqueness_class": entry["uniqueness_class"],
            "constraint_classes": entry["constraint_classes"],
            "ambiguity_behavior": entry["ambiguity_behavior"],
            "dependencies": {
                "orientation": entry["orientation_dependency"],
                "residue": entry["residue_dependency"],
                "transport": entry["transport_dependency"],
                "branch": entry["branch_dependency"]
            },
            "implications": {
                "stability": entry["stability_implication"]
            },
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        }
        trace["reconstruction_uniqueness_trace"]["associated_entries"].append(entry_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace reconstruction uniqueness dependencies.")
    parser.add_argument("--query", required=True, help="Entry ID, Operator ID, or Law ID (e.g., RUC-001 or delta)")
    parser.add_argument("--uniqueness", default="registry/math/reconstruction_uniqueness_registry.json")
    
    args = parser.parse_args()
    res = trace_reconstruction_uniqueness(args.query, args.uniqueness)
    print(json.dumps(res, indent=2))
