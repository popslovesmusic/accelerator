import json
import os
import argparse

def trace_equivalence_property(query_id, prop_reg, pres_reg):
    try:
        with open(prop_reg, 'r') as f: prop_data = json.load(f)
        with open(pres_reg, 'r') as f: pres_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search properties by entry_id, relation, or theorem
    prop_entries = [e for e in prop_data.get("property_entries", []) if query_id == e["entry_id"] or query_id == e["relation"] or query_id in e["supported_theorems"]]
    
    # Search preservation by operator or relation
    pres_entries = [e for e in pres_data.get("preservation_entries", []) if query_id == e["operator"] or query_id == e["relation"]]
    
    if not prop_entries and not pres_entries:
        return {"error": f"Equivalence property data for {query_id} not found."}

    trace = {
        "equivalence_property_trace": {
            "query_id": query_id,
            "associated_properties": [],
            "associated_preservations": []
        }
    }

    for entry in prop_entries:
        trace["equivalence_property_trace"]["associated_properties"].append({
            "entry_id": entry["entry_id"],
            "relation": entry["relation"],
            "reflexive": entry["reflexive_status"],
            "symmetric": entry["symmetric_status"],
            "transitive": entry["transitive_status"],
            "supported_theorems": entry["supported_theorems"]
        })

    for entry in pres_entries:
        trace["equivalence_property_trace"]["associated_preservations"].append({
            "entry_id": entry["entry_id"],
            "operator": entry["operator"],
            "relation": entry["relation"],
            "status": entry["preservation_status"],
            "condition": entry["condition"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace equivalence property dependencies.")
    parser.add_argument("--query", required=True, help="Theorem ID, Operator ID, or Relation Name (e.g., MT-001 or Pi_A)")
    parser.add_argument("--prop", default="registry/math/equivalence_property_registry.json")
    parser.add_argument("--pres", default="registry/math/equivalence_preservation_registry.json")
    
    args = parser.parse_args()
    res = trace_equivalence_property(args.query, args.prop, args.pres)
    print(json.dumps(res, indent=2))
