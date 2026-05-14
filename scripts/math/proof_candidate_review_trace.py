import json
import os
import argparse

def trace_review_status(query):
    trace = {
        "proof_candidate_review_trace": {
            "query": query,
            "standards_active": False,
            "obligations": [],
            "rejection_criteria_checked": [],
            "incompleteness_handling_rule": None
        }
    }

    standard_path = "registry/math/proof_candidate_review_standard_registry.json"
    obligation_path = "registry/math/proof_candidate_counterexample_obligation_registry.json"
    incompleteness_path = "registry/math/proof_candidate_incompleteness_handling_registry.json"

    if os.path.exists(standard_path):
        trace["proof_candidate_review_trace"]["standards_active"] = True

    if os.path.exists(obligation_path):
        with open(obligation_path, 'r') as f:
            obligations = json.load(f).get("proof_candidate_counterexample_obligation", {}).get("obligations", [])
            for ob in obligations:
                if ob.get("target") == query:
                    trace["proof_candidate_review_trace"]["obligations"].append(ob)

    # Note: This is a trace of infrastructure relevance, not a status promotion.
    
    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace proof-candidate review status.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_review_status(args.query)
    print(json.dumps(res, indent=2))
