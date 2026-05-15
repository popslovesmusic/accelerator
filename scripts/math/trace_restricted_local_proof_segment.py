import json
import os
from datetime import datetime

def trace_proof_segment():
    """
    Traces the local proof segment back to eligible basins.
    """
    eligibility_path = "validation/results/stable_basin_proof_eligibility_summary.json"
    segment_registry_path = "registry/math/restricted_local_proof_segment_registry.json"
    trace_output_path = "validation/results/restricted_local_proof_segment_trace.json"
    
    if not os.path.exists(eligibility_path):
        return {"status": "fail", "reason": "eligibility summary missing"}

    with open(eligibility_path, 'r') as f:
        elig_data = json.load(f)

    trace = {
        "trace_id": "TRACE-RLP-SEGMENT-001",
        "timestamp": datetime.now().isoformat(),
        "eligible_basins_selected": [],
        "blocked_basins_identified": [],
        "segment_status": "drafted"
    }

    for assignment in elig_data["eligibility_assignments"]:
        if assignment["eligibility_class"] == "PFE-ELIGIBLE-LOCAL":
            trace["eligible_basins_selected"].append(assignment["counterexample_id"])
        else:
            trace["blocked_basins_identified"].append({
                "id": assignment["counterexample_id"],
                "class": assignment["eligibility_class"]
            })

    with open(trace_output_path, 'w') as f:
        json.dump(trace, f, indent=2)

    print(f"Proof segment trace complete. Logged to {trace_output_path}")
    return trace

if __name__ == "__main__":
    trace_proof_segment()
