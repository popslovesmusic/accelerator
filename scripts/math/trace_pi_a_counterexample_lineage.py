import json
import os
from datetime import datetime

def trace_lineage():
    """
    Traces the lineage of Pi_A counterexamples.
    """
    lineage_path = "registry/math/pi_a_counterexample_lineage.json"
    atlas_path = "registry/math/pi_a_counterexample_reconciliation_atlas.json"
    
    if not os.path.exists(atlas_path):
        return {"status": "fail", "reason": "atlas missing"}

    with open(atlas_path, 'r') as f:
        atlas = json.load(f)

    lineage = {
        "trace_id": "TRACE-CE-LINEAGE-001",
        "timestamp": datetime.now().isoformat(),
        "origin_patch": "MPF-PF-013",
        "target_candidate": "LTC-001",
        "traces": []
    }

    for entry in atlas["counterexample_reconciliation_entries"]:
        trace = {
            "counterexample_id": entry["counterexample_id"],
            "operator_chain": entry["affected_operators"],
            "failure_geometry_link": "FG-A" + entry["counterexample_id"].split("-")[1],
            "discharge_status": entry["discharge_status"]
        }
        lineage["traces"].append(trace)

    with open(lineage_path, 'w') as f:
        json.dump(lineage, f, indent=2)

    print(f"Lineage trace complete. Logged to {lineage_path}")
    return lineage

if __name__ == "__main__":
    trace_lineage()
