import json
import os
import argparse

def trace_rc002_derivation(query_id, rc002_reg, evidence_reg):
    try:
        with open(rc002_reg, 'r') as f: rc002_data = json.load(f)
        with open(evidence_reg, 'r') as f: evidence_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    if query_id != "RC-002":
        return {"error": f"Trace target {query_id} not supported by this script."}

    trace = {
        "rc002_derivation_trace": {
            "chain_id": "RC-002",
            "status": rc002_data["meta"]["status"],
            "step_resolutions": rc002_data["step_resolutions"],
            "explicit_evidence_mappings": evidence_data["evidence_entries"]
        }
    }

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-002 derivation closure status.")
    parser.add_argument("--query", required=True, help="Chain ID (e.g. RC-002)")
    parser.add_argument("--rc002", default="registry/math/rc002_derivation_closure_registry.json")
    parser.add_argument("--evidence", default="registry/math/rc002_step_evidence_registry.json")
    
    args = parser.parse_args()
    res = trace_rc002_derivation(args.query, args.rc002, args.evidence)
    print(json.dumps(res, indent=2))
