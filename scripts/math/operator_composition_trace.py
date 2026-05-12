import json
import os
import argparse

def trace_operator_composition(query_id, comp_reg, comm_reg):
    try:
        with open(comp_reg, 'r') as f: comp_data = json.load(f)
        with open(comm_reg, 'r') as f: comm_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in compositions
    comp_entries = [e for e in comp_data.get("composition_entries", []) if query_id in e.get("operators", []) or query_id == e.get("entry_id")]
    
    # Search in commutations
    comm_entries = [e for e in comm_data.get("commutation_entries", []) if query_id in e.get("operator_pair", []) or query_id == e.get("entry_id")]
    
    if not comp_entries and not comm_entries:
        return {"error": f"Composition or commutation data for {query_id} not found."}

    trace = {
        "operator_composition_trace": {
            "query_id": query_id,
            "associated_compositions": [],
            "associated_commutations": []
        }
    }

    for entry in comp_entries:
        trace["operator_composition_trace"]["associated_compositions"].append({
            "entry_id": entry["entry_id"],
            "composition": entry["composition"],
            "composition_class": entry["composition_class"],
            "interpretation": entry["interpretation"],
            "expected_behavior": entry["expected_behavior"],
            "failure_risks": entry["failure_modes"]
        })

    for entry in comm_entries:
        trace["operator_composition_trace"]["associated_commutations"].append({
            "entry_id": entry["entry_id"],
            "operator_pair": entry["operator_pair"],
            "commutation_status": entry["commutation_status"],
            "reason": entry["reason"],
            "failure_risks": entry["failure_modes"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace operator composition dependencies.")
    parser.add_argument("--query", required=True, help="Operator ID or Entry ID (e.g., delta or OC-001)")
    parser.add_argument("--composition", default="registry/math/operator_composition_registry.json")
    parser.add_argument("--commutation", default="registry/math/operator_commutation_registry.json")
    
    args = parser.parse_args()
    res = trace_operator_composition(args.query, args.composition, args.commutation)
    print(json.dumps(res, indent=2))
