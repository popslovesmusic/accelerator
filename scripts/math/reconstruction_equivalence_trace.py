import json
import os
import argparse

def trace_equivalence(query):
    trace = {
        "reconstruction_equivalence_trace": {
            "query": query,
            "equivalence_class": None,
            "preimage_family": None,
            "indistinguishability_class": None,
            "equivalence_basin": None,
            "hypothesis": None
        }
    }

    geo_reg = "registry/math/reconstruction_equivalence_geometry_registry.json"
    fam_reg = "registry/math/reconstruction_preimage_family_registry.json"
    ind_reg = "registry/math/observable_indistinguishability_class_registry.json"
    basin_reg = "registry/math/recursive_equivalence_basin_registry.json"
    hyp_reg = "registry/math/reconstruction_equivalence_hypothesis_registry.json"

    try:
        if os.path.exists(geo_reg):
            with open(geo_reg, 'r') as f:
                classes = json.load(f).get("reconstruction_equivalence_geometry", {}).get("equivalence_classes", [])
                trace["reconstruction_equivalence_trace"]["equivalence_class"] = next((c for c in classes if query in c["name"] or query in c["source_operator"]), None)

        if os.path.exists(fam_reg):
             with open(fam_reg, 'r') as f:
                mappings = json.load(f).get("reconstruction_preimage_family", {}).get("operator_family_mapping", [])
                trace["reconstruction_equivalence_trace"]["preimage_family"] = next((m for m in mappings if query in m["operator"]), None)

        if os.path.exists(ind_reg):
             with open(ind_reg, 'r') as f:
                classes = json.load(f).get("observable_indistinguishability_class", {}).get("classes", [])
                trace["reconstruction_equivalence_trace"]["indistinguishability_class"] = next((c for c in classes if query in c["name"]), None)

        if os.path.exists(basin_reg):
             with open(basin_reg, 'r') as f:
                basins = json.load(f).get("recursive_equivalence_basin", {}).get("basin_candidates", [])
                trace["reconstruction_equivalence_trace"]["equivalence_basin"] = next((b for b in basins if query in b["target"] or query in b["name"]), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                hyps = json.load(f).get("reconstruction_equivalence_hypothesis", {}).get("hypotheses", [])
                for h in hyps:
                    target = h.get("target_theorem") or h.get("target_reduction_chain")
                    if target and (query in target or query in h.get("statement", "")):
                        trace["reconstruction_equivalence_trace"]["hypothesis"] = h
                        break

    except Exception as e:
        trace["reconstruction_equivalence_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace reconstruction equivalence geometry.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_equivalence(args.query)
    print(json.dumps(res, indent=2))
