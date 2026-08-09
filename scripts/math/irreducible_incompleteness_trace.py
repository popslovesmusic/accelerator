import json
import os
import argparse

def trace_irreducibility(query):
    trace = {
        "irreducible_incompleteness_trace": {
            "query": query,
            "analysis": None,
            "decision": None,
            "refinement_path": None,
            "hypothesis_conversion": None
        }
    }

    analysis_reg = "registry/math/irreducible_incompleteness_analysis_registry.json"
    decision_reg = "registry/math/incompleteness_irreducibility_decision_registry.json"
    path_reg = "registry/math/incompleteness_refinement_path_registry.json"
    hyp_reg = "registry/math/incompleteness_to_hypothesis_conversion_registry.json"

    try:
        if os.path.exists(analysis_reg):
            with open(analysis_reg, 'r') as f:
                logs = json.load(f).get("irreducible_incompleteness_analysis", {}).get("analysis_log", [])
                trace["irreducible_incompleteness_trace"]["analysis"] = next((log for log in logs if query in log["target"]), None)

        if os.path.exists(decision_reg):
             with open(decision_reg, 'r') as f:
                decisions = json.load(f).get("decisions", [])
                trace["irreducible_incompleteness_trace"]["decision"] = next((d for d in decisions if query in d["target"]), None)

        if os.path.exists(path_reg):
             with open(path_reg, 'r') as f:
                paths = json.load(f).get("paths", [])
                trace["irreducible_incompleteness_trace"]["refinement_path"] = next((p for p in paths if query in p["target"]), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                conversions = json.load(f).get("conversions", [])
                trace["irreducible_incompleteness_trace"]["hypothesis_conversion"] = next((c for c in conversions if query in c["source"] or query in c["target_theorem"]), None)

    except Exception as e:
        trace["irreducible_incompleteness_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace irreducible incompleteness.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_irreducibility(args.query)
    print(json.dumps(res, indent=2))
