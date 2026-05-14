import json
import os
import argparse

def trace_topology(query):
    trace = {
        "admissibility_topology_trace": {
            "query": query,
            "main_class": None,
            "basin_transition": None,
            "orientation_transition": None,
            "bifurcation": None,
            "branch_transition": None,
            "stability_transition": None,
            "hypothesis": None
        }
    }

    main_reg = "registry/math/admissibility_topology_transition_registry.json"
    basin_reg = "registry/math/admissibility_basin_transition_registry.json"
    o_reg = "registry/math/orientation_window_transition_registry.json"
    en_reg = "registry/math/epsilon_null_bifurcation_registry.json"
    br_reg = "registry/math/branch_retention_transition_registry.json"
    rs_reg = "registry/math/recursive_stability_transition_registry.json"
    hyp_reg = "registry/math/admissibility_transition_hypothesis_registry.json"

    if query == "orientation_operator_minus_i":
        query = "-(i)"

    try:
        if os.path.exists(main_reg):
            with open(main_reg, 'r') as f:
                classes = json.load(f).get("admissibility_topology_transition", {}).get("transition_classes", [])
                trace["admissibility_topology_trace"]["main_class"] = next((c for c in classes if query in c["name"] or query in c["id"]), None)

        if os.path.exists(basin_reg):
             with open(basin_reg, 'r') as f:
                trans = json.load(f).get("admissibility_basin_transition", {}).get("transitions", [])
                trace["admissibility_topology_trace"]["basin_transition"] = next((t for t in trans if any(query in str(v) for v in t.values())), None)

        if os.path.exists(o_reg):
             with open(o_reg, 'r') as f:
                trans = json.load(f).get("orientation_window_transition", {}).get("transitions", [])
                trace["admissibility_topology_trace"]["orientation_transition"] = next((t for t in trans if any(query in str(v) for v in t.values())), None)

        if os.path.exists(en_reg):
             with open(en_reg, 'r') as f:
                types = json.load(f).get("epsilon_null_bifurcation", {}).get("bifurcation_types", [])
                trace["admissibility_topology_trace"]["bifurcation"] = next((t for t in types if any(query in str(v) for v in t.values())), None)

        if os.path.exists(br_reg):
             with open(br_reg, 'r') as f:
                trans = json.load(f).get("branch_retention_transition", {}).get("transitions", [])
                trace["admissibility_topology_trace"]["branch_transition"] = next((t for t in trans if any(query in str(v) for v in t.values())), None)

        if os.path.exists(rs_reg):
             with open(rs_reg, 'r') as f:
                trans = json.load(f).get("recursive_stability_transition", {}).get("transitions", [])
                trace["admissibility_topology_trace"]["stability_transition"] = next((t for t in trans if any(query in str(v) for v in t.values())), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                hyps = json.load(f).get("hypotheses", [])
                for h in hyps:
                    target = h.get("target_theorem") or h.get("target_reduction_chain")
                    if target and (query in target or query in h.get("statement", "")):
                        trace["admissibility_topology_trace"]["hypothesis"] = h
                        break

    except Exception as e:
        trace["admissibility_topology_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace admissibility topology transitions.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_topology(args.query)
    print(json.dumps(res, indent=2))
