import json
import os
import argparse

def trace_residue_conservation(query_id, rcon_reg, inv_reg):
    try:
        with open(rcon_reg, 'r') as f: rcon_data = json.load(f)
        with open(inv_reg, 'r') as f: inv_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in balance entries
    entries = [e for e in rcon_data.get("balance_entries", []) if query_id == e.get("entry_id") or query_id == e.get("target") or query_id == e.get("balance_class")]
    
    # Search in invariants
    invariants = [i for i in inv_data.get("candidate_invariants", []) if query_id == i.get("invariant_id") or query_id in i.get("name", "")]

    if not entries and not invariants:
        return {"error": f"Residue conservation data for {query_id} not found."}

    trace = {
        "residue_conservation_trace": {
            "query_id": query_id,
            "associated_entries": [],
            "associated_invariants": []
        }
    }

    for entry in entries:
        trace["residue_conservation_trace"]["associated_entries"].append({
            "entry_id": entry["entry_id"],
            "target": entry["target"],
            "balance_class": entry["balance_class"],
            "stability_implication": entry["stability_implication"],
            "conditions": entry["conditions"],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        })

    for inv in invariants:
        trace["residue_conservation_trace"]["associated_invariants"].append({
            "invariant_id": inv["invariant_id"],
            "name": inv["name"],
            "statement": inv["statement"],
            "status": inv["status"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace residue conservation dependencies.")
    parser.add_argument("--query", required=True, help="Target ID or Entry ID (e.g., residue_update or RCON-001)")
    parser.add_argument("--rcon", default="registry/math/residue_conservation_registry.json")
    parser.add_argument("--inv", default="registry/math/residue_transport_invariant_registry.json")
    
    args = parser.parse_args()
    res = trace_residue_conservation(args.query, args.rcon, args.inv)
    print(json.dumps(res, indent=2))
