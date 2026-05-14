import json
import os
import argparse

def trace_stress_status(query):
    trace = {
        "proof_candidate_stress_trace": {
            "query": query,
            "stress_tests": [],
            "adversarial_cases": [],
            "last_updated": None
        }
    }

    test_reg = "registry/math/proof_candidate_stress_test_registry.json"
    case_reg = "registry/math/proof_candidate_adversarial_case_registry.json"

    try:
        if os.path.exists(test_reg):
            with open(test_reg, 'r') as f:
                tests = json.load(f).get("proof_candidate_stress_tests", {}).get("tests", [])
                for t in tests:
                    if t["target"] == query:
                        trace["proof_candidate_stress_trace"]["stress_tests"].append(t)
        
        if os.path.exists(case_reg):
             with open(case_reg, 'r') as f:
                cases = json.load(f).get("proof_candidate_adversarial_cases", {}).get("cases", [])
                for c in cases:
                    if c["target"] == query:
                        trace["proof_candidate_stress_trace"]["adversarial_cases"].append(c)
    except Exception as e:
        trace["proof_candidate_stress_trace"]["errors"] = [str(e)]

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace proof-candidate stress status.")
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    
    res = trace_stress_status(args.query)
    print(json.dumps(res, indent=2))
