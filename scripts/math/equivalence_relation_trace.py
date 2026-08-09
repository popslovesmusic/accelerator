import json
import os
import argparse

def trace_equivalence_relation(query_id, equiv_reg):
    try:
        with open(equiv_reg, 'r') as f: equiv_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in entries
    entries = [e for e in equiv_data.get("equivalence_relation_entries", []) if query_id in e.get("supports_theorems", []) or query_id in e.get("supports_operators", []) or query_id == e.get("entry_id") or query_id == e.get("relation_class")]
    
    if not entries:
        return {"error": f"Equivalence relation data for {query_id} not found."}

    trace = {
        "equivalence_relation_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        trace["equivalence_relation_trace"]["associated_entries"].append({
            "entry_id": entry["entry_id"],
            "relation_class": entry["relation_class"],
            "supports_theorems": entry.get("supports_theorems", []),
            "supports_operators": entry.get("supports_operators", []),
            "reflexive": entry["reflexive_status"],
            "symmetric": entry["symmetric_status"],
            "transitive": entry["transitive_status"],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace equivalence relation dependencies.")
    parser.add_argument("--query", required=True, help="Theorem ID, Operator ID, or Entry ID (e.g., MT-001 or EQ-001)")
    parser.add_argument("--equivalence", default="registry/math/equivalence_relation_registry.json")
    
    args = parser.parse_args()
    res = trace_equivalence_relation(args.query, args.equivalence)
    print(json.dumps(res, indent=2))
