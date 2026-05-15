import json
import os
from datetime import datetime

def validate_mt_law_a_counterexamples():
    results = {
        "mt_law_a_counterexample_obligations_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_counterexample_obligations_validation"]
    
    registry_path = "registry/math/mt_law_a_counterexample_registry.json"
    doc_path = "docs/math/mt_law_a_counterexample_obligations.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A counterexample registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check for counterexample classes
                classes = data.get("counterexample_classes", [])
                if len(classes) < 7:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient counterexample classes: {len(classes)}/7")
                
                required_ids = ["CE-A001", "CE-A002", "CE-A003", "CE-A004", "CE-A005", "CE-A006", "CE-A007"]
                found_ids = [c.get("id") for c in classes]
                for rid in required_ids:
                    if rid not in found_ids:
                        report["errors"].append(f"Missing required class ID: {rid}")

                # Check governance (promotion blocked)
                gov = data.get("governance_flags", {})
                if gov.get("promote_to_theorem") is True:
                    report["status"] = "fail"
                    report["errors"].append("Theorem promotion must be blocked in counterexample phase.")
                
                report["checks"].append("MT-LAW-A counterexample registry structure verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A counterexample document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "dependency patch", "failure class taxonomy",
                "budget overflow counterexample", "admissibility exhaustion counterexample",
                "topology severance counterexample", "identity fragmentation counterexample",
                "channel destabilization counterexample", "reconstruction divergence counterexample",
                "oscillatory instability counterexample", "simulation hooks",
                "proof blockers", "governance constraints", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from counterexample document.")
            
            # Governance compliance check
            forbidden_phrases = ["proof completion", "global closure", "physical validation"]
            for phrase in forbidden_phrases:
                if phrase in content and "no " not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Potential governance violation: phrase '{phrase}' found without negation.")

            # Status footer check
            if "ts0_counterexample_obligation" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A counterexample document presence and content scanned.")

    # Generate result file
    output_path = "validation/results/mt_law_a_counterexample_obligations_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "counterexample_classes_checked": len(classes) if 'classes' in locals() else 0,
        "missing_counterexample_classes": [rid for rid in required_ids if rid not in found_ids] if 'found_ids' in locals() else required_ids,
        "governance_violations": report["errors"] + report["warnings"],
        "proof_blockers_remaining": data.get("proof_blockers", []) if 'data' in locals() else [],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_counterexamples()
    print(json.dumps(res, indent=2))
