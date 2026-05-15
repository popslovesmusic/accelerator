import json
import os
from datetime import datetime

def validate_mt_law_a_scaffold():
    results = {
        "mt_law_a_formal_lemma_scaffold_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_formal_lemma_scaffold_validation"]
    
    registry_path = "registry/math/mt_law_a_formal_lemma_registry.json"
    doc_path = "docs/math/mt_law_a_formal_lemma_scaffold.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A formal lemma registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check required fields
                required_fields = ["lemma_candidate", "formal_symbols", "assumptions", "constraints", "failure_conditions", "counterexample_classes", "known_gaps", "nonproof_flags", "governance_flags"]
                for field in required_fields:
                    if field not in data:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing required field in registry: {field}")
                
                # Check for proof claim (must be False)
                if data.get("nonproof_flags", {}).get("is_formal_proof") is True:
                    report["status"] = "fail"
                    report["errors"].append("CRITICAL GOVERNANCE VIOLATION: Lemma registry incorrectly claims formal proof.")
                
                report["checks"].append("MT-LAW-A formal lemma registry structure verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A formal lemma scaffold document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "dependency chain", "formal definitions",
                "persistence assumptions", "admissibility constraints",
                "finite budget constraints", "topology accessibility constraints",
                "identity continuity constraints", "persistence lemma candidate",
                "necessary conditions", "failure conditions",
                "counterexample boundaries", "cross-mechanism scope",
                "known gaps", "non-proof declaration", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from scaffold document.")
            
            # Check for non-proof declaration
            if "formal scaffold only" not in content or "not constitute a formal proof" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Missing or weak non-proof declaration in document.")

            # Status footer check
            if "ts2_formal_scaffold_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A scaffold document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_formal_lemma_scaffold_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "lemma_sections_verified": len(required_sections) if 'required_sections' in locals() else 0,
        "assumptions_verified": len(data.get("assumptions", [])) if 'data' in locals() else 0,
        "constraint_integrity": "high" if report["status"] == "pass" else "compromised",
        "proof_claim_violations": [e for e in report["errors"] if "proof" in e.lower()],
        "known_gaps_remaining": data.get("known_gaps", []) if 'data' in locals() else [],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_scaffold()
    print(json.dumps(res, indent=2))
