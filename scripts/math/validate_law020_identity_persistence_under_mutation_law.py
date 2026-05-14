import json
import os

def validate_law020():
    results = {
        "law020_identity_persistence_under_mutation_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["law020_identity_persistence_under_mutation_law_validation"]
    
    registry_path = "registry/math/law020_identity_persistence_under_mutation_law_registry.json"
    doc_path = "docs/math/law020_identity_persistence_under_mutation_law.md"
    result_path = "outputs/math_tests/law020_identity_persistence_under_mutation_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("LAW-020 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "continuation_channel_dependency_explicit",
                    "identity_relation_candidate_explicit",
                    "continuity_metric_candidate_explicit",
                    "fork_condition_explicit",
                    "merge_condition_explicit",
                    "identity_collapse_condition_explicit",
                    "nonprimitive_identity_clause_explicit"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                report["checks"].append("LAW-020 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("LAW-020 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "continuation channel", "identity relation candidate",
                "continuity metric", "fork condition",
                "merge condition", "identity collapse condition", "non-primitive identity clause",
                "no physics claim"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Term '{term}' missing from law document.")
        report["checks"].append("LAW-020 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        report["status"] = "fail"
        report["errors"].append("LAW-020 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     report["status"] = "fail"
                     report["errors"].append("LAW-020 execution result indicates failure.")
            report["checks"].append("LAW-020 execution result verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Result parse error: {e}")

    output_path = "outputs/audits/law020_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_law020()
    print(json.dumps(res, indent=2))
