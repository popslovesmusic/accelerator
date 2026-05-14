import json
import os
import argparse

def trace_rc002_derivation_supported(query, supported_reg):
    try:
        with open(supported_reg, 'r') as f: s_data = json.load(f).get("rc002_derivation_supported", {})
    except Exception as e:
        return {"error": str(e)}

    trace_results = []
    if query == "RC-002":
        trace_results.append(s_data)
    else:
        for step in s_data.get("supported_steps", []):
            if query == step["step_id"]:
                trace_results.append(step)

    return {"rc002_derivation_supported_trace": { "query": query, "results": trace_results }}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-002 derivation supported status.")
    parser.add_argument("--query", required=True, help="Target (RC-002) or step ID to trace.")
    parser.add_argument("--supported", default="registry/math/rc002_derivation_supported_registry.json")
    
    args = parser.parse_args()
    res = trace_rc002_derivation_supported(args.query, args.supported)
    print(json.dumps(res, indent=2))
