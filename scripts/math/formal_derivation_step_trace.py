import json
import os
import argparse

def trace_formal_derivation_step(query, elevation_reg):
    try:
        with open(elevation_reg, 'r') as f: elevation_data = json.load(f)
    except Exception as e:
        return {"error": str(e)}

    trace_results = []
    for entry in elevation_data.get("elevation_entries", []):
        if query == entry["target_id"] or any(query == step["step_id"] for step in entry.get("steps", [])):
            trace_results.append(entry)

    return {"formal_derivation_step_trace": {"query": query, "results": trace_results}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace formal derivation step elevation.")
    parser.add_argument("--query", required=True, help="Target ID or step ID to trace.")
    parser.add_argument("--elevation", default="registry/math/formal_derivation_step_elevation_registry.json")
    
    args = parser.parse_args()
    res = trace_formal_derivation_step(args.query, args.elevation)
    print(json.dumps(res, indent=2))
