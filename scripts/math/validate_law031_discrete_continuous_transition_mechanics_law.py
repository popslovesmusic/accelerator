import json
import os

def validate_law031():
    results = {
        "law031_discrete_continuous_transition_mechanics_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["law031_discrete_continuous_transition_mechanics_law_validation"]
    
    registry_path = "registry/math/law031_discrete_continuous_transition_mechanics_law_registry.json"
    doc_path = "docs/math/law031_discrete_continuous_transition_mechanics_law.md"
    result_path = "outputs/math_tests/law031_discrete_continuous_transition_mechanics_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("LAW-031 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "continuous_gradient_candidate_explicit",
                    "threshold_candidate_explicit",
                    "discrete_event_candidate_explicit",
                    "threshold_crossing_condition_explicit",
                    "stabilization_quantization_candidate_explicit",
                    "continuity_preservation_clause_explicit",
                    "nonphysical_discreteness_clause_explicit"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                report["checks"].append("LAW-031 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("LAW-031 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "continuous gradient", "threshold candidate",
                "discrete event", "threshold crossing condition",
                "stabilization quantization", "continuity preservation",
                "non-physical discreteness", "no physics claim",
                "no physical quantization", "no quantum mechanics recovery"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Term '{term}' missing from law document.")
        report["checks"].append("LAW-031 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        report["status"] = "fail"
        report["errors"].append("LAW-031 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     report["status"] = "fail"
                     report["errors"].append("LAW-031 execution result indicates failure.")
            report["checks"].append("LAW-031 execution result verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Result parse error: {e}")

    output_path = "outputs/audits/law031_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_law031()
    print(json.dumps(res, indent=2))
