import json
import os
from datetime import datetime

def validate_repair_execution():
    registry_path = "registry/math/rc_repair_queue_execution_registry.json"
    doc_path = "docs/math/rc_repair_queue_execution_plan.md"
    result_path = "validation/results/rc_repair_queue_execution_result.json"
    val_out_path = "validation/results/rc_repair_queue_execution_validation_result.json"
    
    report = {
        "validation_id": "VAL-RC-EXEC-VALID",
        "status": "pass",
        "governance_violations": [],
        "repair_entries_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing execution registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing execution document")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("execution results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Check governance
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")

            # Check schema fields
            required_fields = ["rc_id", "repair_track", "inheritance_risk", "proof_eligibility_effect"]
            for entry in data["repair_entries"]:
                for field in required_fields:
                    if field not in entry:
                         report["status"] = "fail"
                         report["governance_violations"].append(f"missing field {field} in execution entry {entry.get('rc_id')}")
                
                # Check mandate: No symbolic entry review ready
                if entry["initial_closure_class"] == "RC-SYMBOLIC" and entry["final_execution_class"] == "RC-READY-FOR-REVIEW":
                     report["status"] = "fail"
                     report["governance_violations"].append(f"symbolic entry {entry['rc_id']} improperly marked review ready")
                
                report["repair_entries_verified"] += 1

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "repair tracks"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_repair_execution()
    print(json.dumps(res, indent=2))
