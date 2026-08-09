import json
import os
import argparse

def trace_mt001_readiness(query_id, readiness_reg):
    try:
        with open(readiness_reg, 'r') as f: readiness_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    if query_id != "MT-001":
        return {"error": f"Trace target {query_id} not supported by this script."}

    trace = {
        "mt001_formal_candidate_trace": {
            "theorem_id": readiness_data["readiness_summary"]["theorem_id"],
            "current_status": readiness_data["readiness_summary"]["current_status"],
            "readiness_level": readiness_data["readiness_summary"]["readiness_level"],
            "blocker_resolution": readiness_data["blocker_status"],
            "criteria_fulfillment": readiness_data["readiness_criteria_check"],
            "pending_requirements": readiness_data["pending_requirements"]
        }
    }

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace MT-001 formal-candidate readiness.")
    parser.add_argument("--query", required=True, help="Theorem ID (e.g. MT-001)")
    parser.add_argument("--readiness", default="registry/math/mt001_formal_candidate_readiness_registry.json")
    
    args = parser.parse_args()
    res = trace_mt001_readiness(args.query, args.readiness)
    print(json.dumps(res, indent=2))
