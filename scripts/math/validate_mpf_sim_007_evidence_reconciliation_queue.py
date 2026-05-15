import json
import os
from datetime import datetime

def validate_repair_queue():
    registry_path = "registry/math/mpf_sim_007_evidence_reconciliation_repair_queue_registry.json"
    doc_path = "docs/math/mpf_sim_007_evidence_reconciliation_repair_queue.md"
    result_path = "validation/results/mpf_sim_007_evidence_reconciliation_queue_result.json"
    val_out_path = "validation/results/mpf_sim_007_evidence_reconciliation_validation_result.json"
    
    report = {
        "validation_id": "VAL-SIM-007-VALID",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing repair queue registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing repair queue documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("repair queue results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")
            
            if data["governance"]["physics_status"] != "NON_PHYSICAL_ANALOG_MODEL":
                 report["status"] = "fail"
                 report["governance_violations"].append("missing non-physical analog model declaration in results")

            # Schema checks
            if not data.get("repair_entries"):
                 # This might be normal if the atlas had 100% supportive evidence
                 pass
            else:
                 required_fields = ["repair_entry_id", "source_evidence_entry", "repair_class", "proof_eligibility_effect"]
                 for field in required_fields:
                     if field not in data["repair_entries"][0]:
                          report["status"] = "fail"
                          report["governance_violations"].append(f"missing field {field} in repair queue entries")

    # 3. Documentation Verification
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "repair targets"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_repair_queue()
    print(json.dumps(res, indent=2))
