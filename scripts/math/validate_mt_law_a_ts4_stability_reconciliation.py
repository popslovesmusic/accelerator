import json
import os
from datetime import datetime

def validate_mt_law_a_ts4_reconciliation():
    results = {
        "mt_law_a_ts4_stability_reconciliation_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_ts4_stability_reconciliation_validation"]
    
    registry_path = "registry/math/mt_law_a_ts4_stability_reconciliation_registry.json"
    recon_doc_path = "docs/math/mt_law_a_ts4_stability_reconciliation.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A TS4 stability reconciliation registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check Reconciliation Targets
                targets = data.get("reconciliation_targets", [])
                if len(targets) < 6:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient reconciliation targets: {len(targets)}/6")
                
                # Outcome check
                allowed_outcomes = [
                    "RESTRICTED_DOMAIN_STABILITY_CONSISTENT",
                    "COUNTEREXAMPLE_PRESSURE_REMAINS_ACTIVE",
                    "DIVERGENCE_REGIONS_REQUIRE_REFINEMENT",
                    "TS4_SCOPE_REMAINS_BOUNDED"
                ]
                outcome = data.get("reconciliation_outcome")
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
                found_blockers = data.get("mandatory_preserved_blockers", [])
                for blocker in required_blockers:
                    if blocker not in found_blockers:
                        report["status"] = "fail"
                        report["errors"].append(f"Mandatory preserved blocker '{blocker}' missing from registry.")

                report["checks"].append("MT-LAW-A TS4 stability reconciliation registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(recon_doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A TS4 stability reconciliation document missing.")
    else:
        with open(recon_doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "restricted stability region reconciliation", "excluded domain reconciliation",
                "counterexample pressure reconciliation", "failure boundary reconciliation",
                "cross-mechanism divergence reconciliation", "topology severance reconciliation",
                "identity continuity ambiguity reconciliation", "open blocker preservation",
                "governance consistency review", "reconciliation outcome", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for Reconciliation Target IDs in document
            for i in range(1, 7):
                if f"rec-a00{i}" not in content:
                    report["errors"].append(f"Reconciliation Target ID REC-A00{i} missing in document.")

            # Status footer check
            if "ts4_reconciliation_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A TS4 stability reconciliation document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_ts4_stability_reconciliation_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "reconciliation_targets_verified": len(targets) if 'targets' in locals() else 0,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_ts4_reconciliation()
    print(json.dumps(res, indent=2))
