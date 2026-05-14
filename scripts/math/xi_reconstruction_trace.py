import json
import os
import argparse

def trace_xi_reconstruction(query):
    trace = {
        "xi_reconstruction_trace": {
            "query": query,
            "bounds": [],
            "preimage_class": None,
            "failure_modes": [],
            "hypothesis": None
        }
    }

    bounds_reg = "registry/math/xi_reconstruction_bounds_registry.json"
    preimage_reg = "registry/math/xi_preimage_classification_registry.json"
    fm_reg = "registry/math/xi_reconstruction_failure_modes.json"
    hyp_reg = "registry/math/xi_reconstruction_hypothesis_registry.json"

    try:
        if os.path.exists(bounds_reg):
            with open(bounds_reg, 'r') as f:
                data = json.load(f).get("xi_reconstruction_bounds", {})
                for mapping in data.get("operator_mapping", []):
                    if mapping["operator"] == query or query == "Xi":
                        trace["xi_reconstruction_trace"]["bounds"].append(mapping)
        
        if os.path.exists(preimage_reg):
             with open(preimage_reg, 'r') as f:
                classes = json.load(f).get("classifications", [])
                trace["xi_reconstruction_trace"]["preimage_class"] = next((c for c in classes if query in c["target"] or query in c["reconstruction_class"]), None)

        if os.path.exists(fm_reg):
             with open(fm_reg, 'r') as f:
                fms = json.load(f).get("failure_modes", [])
                for fm in fms:
                    if query in fm["name"] or query == "Xi":
                        trace["xi_reconstruction_trace"]["failure_modes"].append(fm)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                hyps = json.load(f).get("hypotheses", [])
                trace["xi_reconstruction_trace"]["hypothesis"] = next((h for h in hyps if query in h["target_theorem"] or query in h["statement"]), None)

    except Exception as e:
        trace["xi_reconstruction_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace Xi reconstruction bounds.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_xi_reconstruction(args.query)
    print(json.dumps(res, indent=2))
