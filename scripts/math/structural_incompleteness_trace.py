import json
import os
import argparse

def trace_structural_incompleteness(query):
    trace = {
        "structural_incompleteness_trace": {
            "query": query,
            "classification": None,
            "irreducible_entry": None,
            "removable_entry": None,
            "theorem_hypothesis": None
        }
    }

    class_reg = "registry/math/structural_incompleteness_classification_registry.json"
    irr_reg = "registry/math/irreducible_incompleteness_registry.json"
    rem_reg = "registry/math/removable_incompleteness_registry.json"
    hyp_reg = "registry/math/incompleteness_to_theorem_hypothesis_registry.json"

    try:
        if os.path.exists(class_reg):
            with open(class_reg, 'r') as f:
                classes = json.load(f).get("structural_incompleteness_classification", {}).get("classifications", [])
                trace["structural_incompleteness_trace"]["classification"] = next((c for c in classes if query in c["target"]), None)

        if os.path.exists(irr_reg):
             with open(irr_reg, 'r') as f:
                entries = json.load(f).get("entries", [])
                trace["structural_incompleteness_trace"]["irreducible_entry"] = next((e for e in entries if query in e["target"]), None)

        if os.path.exists(rem_reg):
             with open(rem_reg, 'r') as f:
                entries = json.load(f).get("entries", [])
                trace["structural_incompleteness_trace"]["removable_entry"] = next((e for e in entries if query in e["target"]), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                mappings = json.load(f).get("mappings", [])
                trace["structural_incompleteness_trace"]["theorem_hypothesis"] = next((m for m in mappings if query in m["source_incompleteness"] or query in m["target_theorem"]), None)

    except Exception as e:
        trace["structural_incompleteness_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace structural incompleteness.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_structural_incompleteness(args.query)
    print(json.dumps(res, indent=2))
