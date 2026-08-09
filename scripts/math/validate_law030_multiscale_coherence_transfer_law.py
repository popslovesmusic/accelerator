import json
import os

def validate_law030():
    results = {
        "law030_multiscale_coherence_transfer_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["law030_multiscale_coherence_transfer_law_validation"]
    
    registry_path = "registry/math/law030_multiscale_coherence_transfer_law_registry.json"
    doc_path = "docs/math/law030_multiscale_coherence_transfer_law.md"
    result_path = "outputs/math_tests/law030_multiscale_coherence_transfer_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("LAW-030 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "scale_like_layer_candidate_explicit",
                    "coherence_metric_candidate_explicit",
                    "upward_transfer_condition_explicit",
                    "downward_constraint_condition_explicit",
                    "scale_decoupling_condition_explicit",
                    "nonprimitive_scale_clause_explicit",
                    "global_synchronization_claim_blocked"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                report["checks"].append("LAW-030 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("LAW-030 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "scale-like layer", "coherence metric",
                "upward transfer", "downward constraint", "scale decoupling",
                "non-primitive scale", "global synchronization",
                "no physics claim", "no physical scale equivalence",
                "no primitive scale hierarchy"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Term '{term}' missing from law document.")
        report["checks"].append("LAW-030 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        report["status"] = "fail"
        report["errors"].append("LAW-030 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     report["status"] = "fail"
                     report["errors"].append("LAW-030 execution result indicates failure.")
            report["checks"].append("LAW-030 execution result verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Result parse error: {e}")

    output_path = "outputs/audits/law030_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_law030()
    print(json.dumps(res, indent=2))
