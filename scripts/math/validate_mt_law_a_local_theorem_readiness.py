import json
import os
from datetime import datetime

def validate_mt_law_a_readiness():
    results = {
        "mt_law_a_local_theorem_readiness_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_local_theorem_readiness_validation"]
    
    registry_path = "registry/math/mt_law_a_local_theorem_readiness_registry.json"
    audit_doc_path = "docs/math/mt_law_a_local_theorem_readiness_audit.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A readiness registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for all 7 audit targets
                targets = data.get("audit_targets", [])
                if len(targets) < 7:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient audit targets: {len(targets)}/7")
                
                # Classification check
                allowed_classifications = [
                    "NOT_READY_FOR_TS4",
                    "PARTIALLY_READY_FOR_TS4_REVIEW",
                    "RESTRICTED_DOMAIN_TS4_REVIEW_CANDIDATE_ONLY"
                ]
                classification = data.get("readiness_classification")
                if classification not in allowed_classifications:
                    report["status"] = "fail"
                    report["errors"].append(f"CRITICAL GOVERNANCE VIOLATION: Forbidden classification '{classification}' assigned.")
                
                # Open Blockers check
                required_blockers = [
                    "topology severance divergence hotspots",
                    "identity continuity ambiguity",
                    "reconstruction equivalence incompleteness",
                    "oscillatory non-stabilization regions",
                    "cross-mechanism divergence regions",
                    "threshold-sensitive metastability"
                ]
                found_blockers = data.get("open_blockers", [])
                for blocker in required_blockers:
                    if blocker not in found_blockers:
                        report["status"] = "fail"
                        report["errors"].append(f"Mandatory open blocker '{blocker}' missing from registry.")

                report["checks"].append("MT-LAW-A readiness registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(audit_doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A readiness audit document missing.")
    else:
        with open(audit_doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "restricted-domain scope audit", "formal definition audit",
                "proof obligation audit", "counterexample preservation audit",
                "stress-domain audit", "cross-mechanism audit", "failure boundary audit",
                "excluded domain audit", "reentry logic audit", "governance compliance audit",
                "open blocker audit", "readiness classification", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for Audit Target IDs in document
            for i in range(1, 8):
                if f"ra-a00{i}" not in content:
                    report["errors"].append(f"Audit Target ID RA-A00{i} missing in document.")

            # Status footer check
            if "ts3_readiness_audit_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A readiness audit document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_local_theorem_readiness_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "audit_targets_verified": len(targets) if 'targets' in locals() else 0,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_readiness()
    print(json.dumps(res, indent=2))
