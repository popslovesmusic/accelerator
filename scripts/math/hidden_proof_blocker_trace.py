import json
import os
import argparse

def trace_hidden_blockers(query):
    trace = {
        "hidden_proof_blocker_trace": {
            "query": query,
            "discoveries": [],
            "candidates": [],
            "risks": [],
            "obligations": []
        }
    }

    disc_path = "registry/math/hidden_proof_blocker_discovery_registry.json"
    cand_path = "registry/math/hidden_incompleteness_candidate_registry.json"
    risk_path = "registry/math/unclassified_blocker_risk_registry.json"
    ob_path = "registry/math/hidden_counterexample_obligation_registry.json"

    try:
        if os.path.exists(disc_path):
            with open(disc_path, 'r') as f:
                logs = json.load(f).get("hidden_proof_blocker_discovery", {}).get("discovery_log", [])
                for log in logs:
                    if log["target"] == query or query in log["basis"]:
                        trace["hidden_proof_blocker_trace"]["discoveries"].append(log)

        if os.path.exists(cand_path):
             with open(cand_path, 'r') as f:
                cands = json.load(f).get("hidden_incompleteness_candidates", {}).get("candidates", [])
                for c in cands:
                    if query in c["target"]:
                        trace["hidden_proof_blocker_trace"]["candidates"].append(c)

        if os.path.exists(risk_path):
             with open(risk_path, 'r') as f:
                risks = json.load(f).get("unclassified_blocker_risk", {}).get("risks", [])
                for r in risks:
                    if r["target"] == query:
                        trace["hidden_proof_blocker_trace"]["risks"].append(r)

        if os.path.exists(ob_path):
             with open(ob_path, 'r') as f:
                obligations = json.load(f).get("hidden_counterexample_obligation", {}).get("obligations", [])
                for o in obligations:
                    if o["target"] == query:
                        trace["hidden_proof_blocker_trace"]["obligations"].append(o)

    except Exception as e:
        trace["hidden_proof_blocker_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace hidden proof blockers.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_hidden_blockers(args.query)
    print(json.dumps(res, indent=2))
