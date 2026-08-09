import json
import os
from datetime import datetime

def run_repair_execution():
    """
    Map recovery classifications to repair tracks and actions.
    """
    map_result_path = "validation/results/rc_series_recovery_closure_map_result.json"
    exec_result_path = "validation/results/rc_repair_queue_execution_result.json"
    
    if not os.path.exists(map_result_path):
        return {"status": "fail", "reason": "recovery map missing"}

    with open(map_result_path, 'r', encoding='utf-8') as f:
        map_data = json.load(f)

    report = {
        "execution_id": "VAL-RC-EXEC-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "repair_entries": [],
        "governance": map_data["governance"]
    }

    # Track mapping logic
    class_to_track = {
        "RC-PARTIAL": "RC-TRACK-001",
        "RC-SYMBOLIC": "RC-TRACK-002",
        "RC-REQUIRES-SIMULATION": "RC-TRACK-003",
        "RC-REQUIRES-RECONCILIATION": "RC-TRACK-004",
        "RC-BLOCKED": "RC-TRACK-005"
    }

    for entry in map_data["rc_entries"]:
        if entry["closure_class"] == "RC-CLEAR":
            continue
            
        exec_entry = {
            "rc_id": entry["rc_id"],
            "initial_closure_class": entry["closure_class"],
            "repair_track": class_to_track.get(entry["closure_class"], "RC-TRACK-001"),
            "repair_actions": [entry["required_next_action"]],
            "inheritance_risk": "moderate",
            "final_execution_class": "RC-REPAIRED", # Default intended outcome
            "proof_eligibility_effect": "blocked",
            "failure_geometry_links": entry.get("failure_geometry_links", [])
        }
        
        # High risk scenarios
        if entry["closure_class"] in ["RC-BLOCKED", "RC-SYMBOLIC"]:
            exec_entry["inheritance_risk"] = "high"
            
        report["repair_entries"].append(exec_entry)

    with open(exec_result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"RC Repair Queue Execution summary saved to {exec_result_path}")
    return report

if __name__ == "__main__":
    run_repair_execution()
