import json
import os
import argparse

def trace_boundary(query):
    trace = {
        "admissibility_boundary_trace": {
            "query": query,
            "main_class": None,
            "detailed_geometry": None,
            "hypothesis": None
        }
    }

    main_reg = "registry/math/admissibility_boundary_geometry_registry.json"
    en_reg = "registry/math/epsilon_null_boundary_geometry_registry.json"
    o_reg = "registry/math/orientation_admissibility_window_registry.json"
    r_reg = "registry/math/recursive_stability_boundary_registry.json"
    t_reg = "registry/math/transport_threshold_boundary_registry.json"
    b_reg = "registry/math/branch_retention_boundary_registry.json"
    hyp_reg = "registry/math/admissibility_boundary_hypothesis_registry.json"

    if query == "orientation_operator_minus_i":
        query = "-(i)"

    try:
        if os.path.exists(main_reg):
            with open(main_reg, 'r') as f:
                classes = json.load(f).get("admissibility_boundary_geometry", {}).get("boundary_classes", [])
                trace["admissibility_boundary_trace"]["main_class"] = next((c for c in classes if query in c["name"] or query in c["id"] or (c.get("operator") and query in c["operator"])), None)

        # Search detailed registries
        detail_regs = [en_reg, o_reg, r_reg, t_reg, b_reg]
        for dr in detail_regs:
            if os.path.exists(dr):
                with open(dr, 'r') as f:
                    data = json.load(f)
                    # Handle different root keys
                    key = next(iter(data.keys()))
                    items = data[key]
                    if isinstance(items, list):
                         match = next((i for i in items if query in str(i)), None)
                    elif isinstance(items, dict):
                         # Handle cases like mappings in epsilon_null
                         sub_match = None
                         for k, v in items.items():
                             if query in str(v):
                                 sub_match = v
                                 break
                         match = sub_match
                    else:
                         match = None
                    
                    if match:
                        trace["admissibility_boundary_trace"]["detailed_geometry"] = match
                        break

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                hyps = json.load(f).get("hypotheses", [])
                for h in hyps:
                    target = h.get("target_theorem") or h.get("target_reduction_chain")
                    if target and (query in target or query in h.get("statement", "")):
                        trace["admissibility_boundary_trace"]["hypothesis"] = h
                        break

    except Exception as e:
        trace["admissibility_boundary_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace admissibility boundary geometry.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_boundary(args.query)
    print(json.dumps(res, indent=2))
