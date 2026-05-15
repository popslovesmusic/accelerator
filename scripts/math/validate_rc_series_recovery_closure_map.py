import json
import os
from datetime import datetime

def validate_recovery_map():
    registry_path = "registry/math/rc_series_recovery_closure_map_registry.json"
    doc_path = "docs/math/rc_series_recovery_closure_map.md"
    result_path = "validation/results/rc_series_recovery_closure_map_result.json"
    val_out_path = "validation/results/rc_series_recovery_closure_map_validation_result.json"
    
    report = {
        "validation_id": "VAL-RC-MAP-VALID",
        "status": "pass",
        "governance_violations": [],
        "rc_entries_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing recovery map registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing recovery map documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("recovery map results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Check for RC001-RC031
            rc_ids = [entry["rc_id"] for entry in data["rc_entries"]]
            if len(rc_ids) < 31:
                 report["status"] = "fail"
                 report["governance_violations"].append(f"missing entries in recovery map: found {len(rc_ids)}/31")
            
            # Check governance
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")

            # Check for non-clear entry actions
            for entry in data["rc_entries"]:
                if entry["closure_class"] != "RC-CLEAR" and entry["required_next_action"] == "None":
                     report["status"] = "fail"
                     report["governance_violations"].append(f"non-clear entry {entry['rc_id']} missing next action")
                report["rc_entries_verified"] += 1

    # 3. Documentation Verification
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "closure classification"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_recovery_map()
    print(json.dumps(res, indent=2))
