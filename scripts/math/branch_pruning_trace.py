import json
import os
import argparse

def trace_branch_pruning(query_id, pruning_reg):
    try:
        with open(pruning_reg, 'r') as f: pruning_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id, target_operator, or target_law
    entries = [e for e in pruning_data.get("pruning_entries", []) if e["entry_id"] == query_id or e["target_operator"] == query_id or e["target_law"] == query_id]
    
    if not entries:
        return {"error": f"Branch pruning data for {query_id} not found in {pruning_reg}"}

    trace = {
        "branch_pruning_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        entry_trace = {
            "entry_id": entry["entry_id"],
            "target_operator": entry["target_operator"],
            "target_law": entry["target_law"],
            "pruning_class": entry["pruning_class"],
            "branch_bound": entry["branch_bound"],
            "dependencies": {
                "selection": entry["selection_dependency"],
                "orientation": entry["orientation_dependency"],
                "residue": entry["residue_dependency"],
                "admissibility": entry["admissibility_dependency"]
            },
            "implications": {
                "stability": entry["stability_implication"],
                "convergence": entry["convergence_implication"]
            },
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        }
        trace["branch_pruning_trace"]["associated_entries"].append(entry_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace branch pruning dependencies.")
    parser.add_argument("--query", required=True, help="Entry ID, Operator ID, or Law ID (e.g., BP-001 or MPF-CV-001)")
    parser.add_argument("--pruning", default="registry/math/branch_pruning_registry.json")
    
    args = parser.parse_args()
    res = trace_branch_pruning(args.query, args.pruning)
    print(json.dumps(res, indent=2))
