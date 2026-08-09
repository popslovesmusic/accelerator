import json
import os
import argparse

def trace_rc001_step02_derivation(query):
    trace = {
        "rc001_step02_derivation_trace": {
            "query": query,
            "status": "unknown",
            "basis": None,
            "evidence": [],
            "last_updated": None
        }
    }

    if query != "RC-001":
        return trace

    supported_reg = "registry/math/rc001_step02_derivation_supported_registry.json"

    try:
        if os.path.exists(supported_reg):
            with open(supported_reg, 'r') as f:
                data = json.load(f).get("rc001_step02_derivation_supported", {})
                trace["rc001_step02_derivation_trace"]["status"] = data.get("status")
                trace["rc001_step02_derivation_trace"]["basis"] = data.get("basis")
                trace["rc001_step02_derivation_trace"]["evidence"] = data.get("evidence", [])
                trace["rc001_step02_derivation_trace"]["last_updated"] = data.get("last_updated")
    except Exception as e:
        trace["rc001_step02_derivation_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-001 STEP-02 derivation status.")
    parser.add_argument("--query", default="RC-001")
    args = parser.parse_args()
    
    res = trace_rc001_step02_derivation(args.query)
    print(json.dumps(res, indent=2))
