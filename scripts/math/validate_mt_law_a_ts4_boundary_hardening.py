import json
import os
from datetime import datetime

def validate_mt_law_a_ts4_hardening():
    results = {
        "mt_law_a_ts4_boundary_hardening_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_ts4_boundary_hardening_validation"]
    
    registry_path = "registry/math/mt_law_a_ts4_boundary_hardening_registry.json"
    hardening_doc_path = "docs/math/mt_law_a_ts4_boundary_hardening.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A TS4 boundary hardening registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check Hardening Targets
                targets = data.get("hardening_targets", [])
                if len(targets) < 6:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient hardening targets: {len(targets)}/6")
                for target in targets:
                    if target.get("status") != "HARDENED":
                        report["status"] = "fail"
                        report["errors"].append(f"Hardening target '{target.get('id')}' not hardened.")
                
                # Check Detection Rules
                rules = data.get("detection_rules", [])
                if len(rules) < 5:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient detection rules: {len(rules)}/5")
                for rule in rules:
                    if rule.get("status") != "OPERATIONAL":
                        report["status"] = "fail"
                        report["errors"].append(f"Detection rule '{rule.get('id')}' not operational.")
                
                # Outcome check
                allowed_outcomes = [
                    "TS4_BOUNDARIES_HARDENED",
                    "COUNTEREXAMPLE_ISOLATION_CONFIRMED",
                    "SCOPE_LEAKAGE_BLOCKED",
                    "DIVERGENCE_REGIONS_PRESERVED"
                ]
                outcome = data.get("hardening_outcome")
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

                report["checks"].append("MT-LAW-A TS4 boundary hardening registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(hardening_doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A TS4 boundary hardening document missing.")
    else:
        with open(hardening_doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "restricted-domain boundary reinforcement", "excluded-domain isolation reinforcement",
                "counterexample isolation reinforcement", "failure boundary reinforcement",
                "cross-mechanism divergence reinforcement", "normalization drift prevention",
                "implicit universality detection", "scope leakage detection",
                "governance reinforcement", "hardening outcome", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for Hardening Target IDs in document
            for i in range(1, 7):
                if f"hd-a00{i}" not in content:
                    report["errors"].append(f"Hardening Target ID HD-A00{i} missing in document.")

            # Check for Detection Rule IDs in document
            for i in range(1, 6):
                if f"dr-a00{i}" not in content:
                    report["errors"].append(f"Detection Rule ID DR-A00{i} missing in document.")

            # Status footer check
            if "ts4_boundary_hardening_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A TS4 boundary hardening document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_ts4_boundary_hardening_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "hardening_targets_hardened": len([t for t in data.get("hardening_targets", []) if t.get("status") == "HARDENED"]) if 'data' in locals() else 0,
        "detection_rules_operational": len([r for r in data.get("detection_rules", []) if r.get("status") == "OPERATIONAL"]) if 'data' in locals() else 0,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_ts4_hardening()
    print(json.dumps(res, indent=2))
