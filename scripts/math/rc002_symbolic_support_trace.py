import json
import os
import argparse

def trace_rc002_symbolic_support(query, elevation_reg):
    try:
        with open(elevation_reg, 'r') as f: e_data = json.load(f).get("rc002_symbolic_support_elevation", {})
    except Exception as e:
        return {"error": str(e)}

    trace_results = []
    if query == "RC-002":
        trace_results.append(e_data)
    else:
        for entry in e_data.get("elevation_entries", []):
            if query == entry["step_id"]:
                trace_results.append(entry)

    return {"rc002_symbolic_support_trace": { "query": query, "results": trace_results }}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-002 symbolic support elevation.")
    parser.add_argument("--query", required=True, help="Target (RC-002) or step ID to trace.")
    parser.add_argument("--elevation", default="registry/math/rc002_symbolic_support_elevation_registry.json")
    
    args = parser.parse_args()
    res = trace_rc002_symbolic_support(args.query, args.elevation)
    print(json.dumps(res, indent=2))
