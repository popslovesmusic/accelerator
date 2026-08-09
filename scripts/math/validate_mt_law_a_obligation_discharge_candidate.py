import json
import os
from datetime import datetime

def validate_mt_law_a_discharge_candidates():
    results = {
        "mt_law_a_obligation_discharge_candidate_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_obligation_discharge_candidate_validation"]
    
    registry_path = "registry/math/mt_law_a_obligation_discharge_candidate_registry.json"
    doc_path = "docs/math/mt_law_a_obligation_discharge_candidate.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A discharge registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for all 7 obligations
                reviews = data.get("obligation_reviews", [])
                if len(reviews) < 7:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient obligation reviews: {len(reviews)}/7")
                
                # Forbidden status check
                forbidden = ["PROVEN", "FULLY_DISCHARGED", "THEOREM_COMPLETE"]
                for r in reviews:
                    if r.get("candidate_status") in forbidden:
                        report["status"] = "fail"
                        report["errors"].append(f"CRITICAL GOVERNANCE VIOLATION: Forbidden status {r.get('candidate_status')} assigned to {r.get('id')}.")
                
                # Verify supporting assumptions and stress domains are recorded
                for r in reviews:
                    if not r.get("supporting_local_assumptions") and r.get("candidate_status") != "BLOCKED":
                        report["errors"].append(f"Review for {r.get('id')} missing supporting assumptions.")
                
                report["checks"].append("MT-LAW-A discharge registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A discharge document missing.")
    else:
        with open(doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "candidate discharge policy", "obligation reviews",
                "blockers and counterexamples", "governance constraints", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for IDs
            for i in range(1, 8):
                if f"po-a00{i}" not in content:
                    report["errors"].append(f"Review for PO-A00{i} missing in document.")

            # Status footer check
            if "ts3_local_discharge_candidates_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A discharge document scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_obligation_discharge_candidate_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "obligations_reviewed": len(reviews) if 'reviews' in locals() else 0,
        "governance_violations": report["errors"] + report["warnings"],
        "blockers_preserved": True if "blockers and counterexamples" in content else False,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_discharge_candidates()
    print(json.dumps(res, indent=2))
