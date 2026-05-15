import json
import os
from datetime import datetime

def validate_mt_law_a_excluded_domains():
    results = {
        "mt_law_a_excluded_domains_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_excluded_domains_validation"]
    
    registry_path = "registry/math/mt_law_a_excluded_domain_registry.json"
    doc_path = "docs/math/mt_law_a_excluded_domains.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A excluded domain registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for all 6 excluded domains
                domains = data.get("excluded_domains", [])
                if len(domains) < 6:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient excluded domains: {len(domains)}/6")
                
                # Check for mandatory fields in each domain
                required_fields = ["excluded_domain_id", "exclusion_condition", "linked_counterexample", "linked_proof_obligation", "blocked_claim", "required_failure_signature", "status"]
                for d in domains:
                    for field in required_fields:
                        if field not in d:
                            report["errors"].append(f"Excluded domain {d.get('excluded_domain_id')} missing field: {field}")

                report["checks"].append("MT-LAW-A excluded domain registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A excluded domains document missing.")
    else:
        with open(doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = ["purpose", "excluded domain taxonomy", "governance constraints", "status footer"]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for domain IDs in document
            for i in range(1, 7):
                if f"ed-a00{i}" not in content:
                    report["errors"].append(f"Excluded Domain ED-A00{i} missing in document.")

            # Status footer check
            if "ts3_excluded_domain_mapping" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A excluded domains document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_excluded_domain_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "excluded_domains_mapped": len(domains) if 'domains' in locals() else 0,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_excluded_domains()
    print(json.dumps(res, indent=2))
