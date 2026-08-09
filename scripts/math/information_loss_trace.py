import json
import os
import argparse

def trace_information_loss(query):
    trace = {
        "information_loss_trace": {
            "query": query,
            "pathway": None,
            "classification": None,
            "ambiguity_geometry": None,
            "recursive_behavior": None,
            "hypothesis": None
        }
    }

    geo_reg = "registry/math/information_loss_geometry_registry.json"
    class_reg = "registry/math/operator_loss_classification_registry.json"
    amb_reg = "registry/math/reconstruction_ambiguity_geometry_registry.json"
    rec_reg = "registry/math/loss_accumulation_under_recursion_registry.json"
    hyp_reg = "registry/math/information_loss_theorem_hypothesis_registry.json"

    try:
        if os.path.exists(geo_reg):
            with open(geo_reg, 'r') as f:
                pathways = json.load(f).get("information_loss_geometry", {}).get("loss_pathways", [])
                trace["information_loss_trace"]["pathway"] = next((p for p in pathways if query in p["operator"]), None)

        if os.path.exists(class_reg):
             with open(class_reg, 'r') as f:
                classes = json.load(f).get("operator_loss_classification", {}).get("classifications", [])
                trace["information_loss_trace"]["classification"] = next((c for c in classes if query in c["operator"] or query in c["class"]), None)

        if os.path.exists(rec_reg):
             with open(rec_reg, 'r') as f:
                mapping = json.load(f).get("operator_recursion_mapping", [])
                trace["information_loss_trace"]["recursive_behavior"] = next((m for m in mapping if query in m["operator"]), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                hyps = json.load(f).get("hypotheses", [])
                trace["information_loss_trace"]["hypothesis"] = next((h for h in hyps if query in h["target_theorem"] or query in h["geometry_basis"]), None)

    except Exception as e:
        trace["information_loss_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace information-loss geometry.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_information_loss(args.query)
    print(json.dumps(res, indent=2))
