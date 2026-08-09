import json
import os
from datetime import datetime

def enforce_stop_conditions():
    conditions_path = "registry/autonomous_stop_conditions.json"
    failures_path = "registry/equivalence_failure_registry.json"
    
    if not os.path.exists(conditions_path) or not os.path.exists(failures_path):
        return

    with open(conditions_path, 'r') as f:
        conditions = json.load(f)
    with open(failures_path, 'r') as f:
        failures = json.load(f)

    print("Enforcing Autonomous Stop-Conditions...")
    
    # Check SC-001 (Example)
    failure_counts = {}
    for rec in failures.get("failure_records", []):
        tname = rec.get("tool_name")
        failure_counts[tname] = failure_counts.get(tname, 0) + 1
    
    for cond in conditions.get("stop_conditions", []):
        if cond["condition_id"] == "SC-001-EQUIV-FATAL":
            for tool, count in failure_counts.items():
                if count >= cond["threshold"]:
                    print(f"BLOCK: Stop Condition {cond['condition_id']} triggered for tool {tool}.")
                    return False

    print("Enforcement: ALL CLEAR")
    return True

if __name__ == "__main__":
    enforce_stop_conditions()
