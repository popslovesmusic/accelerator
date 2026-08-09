import json
import os
import argparse

def trace_rc002_counterexample(query):
    trace = {
        "rc002_counterexample_trace": {
            "query": query,
            "status": "unknown",
            "analysis": None,
            "failure_modes": [],
            "last_updated": None
        }
    }

    review_reg = "registry/math/rc002_counterexample_review_registry.json"
    fm_reg = "registry/math/rc002_counterexample_failure_modes.json"

    try:
        if os.path.exists(review_reg):
            with open(review_reg, 'r') as f:
                reviews = json.load(f).get("rc002_counterexample_review", {}).get("reviews", [])
                match = next((r for r in reviews if r["obligation_id"] == query), None)
                if match:
                    trace["rc002_counterexample_trace"]["status"] = match["status"]
                    trace["rc002_counterexample_trace"]["analysis"] = match["analysis"]
        
        if os.path.exists(fm_reg):
             with open(fm_reg, 'r') as f:
                fm_data = json.load(f).get("rc002_counterexample_failure_modes", {}).get("failure_modes", [])
                trace["rc002_counterexample_trace"]["failure_modes"] = fm_data
    except Exception as e:
        trace["rc002_counterexample_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace RC-002 counterexample obligation.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_rc002_counterexample(args.query)
    print(json.dumps(res, indent=2))
