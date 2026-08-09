import json
import os
import argparse

def trace_residue_behavior(query_id, behavior_reg):
    try:
        with open(behavior_reg, 'r') as f: behavior_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id, target_operator, or target_law
    entries = [e for e in behavior_data.get("behavior_entries", []) if e["entry_id"] == query_id or e["target_operator"] == query_id or e["target_law"] == query_id]
    
    if not entries:
        return {"error": f"Residue behavior data for {query_id} not found in {behavior_reg}"}

    trace = {
        "residue_behavior_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        entry_trace = {
            "entry_id": entry["entry_id"],
            "target_operator": entry["target_operator"],
            "target_law": entry["target_law"],
            "behavior_class": entry["behavior_class"],
            "balance_expression": entry["balance_expression"],
            "implications": {
                "stability": entry["stability_implication"],
                "convergence": entry["convergence_implication"]
            },
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        }
        trace["residue_behavior_trace"]["associated_entries"].append(entry_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace residue behavior dependencies.")
    parser.add_argument("--query", required=True, help="Entry ID, Operator ID, or Law ID (e.g., RB-001 or residue_update)")
    parser.add_argument("--behavior", default="registry/math/residue_transport_behavior_registry.json")
    
    args = parser.parse_args()
    res = trace_residue_behavior(args.query, args.behavior)
    print(json.dumps(res, indent=2))
