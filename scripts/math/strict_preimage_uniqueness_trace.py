import json
import os
import argparse

def trace_uniqueness(query):
    trace = {
        "strict_preimage_uniqueness_trace": {
            "query": query,
            "constraint_class": None,
            "splitting_rule": None,
            "failure_mode": None,
            "reconstructability_constraint": None,
            "hypothesis": None
        }
    }

    strict_reg = "registry/math/strict_preimage_uniqueness_constraints_registry.json"
    splitting_reg = "registry/math/orientation_preimage_splitting_registry.json"
    fm_reg = "registry/math/preimage_failure_mode_registry.json"
    local_reg = "registry/math/local_reconstructability_constraint_registry.json"
    hyp_reg = "registry/math/preimage_uniqueness_hypothesis_registry.json"

    if query == "orientation_operator_minus_i":
        query = "-(i)"

    try:
        if os.path.exists(strict_reg):
            with open(strict_reg, 'r') as f:
                classes = json.load(f).get("strict_preimage_uniqueness_constraints", {}).get("constraint_classes", [])
                trace["strict_preimage_uniqueness_trace"]["constraint_class"] = next((c for c in classes if query in c["name"] or query in str(c.get("condition", "")) or query in c["id"] or query in c.get("operator", "")), None)

        if os.path.exists(splitting_reg):
             with open(splitting_reg, 'r') as f:
                rules = json.load(f).get("splitting_rules", [])
                trace["strict_preimage_uniqueness_trace"]["splitting_rule"] = next((r for r in rules if query in r["target"] or query in r["mechanism"] or query in r["id"]), None)

        if os.path.exists(fm_reg):
             with open(fm_reg, 'r') as f:
                fms = json.load(f).get("failure_modes", [])
                trace["strict_preimage_uniqueness_trace"]["failure_mode"] = next((fm for fm in fms if query in fm["name"] or query in str(fm.get("operator", "")) or query in fm["id"]), None)

        if os.path.exists(local_reg):
             with open(local_reg, 'r') as f:
                constraints = json.load(f).get("constraints", [])
                trace["strict_preimage_uniqueness_trace"]["reconstructability_constraint"] = next((lc for lc in constraints if query in lc["name"] or query in lc["statement"] or query in lc["id"]), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                hyps = json.load(f).get("hypotheses", [])
                for h in hyps:
                    target = h.get("target_theorem") or h.get("target_reduction_chain")
                    if target and (query in target or query in h.get("statement", "")):
                        trace["strict_preimage_uniqueness_trace"]["hypothesis"] = h
                        break

    except Exception as e:
        trace["strict_preimage_uniqueness_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace strict preimage uniqueness constraints.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_uniqueness(args.query)
    print(json.dumps(res, indent=2))
