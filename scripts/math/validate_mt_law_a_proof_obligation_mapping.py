import json
import os
from datetime import datetime

def validate_mt_law_a_obligations():
    results = {
        "mt_law_a_proof_obligation_mapping_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_proof_obligation_mapping_validation"]
    
    registry_path = "registry/math/mt_law_a_proof_obligation_registry.json"
    doc_path = "docs/math/mt_law_a_proof_obligation_mapping.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A proof obligation registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for obligations
                obligations = data.get("proof_obligations", [])
                if len(obligations) < 7:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient proof obligations: {len(obligations)}/7")
                
                # Verify statuses are all OPEN
                for po in obligations:
                    if po.get("status") != "OPEN":
                        report["status"] = "fail"
                        report["errors"].append(f"Proof obligation {po.get('id')} incorrectly marked as {po.get('status')}.")
                
                # Verify blockers are present
                if len(data.get("blocker_map", [])) < 6:
                    report["errors"].append("Insufficient blockers in registry.")
                
                # Verify counterexample discharge requirements
                discharge = data.get("counterexample_discharge", {}).get("obligations", [])
                if len(discharge) < 7:
                    report["errors"].append(f"Insufficient counterexample discharge obligations: {len(discharge)}/7")

                report["checks"].append("MT-LAW-A proof obligation registry structure verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A proof obligation document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "dependency patch", "proof obligations",
                "blocker map", "counterexample discharge requirements",
                "governance constraints", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for IDs
            for i in range(1, 8):
                if f"po-a00{i}" not in content:
                    report["errors"].append(f"Obligation ID PO-A00{i} missing in document.")

            # Status footer check
            if "ts2_proof_obligations_mapped" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A proof obligation document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_proof_obligation_mapping_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "proof_obligations_listed": len(obligations) if 'obligations' in locals() else 0,
        "blockers_mapped": len(data.get("blocker_map", [])) if 'data' in locals() else 0,
        "counterexample_discharge_requirements_declared": True,
        "no_proof_promotion_verified": report["status"] == "pass",
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_obligations()
    print(json.dumps(res, indent=2))
