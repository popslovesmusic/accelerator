import json
import os
import argparse

def trace_rc001_derivation(query_id, rc001_reg, evidence_reg):
    try:
        with open(rc001_reg, 'r') as f: rc001_data = json.load(f)
        with open(evidence_reg, 'r') as f: evidence_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    if query_id != "RC-001":
        return {"error": f"Trace target {query_id} not supported by this script."}

    trace = {
        "rc001_derivation_trace": {
            "chain_id": "RC-001",
            "status": rc001_data["meta"]["status"],
            "step_resolutions": rc001_data["step_resolutions"],
            "explicit_evidence_mappings": evidence_data["evidence_entries"]
        }
    }

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-001 derivation closure status.")
    parser.add_argument("--query", required=True, help="Chain ID (e.g. RC-001)")
    parser.add_argument("--rc001", default="registry/math/rc001_derivation_closure_registry.json")
    parser.add_argument("--evidence", default="registry/math/rc001_step_evidence_registry.json")
    
    args = parser.parse_args()
    res = trace_rc001_derivation(args.query, args.rc001, args.evidence)
    print(json.dumps(res, indent=2))
