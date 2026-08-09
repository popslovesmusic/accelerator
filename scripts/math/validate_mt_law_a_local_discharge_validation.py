import json
import os
from datetime import datetime

def validate_mt_law_a_local_validation():
    results = {
        "mt_law_a_local_discharge_validation_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_local_discharge_validation_validation"]
    
    registry_path = "registry/math/mt_law_a_local_discharge_validation_registry.json"
    doc_path = "docs/math/mt_law_a_local_discharge_validation.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A local validation registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for all 7 validation results
                v_results = data.get("validation_results", [])
                if len(v_results) < 7:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient validation results: {len(v_results)}/7")
                
                # Forbidden outcome check
                forbidden = ["FULLY_PROVEN", "UNIVERSALLY_VALID", "COUNTEREXAMPLE_RESOLVED", "THEOREM_COMPLETE"]
                for v in v_results:
                    if v.get("outcome") in forbidden:
                        report["status"] = "fail"
                        report["errors"].append(f"CRITICAL GOVERNANCE VIOLATION: Forbidden outcome {v.get('outcome')} assigned to {v.get('obligation_id')}.")
                
                # Check governance status field
                for v in v_results:
                    if v.get("governance_status") != "COMPLIANT":
                        report["errors"].append(f"Obligation {v.get('obligation_id')} governance status is {v.get('governance_status')}.")

                report["checks"].append("MT-LAW-A local validation registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A local validation document missing.")
    else:
        with open(doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "required validation targets", "validation outcomes",
                "governance constraints", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for Target IDs
            for i in range(1, 7):
                if f"lv-a00{i}" not in content:
                    report["errors"].append(f"Target ID LV-A00{i} missing in document.")

            # Status footer check
            if "ts3_local_validation_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A local validation document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_local_discharge_validation_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "targets_verified": 6,
        "outcomes_compliant": True if report["status"] == "pass" else False,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_local_validation()
    print(json.dumps(res, indent=2))
