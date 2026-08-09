import json
import os
import argparse

def trace_epsilon_null(query_id, en_reg, pm_reg):
    try:
        with open(en_reg, 'r') as f: en_data = json.load(f)
        with open(pm_reg, 'r') as f: pm_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search EN by entry_id or target_law
    en_entries = [e for e in en_data.get("epsilon_null_entries", []) if e["entry_id"] == query_id or e["target_law"] == query_id]
    
    # Search PM by entry_id or target_object
    pm_entries = [e for e in pm_data.get("measure_entries", []) if e["entry_id"] == query_id or e["target_object"] == query_id]
    
    if not en_entries and not pm_entries:
        return {"error": f"Epsilon null or measure data for {query_id} not found."}

    trace = {
        "epsilon_null_trace": {
            "query_id": query_id,
            "en_associated_entries": [],
            "pm_associated_entries": []
        }
    }

    for entry in en_entries:
        trace["epsilon_null_trace"]["en_associated_entries"].append({
            "entry_id": entry["entry_id"],
            "target_law": entry["target_law"],
            "epsilon_class": entry["epsilon_class"],
            "null_rule": entry["null_rule"],
            "boundary_behavior": entry["boundary_behavior"],
            "stability_implication": entry["stability_implication"],
            "failure_risks": entry["failure_modes"]
        })

    for entry in pm_entries:
        trace["epsilon_null_trace"]["pm_associated_entries"].append({
            "entry_id": entry["entry_id"],
            "target_object": entry["target_object"],
            "measure_class": entry["measure_class"],
            "density_metric": entry["density_metric"],
            "normalization_rule": entry["normalization_rule"],
            "failure_risks": entry["failure_modes"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace epsilon_null and participation measure dependencies.")
    parser.add_argument("--query", required=True, help="Entry ID, Law ID, or Object ID (e.g., EN-001 or MPF-PV-001)")
    parser.add_argument("--en", default="registry/math/epsilon_null_registry.json")
    parser.add_argument("--pm", default="registry/math/participation_measure_registry.json")
    
    args = parser.parse_args()
    res = trace_epsilon_null(args.query, args.en, args.pm)
    print(json.dumps(res, indent=2))
