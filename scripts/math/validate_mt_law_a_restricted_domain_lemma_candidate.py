import json
import os
from datetime import datetime

def validate_mt_law_a_restricted_domain():
    results = {
        "mt_law_a_restricted_domain_lemma_candidate_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_restricted_domain_lemma_candidate_validation"]
    
    registry_path = "registry/math/mt_law_a_restricted_domain_lemma_candidate_registry.json"
    doc_path = "docs/math/mt_law_a_restricted_domain_lemma_candidate.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A restricted domain registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check required fields
                required_fields = ["restricted_domain_conditions", "candidate_statement", "excluded_domains", "governance_flags"]
                for field in required_fields:
                    if field not in data:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing required field in registry: {field}")
                
                # Check governance (promotion blocked)
                gov = data.get("governance_flags", {})
                if gov.get("proof_status") != "TS3_restricted_domain_candidate_only":
                    report["status"] = "fail"
                    report["errors"].append(f"Incorrect proof status: {gov.get('proof_status')}. Must be 'TS3_restricted_domain_candidate_only'.")

                report["checks"].append("MT-LAW-A restricted domain registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A restricted domain document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "restricted domain declaration", "explicit non-universality declaration",
                "candidate lemma statement", "local assumptions", "required constraints",
                "excluded domains", "preserved counterexamples", "remaining open obligations",
                "known blockers", "governance status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Non-universality language check
            required_lang = [
                "strictly local restricted domain",
                "does not establish universal persistence",
                "does not establish global closure",
                "non-physical",
                "active and non-discharged"
            ]
            for lang in required_lang:
                if lang not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Required non-universality language missing: '{lang}'")

            # Check for candidate statement without promotion
            if "not a global theorem" not in content or "not proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Candidate statement missing required 'NOT PROVEN' or 'NOT GLOBAL' markers.")

        report["checks"].append("MT-LAW-A restricted domain document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_restricted_domain_lemma_candidate_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "restricted_domain_explicit": True if "strictly local restricted domain" in content else False,
        "candidate_lemma_stated": True if "candidate lemma statement" in content else False,
        "excluded_domains_listed": len(data.get("excluded_domains", [])) if 'data' in locals() else 0,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_restricted_domain()
    print(json.dumps(res, indent=2))
