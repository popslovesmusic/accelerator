import json
import os
import argparse

def trace_reduction_chain(query, rc_reg, prim_reg):
    try:
        with open(rc_reg, 'r') as f: rc_data = json.load(f)
        with open(prim_reg, 'r') as f: prim_data = json.load(f)
    except Exception as e:
        return {"error": str(e)}

    trace = {
        "query": query,
        "matching_chains": [],
        "primitive_dependencies": [],
        "derivation_paths": [],
        "warnings": []
    }

    # Find chains
    for entry in rc_data.get("entries", []):
        if query.lower() in entry["target_expression"].lower() or query.lower() in entry["entry_id"].lower():
            trace["matching_chains"].append(entry)
            
            # Map primitives
            for p_id in entry.get("primitive_dependencies", []):
                for p in prim_data.get("primitives", []):
                    if p["id"] == p_id:
                        trace["primitive_dependencies"].append(p)

    if not trace["matching_chains"]:
        trace["warnings"].append(f"No reduction chains found for query: {query}")

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace formal reduction chains.")
    parser.add_argument("--query", required=True, help="Expression or operator symbol.")
    parser.add_argument("--rc", default="registry/math/reduction_chain_registry.json")
    parser.add_argument("--prims", default="registry/math/primitive_dependency_registry.json")
    
    args = parser.parse_args()
    res = trace_reduction_chain(args.query, args.rc, args.prims)
    print(json.dumps(res, indent=2))
