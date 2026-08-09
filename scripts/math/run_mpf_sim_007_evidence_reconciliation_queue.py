import json
import os
from datetime import datetime

def run_repair_queue():
    """
    Runner for the Evidence-Reconciliation Repair Queue.
    Identifies mixed or blocking evidence from the atlas and populates the queue.
    """
    atlas_path = "validation/results/mpf_sim_006_cross_simulation_evidence_atlas_result.json"
    result_path = "validation/results/mpf_sim_007_evidence_reconciliation_queue_result.json"
    
    if not os.path.exists(atlas_path):
        return {"status": "fail", "reason": "atlas result missing"}

    with open(atlas_path, 'r', encoding='utf-8') as f:
        atlas_data = json.load(f)

    queue = {
        "queue_id": "SIM-REPAIR-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "repair_entries": [],
        "governance": {
            "theorem_status": "NOT_PROVEN",
            "scope_status": "STRICTLY_LOCAL_RESTRICTED_DOMAIN",
            "physics_status": "NON_PHYSICAL_ANALOG_MODEL"
        }
    }

    # Map atlas entries to repair obligations
    for entry in atlas_data["cross_simulation_entries"]:
        ev_class = entry["evidence_class"]
        
        if ev_class in ["SIM-EVIDENCE-MIXED", "SIM-EVIDENCE-BLOCKING"]:
            repair_entry = {
                "repair_entry_id": f"REP-{entry['entry_id']}",
                "source_evidence_entry": entry["entry_id"],
                "trigger_condition": ev_class,
                "failure_geometry_links": [f"FG-A{entry['entry_id'].split('-')[1]}" if '-' in entry['entry_id'] else "unknown"],
                "repair_class": "SIM-REPAIR-METASTABLE" if ev_class == "SIM-EVIDENCE-MIXED" else "SIM-REPAIR-BLOCKING",
                "proof_eligibility_effect": "review_required" if ev_class == "SIM-EVIDENCE-MIXED" else "blocked",
                "recommended_action": "Map transition thresholds and verify re-entry conditions."
            }
            queue["repair_entries"].append(repair_entry)

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2)

    print(f"Evidence reconciliation repair queue updated. Results in {result_path}")
    return queue

if __name__ == "__main__":
    run_repair_queue()
