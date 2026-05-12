import json
import os
import argparse

def trace_operational_stability(query_id, stability_reg):
    try:
        with open(stability_reg, 'r') as f: stability_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by test_id or target_validator
    tests = [t for t in stability_data.get("stability_tests", []) if t["test_id"] == query_id or t["target_validator"] == query_id]
    
    if not tests:
        return {"error": f"Stability data for {query_id} not found in {stability_reg}"}

    trace = {
        "stability_trace": {
            "query_id": query_id,
            "associated_tests": []
        }
    }

    for test in tests:
        test_trace = {
            "test_id": test["test_id"],
            "target_validator": test["target_validator"],
            "stability_dimension": test["stability_dimension"],
            "perturbation_class": test["perturbation_class"],
            "expected_behavior": test["expected_behavior"],
            "dependencies": {
                "inputs": test["input_objects"],
                "operators": test["operators"]
            },
            "failure_risks": test["failure_modes"]
        }
        trace["stability_trace"]["associated_tests"].append(test_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace operational stability dependencies.")
    parser.add_argument("--query", required=True, help="Test ID or Validator ID (e.g., OST-RCV-001 or MPF-RCV-001)")
    parser.add_argument("--stability", default="registry/math/operational_stability_registry.json")
    
    args = parser.parse_args()
    res = trace_operational_stability(args.query, args.stability)
    print(json.dumps(res, indent=2))
