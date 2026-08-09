import json
import os
import argparse

def trace_recursive_loss(query):
    trace = {
        "recursive_loss_trace": {
            "query": query,
            "accumulation_dynamic": None,
            "reconstruction_horizon": None,
            "saturation_basin": None,
            "hypothesis": None
        }
    }

    acc_reg = "registry/math/recursive_loss_accumulation_registry.json"
    amb_reg = "registry/math/recursive_reconstruction_ambiguity_registry.json"
    basin_reg = "registry/math/loss_saturation_basin_registry.json"
    hyp_reg = "registry/math/recursive_loss_hypothesis_registry.json"

    try:
        if os.path.exists(acc_reg):
            with open(acc_reg, 'r') as f:
                mappings = json.load(f).get("recursive_loss_accumulation", {}).get("operator_dynamics_mapping", [])
                trace["recursive_loss_trace"]["accumulation_dynamic"] = next((m for m in mappings if query in m["operator"]), None)

        if os.path.exists(amb_reg):
             with open(amb_reg, 'r') as f:
                horizons = json.load(f).get("recursive_reconstruction_ambiguity", {}).get("operator_horizons", [])
                trace["recursive_loss_trace"]["reconstruction_horizon"] = next((h for h in horizons if query in h["operator"]), None)

        if os.path.exists(basin_reg):
             with open(basin_reg, 'r') as f:
                basins = json.load(f).get("loss_saturation_basin", {}).get("basins", [])
                trace["recursive_loss_trace"]["saturation_basin"] = next((b for b in basins if query in b["target"]), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                hyps = json.load(f).get("recursive_loss_hypothesis", {}).get("hypotheses", [])
                for h in hyps:
                    target = h.get("target_theorem") or h.get("target_reduction_chain")
                    if target and (query in target or query in h.get("statement", "")):
                        trace["recursive_loss_trace"]["hypothesis"] = h
                        break

    except Exception as e:
        trace["recursive_loss_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace recursive information loss.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_recursive_loss(args.query)
    print(json.dumps(res, indent=2))
