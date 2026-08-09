import json
import os
from datetime import datetime

def validate_mt_law_a_ts4_review():
    results = {
        "mt_law_a_ts4_restricted_domain_review_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_ts4_restricted_domain_review_validation"]
    
    registry_path = "registry/math/mt_law_a_ts4_review_registry.json"
    review_doc_path = "docs/math/mt_law_a_ts4_restricted_domain_review.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A TS4 review registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check Review Targets
                targets = data.get("review_targets", [])
                if len(targets) < 6:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient review targets: {len(targets)}/6")
                
                # Outcome check
                allowed_outcomes = [
                    "TS4_RESTRICTED_DOMAIN_REVIEW_ALLOWED",
                    "TS4_COUNTEREXAMPLE_PRESSURE_REMAINS_HIGH",
                    "TS4_SCOPE_REFINEMENT_REQUIRED",
                    "TS4_REVIEW_DEFERRED_PENDING_BLOCKERS"
                ]
                outcome = data.get("review_outcome")
                if outcome not in allowed_outcomes:
                    report["status"] = "fail"
                    report["errors"].append(f"CRITICAL GOVERNANCE VIOLATION: Forbidden outcome '{outcome}' assigned.")
                
                # Mandatory Blockers check
                required_blockers = [
                    "topology severance divergence hotspots",
                    "identity continuity ambiguity",
                    "reconstruction equivalence incompleteness",
                    "oscillatory non-stabilization regions",
                    "cross-mechanism divergence regions",
                    "threshold-sensitive metastability"
                ]
                found_blockers = data.get("mandatory_open_blockers", [])
                for blocker in required_blockers:
                    if blocker not in found_blockers:
                        report["status"] = "fail"
                        report["errors"].append(f"Mandatory open blocker '{blocker}' missing from registry.")

                report["checks"].append("MT-LAW-A TS4 review registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(review_doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A TS4 review document missing.")
    else:
        with open(review_doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "ts4 restricted-domain scope verification", "formal definition consistency review",
                "proof obligation consistency review", "restricted stability region review",
                "counterexample preservation review", "failure boundary integrity review",
                "cross-mechanism divergence review", "excluded domain integrity review",
                "governance compliance review", "open blocker preservation",
                "ts4 review outcome", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for Review Target IDs in document
            for i in range(1, 7):
                if f"ts4-a00{i}" not in content:
                    report["errors"].append(f"Review Target ID TS4-A00{i} missing in document.")

            # Status footer check
            if "ts4_restricted_review_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A TS4 review document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_ts4_restricted_domain_review_result.json"
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
    res = validate_mt_law_a_ts4_review()
    print(json.dumps(res, indent=2))
