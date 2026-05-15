import json
import os
from datetime import datetime

def validate_mt_law_a_review():
    results = {
        "mt_law_a_restricted_lemma_review_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_restricted_lemma_review_validation"]
    
    registry_path = "registry/math/mt_law_a_restricted_lemma_review_registry.json"
    doc_path = "docs/math/mt_law_a_restricted_lemma_review.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A review registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for all 7 review targets
                targets = data.get("review_targets", [])
                if len(targets) < 7:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient review targets: {len(targets)}/7")
                
                # Forbidden outcome check
                forbidden = ["THEOREM_PROVEN", "UNIVERSALLY_VALID", "COUNTEREXAMPLES_DISCHARGED", "GLOBAL_CLOSURE_ESTABLISHED", "PHYSICS_MAPPING_CONFIRMED"]
                if data.get("review_outcome") in forbidden:
                    report["status"] = "fail"
                    report["errors"].append(f"CRITICAL GOVERNANCE VIOLATION: Forbidden outcome {data.get('review_outcome')} assigned.")
                
                report["checks"].append("MT-LAW-A review registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A review document missing.")
    else:
        with open(doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "restricted domain summary", "assumption integrity review",
                "excluded domain review", "reentry condition review",
                "counterexample preservation review", "governance compliance review",
                "open blockers", "non-universality confirmation",
                "review outcome summary", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for Target IDs in document
            for i in range(1, 8):
                if f"rv-a00{i}" not in content:
                    report["errors"].append(f"Review Target ID RV-A00{i} missing in document.")

            # Status footer check
            if "ts3_review_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A review document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_restricted_lemma_review_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "review_targets_verified": len(targets) if 'targets' in locals() else 0,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_review()
    print(json.dumps(res, indent=2))
