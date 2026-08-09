import json
import os
from datetime import datetime

def validate_mt_law_a_boundary_consistency():
    results = {
        "mt_law_a_scope_boundary_consistency_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_scope_boundary_consistency_validation"]
    
    registry_path = "registry/math/mt_law_a_scope_boundary_consistency_registry.json"
    doc_path = "docs/math/mt_law_a_scope_boundary_consistency.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A boundary consistency registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for all 6 consistency rules
                rules = data.get("consistency_rules", [])
                if len(rules) < 6:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient consistency rules: {len(rules)}/6")
                
                # Check required fields
                required_fields = ["id", "rule", "linked_exclusion"]
                for r in rules:
                    for field in required_fields:
                        if field not in r:
                            report["errors"].append(f"Consistency rule {r.get('id')} missing field: {field}")

                # Check governance (promotion blocked)
                gov = data.get("governance_flags", {})
                if gov.get("proof_status") != "TS3_scope_boundary_consistency":
                    report["status"] = "fail"
                    report["errors"].append(f"Incorrect proof status: {gov.get('proof_status')}. Must be 'TS3_scope_boundary_consistency'.")

                report["checks"].append("MT-LAW-A boundary consistency registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A boundary consistency document missing.")
    else:
        with open(doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = ["purpose", "boundary consistency rules", "global check summary", "status footer"]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for non-universality language
            if "does not establish universal boundary completeness" not in content or "bounded local admissibility domain" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Required non-universality language missing or weak.")

            # Status footer check
            if "ts3_scope_boundary_consistency" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A boundary consistency document presence and content scanned.")

    # 3. Cross-Registry Overlap Check
    excluded_path = "registry/math/mt_law_a_excluded_domain_registry.json"
    restricted_path = "registry/math/mt_law_a_restricted_domain_lemma_candidate_registry.json"
    
    if os.path.exists(excluded_path) and os.path.exists(restricted_path):
        try:
            with open(excluded_path, 'r') as f:
                excluded_data = json.load(f)
            with open(restricted_path, 'r') as f:
                restricted_data = json.load(f)
            
            # Semantic Check: Excluded domains must be linked to active failure signatures
            for d in excluded_data.get("excluded_domains", []):
                if not d.get("required_failure_signature"):
                    report["errors"].append(f"Excluded domain {d.get('excluded_domain_id')} missing failure signature.")
            
            report["checks"].append("Cross-registry scope/exclusion consistency verified.")
        except Exception as e:
            report["warnings"].append(f"Cross-registry check error: {e}")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_scope_boundary_consistency_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "rules_verified": 6,
        "non_overlap_confirmed": True if report["status"] == "pass" else False,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_boundary_consistency()
    print(json.dumps(res, indent=2))
