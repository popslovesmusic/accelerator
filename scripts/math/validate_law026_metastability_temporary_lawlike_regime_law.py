import json
import os

def validate_law026():
    results = {
        "law026_metastability_temporary_lawlike_regime_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["law026_metastability_temporary_lawlike_regime_law_validation"]
    
    registry_path = "registry/math/law026_metastability_temporary_lawlike_regime_law_registry.json"
    doc_path = "docs/math/law026_metastability_temporary_lawlike_regime_law.md"
    result_path = "outputs/math_tests/law026_metastability_temporary_lawlike_regime_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("LAW-026 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "metastable_regime_candidate_explicit",
                    "validity_window_candidate_explicit",
                    "lifespan_condition_explicit",
                    "transition_condition_explicit",
                    "temporary_law_clause_explicit",
                    "eternal_law_claim_blocked",
                    "universal_regime_claim_blocked"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                report["checks"].append("LAW-026 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("LAW-026 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "metastable regime", "validity window",
                "lifespan condition", "transition condition", "temporary law clause",
                "no physics claim", "no eternal laws",
                "no universal regime structure"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Term '{term}' missing from law document.")
        report["checks"].append("LAW-026 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        report["status"] = "fail"
        report["errors"].append("LAW-026 execution result missing.")
    else:
        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     report["status"] = "fail"
                     report["errors"].append("LAW-026 execution result indicates failure.")
            report["checks"].append("LAW-026 execution result verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Result parse error: {e}")

    output_path = "outputs/audits/law026_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_law026()
    print(json.dumps(res, indent=2))
