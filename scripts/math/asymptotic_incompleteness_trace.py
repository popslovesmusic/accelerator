import json
import os
import argparse

def trace_asymptotic_incompleteness(query):
    trace = {
        "asymptotic_incompleteness_trace": {
            "query": query,
            "classifications": [],
            "mappings": [],
            "blockers": [],
            "obligations": []
        }
    }

    class_path = "registry/math/open_question_incompleteness_classification.json"
    map_path = "registry/math/asymptotic_incompleteness_mapping_registry.json"
    block_path = "registry/math/proof_blocking_incompleteness_registry.json"
    ob_path = "registry/math/incompleteness_counterexample_obligation_registry.json"

    try:
        if os.path.exists(class_path):
            with open(class_path, 'r') as f:
                classes = json.load(f).get("open_question_incompleteness_classification", {}).get("classifications", [])
                for c in classes:
                    if query == "open_questions" or query in c["question"]:
                        trace["asymptotic_incompleteness_trace"]["classifications"].append(c)

        if os.path.exists(map_path):
             with open(map_path, 'r') as f:
                mappings = json.load(f).get("asymptotic_incompleteness_mapping", {}).get("mappings", [])
                for m in mappings:
                    if m["target"] == query:
                        trace["asymptotic_incompleteness_trace"]["mappings"].append(m)

        if os.path.exists(block_path):
             with open(block_path, 'r') as f:
                blockers = json.load(f).get("proof_blocking_incompleteness", {}).get("blockers", [])
                for b in blockers:
                    if b["target"] == query:
                        trace["asymptotic_incompleteness_trace"]["blockers"].append(b)

        if os.path.exists(ob_path):
             with open(ob_path, 'r') as f:
                obligations = json.load(f).get("incompleteness_counterexample_obligation", {}).get("obligations", [])
                for o in obligations:
                    if o["target"] == query:
                        trace["asymptotic_incompleteness_trace"]["obligations"].append(o)

    except Exception as e:
        trace["asymptotic_incompleteness_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace asymptotic incompleteness.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_asymptotic_incompleteness(args.query)
    print(json.dumps(res, indent=2))
