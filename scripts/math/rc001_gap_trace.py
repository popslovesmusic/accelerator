import json
import os
import argparse

def trace_rc001_gap(query):
    trace = {
        "rc001_gap_trace": {
            "query": query,
            "status": "unknown",
            "gaps": [],
            "blockers": [],
            "last_audit": None
        }
    }

    if query != "RC-001":
        return trace

    gap_reg = "registry/math/rc001_proof_candidate_gap_registry.json"
    blocker_reg = "registry/math/rc001_remaining_blocker_registry.json"

    try:
        if os.path.exists(gap_reg):
            with open(gap_reg, 'r') as f:
                g_data = json.load(f).get("rc001_proof_candidate_gap", {})
                trace["rc001_gap_trace"]["status"] = g_data.get("status")
                trace["rc001_gap_trace"]["last_audit"] = g_data.get("last_audit")
                for domain, info in g_data.get("domains", {}).items():
                    if info.get("status") == "fail":
                        trace["rc001_gap_trace"]["gaps"].append({"domain": domain, "reason": info.get("basis")})
        
        if os.path.exists(blocker_reg):
             with open(blocker_reg, 'r') as f:
                b_data = json.load(f).get("rc001_remaining_blocker_set", {})
                trace["rc001_gap_trace"]["blockers"] = b_data.get("blockers", [])
    except Exception as e:
        trace["rc001_gap_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-001 readiness gaps.")
    parser.add_argument("--query", default="RC-001")
    args = parser.parse_args()
    
    res = trace_rc001_gap(args.query)
    print(json.dumps(res, indent=2))
