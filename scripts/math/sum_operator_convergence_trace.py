import json
import os
import argparse

def trace_sum_operator_convergence(query, convergence_reg, failure_reg, bound_reg):
    try:
        with open(convergence_reg, 'r') as f: conv_data = json.load(f).get("sum_operator_convergence_registry", {})
        with open(failure_reg, 'r') as f: failure_data = json.load(f).get("sum_operator_failure_modes", {})
        with open(bound_reg, 'r') as f: bound_data = json.load(f).get("nonlocal_sum_bound_registry", {})
    except Exception as e:
        return {"error": str(e)}

    failures = {fm["id"]: fm for fm in failure_data.get("failure_modes", [])}
    bounds = {b["bound_id"]: b for b in bound_data.get("bounds", [])}
    
    trace_results = []
    for entry in conv_data.get("convergence_entries", []):
        if query in [entry["entry_id"], entry["target"], "GAP-001" if entry.get("status") == "gap_open" else "", "RC-001" if "RC-001" in entry["target"] else ""]:
            # Enrich entry with failure mode and bound details
            enriched_entry = entry.copy()
            enriched_entry["condition_details"] = [bounds.get(c, {"error": "unknown"}) for c in entry.get("conditions", [])]
            enriched_entry["failure_mode_details"] = [failures.get(fm, {"error": "unknown"}) for fm in entry.get("failure_modes", [])]
            trace_results.append(enriched_entry)

    return {"sum_operator_convergence_trace": {"query": query, "results": trace_results}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace sum operator convergence.")
    parser.add_argument("--query", required=True, help="Target, entry_id, or gap_id to trace.")
    parser.add_argument("--convergence", default="registry/math/sum_operator_convergence_registry.json")
    parser.add_argument("--failures", default="registry/math/sum_operator_failure_modes.json")
    parser.add_argument("--bounds", default="registry/math/nonlocal_sum_bound_registry.json")
    
    args = parser.parse_args()
    res = trace_sum_operator_convergence(args.query, args.convergence, args.failures, args.bounds)
    print(json.dumps(res, indent=2))
