import json
import os
import argparse

def trace_asymmetry(query):
    trace = {
        "continuation_reconstruction_trace": {
            "query": query,
            "asymmetry_status": None,
            "loss_classification": None,
            "operator_relation": None,
            "hypothesis": None
        }
    }

    asym_reg = "registry/math/continuation_reconstruction_asymmetry_registry.json"
    loss_reg = "registry/math/reconstruction_loss_classification_registry.json"
    op_reg = "registry/math/continuation_vs_reconstruction_operator_registry.json"
    hyp_reg = "registry/math/reconstruction_hypothesis_conversion_registry.json"

    try:
        if os.path.exists(asym_reg):
            with open(asym_reg, 'r') as f:
                targets = json.load(f).get("continuation_reconstruction_asymmetry", {}).get("asymmetry_targets", [])
                trace["continuation_reconstruction_trace"]["asymmetry_status"] = next((t for t in targets if query in t["operator"]), None)

        if os.path.exists(loss_reg):
             with open(loss_reg, 'r') as f:
                losses = json.load(f).get("reconstruction_loss_classification", {}).get("loss_classes", [])
                trace["continuation_reconstruction_trace"]["loss_classification"] = next((l for l in losses if query in l["name"] or query in l["example"]), None)

        if os.path.exists(op_reg):
             with open(op_reg, 'r') as f:
                ops = json.load(f).get("continuation_vs_reconstruction_operator", {}).get("operator_relations", [])
                trace["continuation_reconstruction_trace"]["operator_relation"] = next((o for o in ops if query in o["symbol"]), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                conversions = json.load(f).get("conversions", [])
                trace["continuation_reconstruction_trace"]["hypothesis"] = next((c for c in conversions if query in c["source_impossibility"] or query in c["target_theorem"]), None)

    except Exception as e:
        trace["continuation_reconstruction_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace continuation-reconstruction asymmetry.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_asymmetry(args.query)
    print(json.dumps(res, indent=2))
