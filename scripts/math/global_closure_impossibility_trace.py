import json
import os
import argparse

def trace_impossibility(query):
    trace = {
        "global_closure_impossibility_trace": {
            "query": query,
            "impossibility_target": None,
            "classification": None,
            "blocker": None,
            "hypothesis_conversion": None
        }
    }

    imp_path = "registry/math/global_closure_impossibility_registry.json"
    class_path = "registry/math/closure_status_classification_registry.json"
    block_path = "registry/math/global_closure_blocker_registry.json"
    hyp_path = "registry/math/impossibility_to_theorem_hypothesis_registry.json"

    try:
        if os.path.exists(imp_path):
            with open(imp_path, 'r') as f:
                targets = json.load(f).get("global_closure_impossibility", {}).get("targets", [])
                trace["global_closure_impossibility_trace"]["impossibility_target"] = next((t for t in targets if query in t["name"] or query in str(t["blockers"])), None)

        if os.path.exists(block_path):
             with open(block_path, 'r') as f:
                blockers = json.load(f).get("global_closure_blocker", {}).get("blockers", [])
                trace["global_closure_impossibility_trace"]["blocker"] = next((b for b in blockers if query in b["feature"] or query in b["scope"]), None)

        if os.path.exists(hyp_path):
             with open(hyp_path, 'r') as f:
                mappings = json.load(f).get("impossibility_to_theorem_hypothesis", {}).get("conversions", [])
                trace["global_closure_impossibility_trace"]["hypothesis_conversion"] = next((m for m in mappings if query in m["target_claim"] or query in m["statement"]), None)

    except Exception as e:
        trace["global_closure_impossibility_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace global closure impossibility.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_impossibility(args.query)
    print(json.dumps(res, indent=2))
