import json
import os
from datetime import datetime

def validate_mt_law_a_reentry():
    results = {
        "mt_law_a_reentry_conditions_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_reentry_conditions_validation"]
    
    registry_path = "registry/math/mt_law_a_reentry_condition_registry.json"
    doc_path = "docs/math/mt_law_a_reentry_conditions.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A reentry registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for all 6 reentry conditions
                reentries = data.get("reentry_conditions", [])
                if len(reentries) < 6:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient reentry conditions: {len(reentries)}/6")
                
                # Check mandatory fields
                required_fields = ["reentry_id", "linked_excluded_domain", "reentry_condition", "required_metric_signature", "required_evidence", "failure_history_preservation", "counterexample_status", "scope_status"]
                for r in reentries:
                    for field in required_fields:
                        if field not in r:
                            report["errors"].append(f"Reentry condition {r.get('reentry_id')} missing field: {field}")
                    
                    if r.get("counterexample_status") != "COUNTEREXAMPLE_REMAINS_ACTIVE_OUTSIDE_RESTRICTED_SCOPE":
                        report["status"] = "fail"
                        report["errors"].append(f"Invalid counterexample status for {r.get('reentry_id')}. Must be active.")

                report["checks"].append("MT-LAW-A reentry registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A reentry conditions document missing.")
    else:
        with open(doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = ["purpose", "reentry logic", "governance constraints", "status footer"]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for reentry IDs in document
            for i in range(1, 7):
                if f"re-a00{i}" not in content:
                    report["errors"].append(f"Reentry ID RE-A00{i} missing in document.")

            # Status footer check
            if "ts3_reentry_conditions_mapped" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A reentry conditions document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_reentry_condition_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "reentry_conditions_verified": len(reentries) if 'reentries' in locals() else 0,
        "failure_history_preservation_explicit": True if "failure history preservation" in content else False,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_reentry()
    print(json.dumps(res, indent=2))
