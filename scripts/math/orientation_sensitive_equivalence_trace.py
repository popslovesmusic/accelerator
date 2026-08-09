import json
import os
import argparse

def trace_orientation_equivalence(query):
    trace = {
        "orientation_sensitive_equivalence_trace": {
            "query": query,
            "refinement_class": None,
            "preimage_refinement": None,
            "branch_family": None,
            "transport_loss": None,
            "hypothesis": None
        }
    }

    geo_reg = "registry/math/orientation_sensitive_equivalence_geometry_registry.json"
    ref_reg = "registry/math/orientation_refined_preimage_registry.json"
    br_reg = "registry/math/orientation_conditioned_branch_registry.json"
    loss_reg = "registry/math/orientation_transport_loss_registry.json"
    hyp_reg = "registry/math/orientation_reconstruction_hypothesis_registry.json"

    if query == "orientation_operator_minus_i":
        query = "-(i)"

    try:
        if os.path.exists(geo_reg):
            with open(geo_reg, 'r') as f:
                classes = json.load(f).get("orientation_sensitive_equivalence_geometry", {}).get("refinement_classes", [])
                trace["orientation_sensitive_equivalence_trace"]["refinement_class"] = next((c for c in classes if query in c["name"] or query in str(c.get("operator", "")) or query in c["id"]), None)

        if os.path.exists(ref_reg):
             with open(ref_reg, 'r') as f:
                refinements = json.load(f).get("preimage_refinements", [])
                trace["orientation_sensitive_equivalence_trace"]["preimage_refinement"] = next((r for r in refinements if query in r["source_equivalence_class"] or query in r["outcome"]), None)

        if os.path.exists(br_reg):
             with open(br_reg, 'r') as f:
                families = json.load(f).get("branch_families", [])
                trace["orientation_sensitive_equivalence_trace"]["branch_family"] = next((f for f in families if query in f["name"] or query in f["description"] or query in f["id"] or query in f.get("operator", "")), None)

        if os.path.exists(loss_reg):
             with open(loss_reg, 'r') as f:
                losses = json.load(f).get("loss_events", [])
                trace["orientation_sensitive_equivalence_trace"]["transport_loss"] = next((l for l in losses if query in str(l.get("operator", "")) or query in l["mechanism"] or query in l["id"]), None)

        if os.path.exists(hyp_reg):
             with open(hyp_reg, 'r') as f:
                hyps = json.load(f).get("hypotheses", [])
                for h in hyps:
                    target = h.get("target_theorem") or h.get("target_reduction_chain")
                    if target and (query in target or query in h.get("statement", "")):
                        trace["orientation_sensitive_equivalence_trace"]["hypothesis"] = h
                        break

    except Exception as e:
        trace["orientation_sensitive_equivalence_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace orientation-sensitive equivalence geometry.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_orientation_equivalence(args.query)
    print(json.dumps(res, indent=2))
