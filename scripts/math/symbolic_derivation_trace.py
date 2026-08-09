import json
import os
import argparse

def trace_symbolic_derivation(query_id, closure_reg, evidence_reg):
    try:
        with open(closure_reg, 'r') as f: closure_data = json.load(f)
        with open(evidence_reg, 'r') as f: evidence_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id or target_chain
    entries = [e for e in closure_data.get("closure_entries", []) if query_id == e.get("entry_id") or query_id == e.get("target_chain")]
    
    if not entries:
        return {"error": f"Derivation closure data for {query_id} not found."}

    trace = {
        "symbolic_derivation_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        test_trace = {
            "entry_id": entry["entry_id"],
            "target_chain": entry["target_chain"],
            "closure_status": entry["closure_status"],
            "evidence_ladder_target": entry["evidence_ladder_target"],
            "step_resolutions": entry["step_resolutions"],
            "explicit_evidence": []
        }
        
        # Link to explicit evidence
        for ev in evidence_data.get("evidence_entries", []):
            if ev["chain_id"] == entry["target_chain"]:
                test_trace["explicit_evidence"].append(ev)
                
        trace["symbolic_derivation_trace"]["associated_entries"].append(test_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace symbolic derivation closure status.")
    parser.add_argument("--query", required=True, help="Chain ID or Entry ID (e.g. RC-001 or DC-RC001)")
    parser.add_argument("--closure", default="registry/math/symbolic_derivation_closure_registry.json")
    parser.add_argument("--evidence", default="registry/math/derivation_step_evidence_registry.json")
    
    args = parser.parse_args()
    res = trace_symbolic_derivation(args.query, args.closure, args.evidence)
    print(json.dumps(res, indent=2))
