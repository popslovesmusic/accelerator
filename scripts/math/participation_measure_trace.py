import json
import os
import argparse

def trace_participation_measure(query_id, refine_reg, norm_reg):
    try:
        with open(refine_reg, 'r') as f: refine_data = json.load(f)
        with open(norm_reg, 'r') as f: norm_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by target or entry ID
    entries = [e for e in refine_data.get("refinement_entries", []) if query_id == e.get("target") or query_id == e.get("primary_class")]
    
    # Search normalization rules
    rules = [r for r in norm_data.get("normalization_rules", []) if query_id == r.get("applicability") or query_id == r.get("rule_id")]

    if not entries and not rules:
        return {"error": f"Participation measure data for {query_id} not found."}

    trace = {
        "participation_measure_trace": {
            "query_id": query_id,
            "associated_refinements": [],
            "associated_normalization_rules": []
        }
    }

    for entry in entries:
        trace["participation_measure_trace"]["associated_refinements"].append({
            "target": entry["target"],
            "status": entry["status"],
            "primary_class": entry["primary_class"],
            "constraints": entry["constraints"]
        })

    for rule in rules:
        trace["participation_measure_trace"]["associated_normalization_rules"].append({
            "rule_id": rule["rule_id"],
            "name": rule["name"],
            "expression": rule["expression"],
            "applicability": rule["applicability"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace participation measure dependencies.")
    parser.add_argument("--query", required=True, help="Target ID or Class ID (e.g., participation_space or finite_cardinality)")
    parser.add_argument("--refine", default="registry/math/participation_measure_refinement_registry.json")
    parser.add_argument("--norm", default="registry/math/measure_normalization_registry.json")
    
    args = parser.parse_args()
    res = trace_participation_measure(args.query, args.refine, args.norm)
    print(json.dumps(res, indent=2))
