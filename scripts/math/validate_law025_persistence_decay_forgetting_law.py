import json
import os

def validate_law025():
    results = {
        "law025_persistence_decay_forgetting_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["law025_persistence_decay_forgetting_law_validation"]
    
    registry_path = "registry/math/law025_persistence_decay_forgetting_law_registry.json"
    doc_path = "docs/math/law025_persistence_decay_forgetting_law.md"
    result_path = "outputs/math_tests/law025_persistence_decay_forgetting_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("LAW-025 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "decay_operator_candidate_explicit",
                    "reinforcement_erosion_condition_explicit",
                    "forgetting_condition_explicit",
                    "basin_weakening_condition_explicit",
                    "transient_lawlike_clause_explicit",
                    "nonprimitive_memory_clause_explicit",
                    "eternal_accumulation_blocked"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                report["checks"].append("LAW-025 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("LAW-025 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "decay operator", "reinforcement erosion",
                "forgetting condition", "basin weakening", "transient law-like",
                "non-primitive memory", "no physics claim", "no entropy equivalence",
                "no psychological memory theory"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Term '{term}' missing from law document.")
        report["checks"].append("LAW-025 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        report["status"] = "fail"
        report["errors"].append("LAW-025 execution result missing.")
    else:
        try:
            with open(result_path, 'r', encoding='utf-8') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     report["status"] = "fail"
                     report["errors"].append("LAW-025 execution result indicates failure.")
            report["checks"].append("LAW-025 execution result verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Result parse error: {e}")

    output_path = "outputs/audits/law025_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_law025()
    print(json.dumps(res, indent=2))
