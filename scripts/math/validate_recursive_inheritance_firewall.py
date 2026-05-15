import json
import os
from datetime import datetime

def validate_firewall():
    registry_path = "registry/math/recursive_inheritance_firewall_registry.json"
    doc_path = "docs/math/recursive_inheritance_firewall.md"
    result_path = "validation/results/recursive_inheritance_firewall_result.json"
    val_out_path = "validation/results/recursive_inheritance_firewall_validation_result.json"
    
    report = {
        "validation_id": "VAL-RIF-VALID",
        "status": "pass",
        "governance_violations": [],
        "inheritance_audits_verified": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing firewall registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing firewall documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("firewall results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")

            # Enforcement check: Blocked classes must have blocked inheritance
            for audit in data["inheritance_audits"]:
                if audit["initial_class"] in ["RC-SYMBOLIC", "RC-PARTIAL", "RC-BLOCKED", "CG-IMPACT-BLOCKING", "CG-IMPACT-DECEPTIVE"]:
                    if audit["inheritance_class"] not in ["INHERITANCE-BLOCKED", "INHERITANCE-QUARANTINED"]:
                        report["status"] = "fail"
                        report["governance_violations"].append(f"firewall breach for {audit['source_id']}: {audit['initial_class']} improperly allowed")
                report["inheritance_audits_verified"] += 1

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "firewall rules"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_firewall()
    print(json.dumps(res, indent=2))
