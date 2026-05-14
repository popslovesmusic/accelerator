import json
import os

def validate_law028():
    results = {
        "law028_topological_invariants_under_continuation_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["law028_topological_invariants_under_continuation_law_validation"]
    
    registry_path = "registry/math/law028_topological_invariants_under_continuation_law_registry.json"
    doc_path = "docs/math/law028_topological_invariants_under_continuation_law.md"
    result_path = "outputs/math_tests/law028_topological_invariants_under_continuation_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("LAW-028 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "invariant_candidate_family_explicit",
                    "persistence_invariant_candidate_explicit",
                    "accessibility_invariant_candidate_explicit",
                    "reinforcement_invariant_candidate_explicit",
                    "reconstruction_invariant_candidate_explicit",
                    "invariant_failure_condition_explicit",
                    "non_global_invariant_clause_explicit"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                report["checks"].append("LAW-028 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("LAW-028 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "invariant candidate family", "persistence invariant",
                "accessibility invariant", "reinforcement invariant",
                "reconstruction invariant", "invariant failure condition",
                "no physics claim", "no global conservation",
                "no universal invariance"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Term '{term}' missing from law document.")
        report["checks"].append("LAW-028 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        report["status"] = "fail"
        report["errors"].append("LAW-028 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     report["status"] = "fail"
                     report["errors"].append("LAW-028 execution result indicates failure.")
            report["checks"].append("LAW-028 execution result verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Result parse error: {e}")

    output_path = "outputs/audits/law028_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_law028()
    print(json.dumps(res, indent=2))
