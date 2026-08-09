import json
import os

def validate_law032():
    results = {
        "law032_recursive_failure_mode_taxonomy_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["law032_recursive_failure_mode_taxonomy_law_validation"]
    
    registry_path = "registry/math/law032_recursive_failure_mode_taxonomy_law_registry.json"
    doc_path = "docs/math/law032_recursive_failure_mode_taxonomy_law.md"
    result_path = "outputs/math_tests/law032_recursive_failure_mode_taxonomy_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("LAW-032 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "failure_mode_family_explicit",
                    "runaway_condition_explicit",
                    "deadlock_condition_explicit",
                    "fragmentation_condition_explicit",
                    "reinforcement_lock_condition_explicit",
                    "admissibility_collapse_condition_explicit",
                    "cascade_condition_explicit",
                    "reconstruction_failure_condition_explicit"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                report["checks"].append("LAW-032 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("LAW-032 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "failure mode family", "runaway condition",
                "deadlock condition", "fragmentation condition",
                "reinforcement lock", "admissibility collapse",
                "cascade condition", "reconstruction failure",
                "no physics claim", "no false stability",
                "no perfect stability", "no universal catastrophe theory"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Term '{term}' missing from law document.")
        report["checks"].append("LAW-032 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        report["status"] = "fail"
        report["errors"].append("LAW-032 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     report["status"] = "fail"
                     report["errors"].append("LAW-032 execution result indicates failure.")
            report["checks"].append("LAW-032 execution result verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Result parse error: {e}")

    output_path = "outputs/audits/law032_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_law032()
    print(json.dumps(res, indent=2))
