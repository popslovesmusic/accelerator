import json
import os
import argparse

def trace_phase_3_stability(query_id, baseline_reg):
    try:
        with open(baseline_reg, 'r') as f: baseline_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by test_id or target
    entries = [e for e in baseline_data.get("baseline_tests", []) if e["test_id"] == query_id or e["target"] == query_id]
    
    if not entries:
        return {"error": f"Phase 3 stability baseline data for {query_id} not found."}

    trace = {
        "phase_3_stability_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        trace["phase_3_stability_trace"]["associated_entries"].append({
            "test_id": entry["test_id"],
            "target": entry["target"],
            "domain": entry["domain"],
            "perturbation_class": entry["perturbation_class"],
            "expected_behavior": entry["expected_behavior"],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace Phase 3 operational stability baseline dependencies.")
    parser.add_argument("--query", required=True, help="Target ID or Test ID (e.g., NavT or P3-STAB-001)")
    parser.add_argument("--baseline", default="registry/math/phase_3_stability_baseline_registry.json")
    
    args = parser.parse_args()
    res = trace_phase_3_stability(args.query, args.baseline)
    print(json.dumps(res, indent=2))
