import json
import os
import argparse

def trace_well_posedness(query, wp_reg, fm_reg):
    try:
        with open(wp_reg, 'r') as f: wp_data = json.load(f)
        with open(fm_reg, 'r') as f: fm_data = json.load(f)
    except Exception as e:
        return {"error": str(e)}

    trace = {
        "query": query,
        "matching_entries": [],
        "associated_failure_modes": [],
        "warnings": []
    }

    # Find entries
    for entry in wp_data.get("entries", []):
        if query.lower() in entry["target_symbol"].lower():
            trace["matching_entries"].append(entry)
            
            # Resolve failure modes
            for fm_id in entry.get("known_failure_modes", []):
                for fm in fm_data.get("failure_modes", []):
                    if fm["id"] == fm_id:
                        trace["associated_failure_modes"].append(fm)

    if not trace["matching_entries"]:
        trace["warnings"].append(f"No well-posedness entries found for query: {query}")

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace well-posedness assumptions.")
    parser.add_argument("--query", required=True, help="Operator or object symbol.")
    parser.add_argument("--wp", default="registry/math/well_posedness_registry.json")
    parser.add_argument("--fm", default="registry/math/failure_mode_registry.json")
    
    args = parser.parse_args()
    res = trace_well_posedness(args.query, args.wp, args.fm)
    print(json.dumps(res, indent=2))
