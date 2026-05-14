import json
import os

def validate_law029():
    results = {
        "law029_recursive_arbitration_conflict_resolution_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["law029_recursive_arbitration_conflict_resolution_law_validation"]
    
    registry_path = "registry/math/law029_recursive_arbitration_conflict_resolution_law_registry.json"
    doc_path = "docs/math/law029_recursive_arbitration_conflict_resolution_law.md"
    result_path = "outputs/math_tests/law029_recursive_arbitration_conflict_resolution_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("LAW-029 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "candidate_set_definition_explicit",
                    "arbitration_operator_candidate_explicit",
                    "conflict_condition_explicit",
                    "priority_score_candidate_explicit",
                    "tie_resolution_condition_explicit",
                    "nonunique_arbitration_clause_explicit",
                    "recursive_feedback_clause_explicit"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                report["checks"].append("LAW-029 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("LAW-029 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "candidate set", "arbitration operator",
                "conflict condition", "priority score", "tie-resolution",
                "non-unique arbitration", "recursive feedback",
                "no physics claim", "no deterministic selection",
                "no global optimality"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Term '{term}' missing from law document.")
        report["checks"].append("LAW-029 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        report["status"] = "fail"
        report["errors"].append("LAW-029 execution result missing.")
    else:
        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     report["status"] = "fail"
                     report["errors"].append("LAW-029 execution result indicates failure.")
            report["checks"].append("LAW-029 execution result verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Result parse error: {e}")

    output_path = "outputs/audits/law029_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_law029()
    print(json.dumps(res, indent=2))
