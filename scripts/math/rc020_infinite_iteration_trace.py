import json
import os
import argparse

def trace_rc020_infinite_iteration(query, strengthen_reg, failure_reg):
    try:
        with open(strengthen_reg, 'r') as f: s_data = json.load(f).get("rc020_infinite_iteration_strengthening", {})
        with open(failure_reg, 'r') as f: f_data = json.load(f).get("rc020_asymptotic_failure_modes", {})
    except Exception as e:
        return {"error": str(e)}

    failures = {fm["id"]: fm for fm in f_data.get("failure_modes", [])}
    
    trace_results = []
    if query == "RC-020" or query == "infinite_iteration":
        for entry in s_data.get("strengthening_entries", []):
            enriched = entry.copy()
            enriched["failure_mode_details"] = [failures.get(fm, {"error": "unknown"}) for fm in entry.get("failure_modes", [])]
            trace_results.append(enriched)

    return {"rc020_infinite_iteration_trace": {"query": query, "results": trace_results}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-020 infinite iteration stability.")
    parser.add_argument("--query", required=True, help="Target (RC-020) or focus to trace.")
    parser.add_argument("--strengthen", default="registry/math/rc020_infinite_iteration_strengthening_registry.json")
    parser.add_argument("--failures", default="registry/math/rc020_asymptotic_failure_modes.json")
    
    args = parser.parse_args()
    res = trace_rc020_infinite_iteration(args.query, args.strengthen, args.failures)
    print(json.dumps(res, indent=2))
