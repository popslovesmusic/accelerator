import json
import os
import argparse

def trace_transition_flux(query_id, convergence_reg):
    try:
        with open(convergence_reg, 'r') as f: conv_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id or target_law
    entries = [e for e in conv_data.get("convergence_entries", []) if e["entry_id"] == query_id or e["target_law"] == query_id]
    
    if not entries:
        return {"error": f"Convergence data for {query_id} not found in {convergence_reg}"}

    trace = {
        "transition_flux_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        entry_trace = {
            "entry_id": entry["entry_id"],
            "target_law": entry["target_law"],
            "convergence_class": entry["convergence_class"],
            "boundedness_statement": entry["boundedness_statement"],
            "dependencies": {
                "domain": entry["domain_conditions"],
                "csi": entry["csi_conditions"],
                "admissibility": entry["admissibility_conditions"],
                "residue": entry["residue_conditions"],
                "selection": entry["selection_rule_dependencies"]
            },
            "failure_modes": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        }
        trace["transition_flux_trace"]["associated_entries"].append(entry_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace transition_flux convergence dependencies.")
    parser.add_argument("--query", required=True, help="Entry ID or Law ID (e.g., TFC-001 or MPF-CV-001)")
    parser.add_argument("--convergence", default="registry/math/transition_flux_convergence_registry.json")
    
    args = parser.parse_args()
    res = trace_transition_flux(args.query, args.convergence)
    print(json.dumps(res, indent=2))
