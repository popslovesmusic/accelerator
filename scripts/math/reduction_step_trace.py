import json
import os
import argparse

def trace_reduction_step(query_id, formal_reg, chain_reg):
    try:
        with open(formal_reg, 'r') as f: formal_data = json.load(f)
        with open(chain_reg, 'r') as f: chain_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in formalization entries
    entries = [e for e in formal_data.get("formalization_entries", []) if query_id == e.get("chain_id") or query_id == e.get("step_id")]
    
    if not entries:
        return {"error": f"Reduction step formalization data for {query_id} not found."}

    trace = {
        "reduction_step_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        trace["reduction_step_trace"]["associated_entries"].append({
            "chain_id": entry["chain_id"],
            "step_id": entry["step_id"],
            "status": entry["status"],
            "evidence_links": entry["evidence_links"],
            "formalization_notes": entry["formalization_notes"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace reduction step formalization status.")
    parser.add_argument("--query", required=True, help="Chain ID or Step ID (e.g., RC-001 or STEP-01)")
    parser.add_argument("--formal", default="registry/math/reduction_step_formalization_registry.json")
    parser.add_argument("--chains", default="registry/math/reduction_chain_registry.json")
    
    args = parser.parse_args()
    res = trace_reduction_step(args.query, args.formal, args.chains)
    print(json.dumps(res, indent=2))
