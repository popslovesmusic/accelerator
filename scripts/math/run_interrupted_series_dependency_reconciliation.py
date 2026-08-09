import json
import os
from datetime import datetime

def run_reconciliation_audit():
    """
    Runner for the Interrupted Series Dependency Reconciliation Audit.
    Enumerate series status and identify repair obligations.
    """
    registry_path = "registry/math/interrupted_series_dependency_reconciliation_registry.json"
    result_path = "validation/results/interrupted_series_dependency_reconciliation_result.json"
    
    if not os.path.exists(registry_path):
        return {"status": "fail", "reason": "reconciliation registry missing"}

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)

    audit_summary = {
        "audit_id": "VAL-DEP-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "families_audited": [],
        "repair_queue_count": 0,
        "governance": registry_data["governance"]
    }

    # Audit logic
    for family in registry_data["dependency_families"]:
        audit_entry = {
            "family_id": family["family_id"],
            "status": family["status"],
            "audit_class": "DEP-CLEAR"
        }
        
        if family["status"] == "PARTIAL_INTERRUPTED":
            audit_entry["audit_class"] = "DEP-REPAIR-QUEUE"
            audit_summary["repair_queue_count"] += 1
            
        audit_summary["families_audited"].append(audit_entry)

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(audit_summary, f, indent=2)

    print(f"Dependency reconciliation audit complete. Results in {result_path}")
    return audit_summary

if __name__ == "__main__":
    run_reconciliation_audit()
