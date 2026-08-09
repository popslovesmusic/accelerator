import json
import os
import argparse

def trace_rc002_proof_candidate(query):
    trace = {
        "rc002_proof_candidate_trace": {
            "query": query,
            "status": "unknown",
            "readiness_state": "pending",
            "foundations": [],
            "governance_locks": [],
            "last_audit": None
        }
    }

    if query != "RC-002":
        return trace

    review_path = "registry/math/rc002_proof_candidate_review_registry.json"
    criteria_path = "registry/math/rc002_proof_candidate_readiness_criteria.json"

    try:
        if os.path.exists(review_path):
            with open(review_path, 'r') as f:
                review_data = json.load(f).get("rc002_proof_candidate_review", {})
                trace["rc002_proof_candidate_trace"]["status"] = review_data.get("status")
                trace["rc002_proof_candidate_trace"]["last_audit"] = review_data.get("last_audit")
                trace["rc002_proof_candidate_trace"]["governance_locks"] = review_data.get("governance_locks", [])
        
        if os.path.exists(criteria_path):
             with open(criteria_path, 'r') as f:
                criteria_data = json.load(f).get("readiness_criteria", {})
                trace["rc002_proof_candidate_trace"]["foundations"] = criteria_data.get("required_foundations", [])
    except Exception as e:
        trace["rc002_proof_candidate_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-002 proof candidate readiness.")
    parser.add_argument("--query", default="RC-002")
    args = parser.parse_args()
    
    res = trace_rc002_proof_candidate(args.query)
    print(json.dumps(res, indent=2))
