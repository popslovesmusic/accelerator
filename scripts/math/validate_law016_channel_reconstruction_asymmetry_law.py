import json
import os

def validate_law016():
    results = {
        "law016_channel_reconstruction_asymmetry_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    registry_path = "registry/math/law016_channel_reconstruction_asymmetry_law_registry.json"
    doc_path = "docs/math/law016_channel_reconstruction_asymmetry_law.md"
    result_path = "outputs/math_tests/law016_channel_reconstruction_asymmetry_law_result.json"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "fail"
        results["law016_channel_reconstruction_asymmetry_law_validation"]["errors"].append("LAW-016 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                conditions = data.get("law_conditions", [])
                required_conditions = [
                    "orientation_array_dependency_explicit",
                    "channel_dependency_explicit",
                    "reconstruction_candidate_explicit",
                    "asymmetry_condition_explicit",
                    "loss_accumulation_condition_explicit",
                    "nonunique_prehistory_clause_explicit",
                    "irreversibility_projection_clause_explicit",
                    "no_entropy_equivalence_claim"
                ]
                for cond in required_conditions:
                    if cond not in conditions:
                        results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "fail"
                        results["law016_channel_reconstruction_asymmetry_law_validation"]["errors"].append(f"Missing law condition: {cond}")
                
                failure_modes = data.get("failure_modes_to_preserve", [])
                if len(failure_modes) < 8:
                    results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "fail"
                    results["law016_channel_reconstruction_asymmetry_law_validation"]["errors"].append(f"Insufficient failure modes: {len(failure_modes)}/8")
                
                results["law016_channel_reconstruction_asymmetry_law_validation"]["checks"].append("LAW-016 registry content verified.")
        except Exception as e:
            results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "fail"
            results["law016_channel_reconstruction_asymmetry_law_validation"]["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(doc_path):
        results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "fail"
        results["law016_channel_reconstruction_asymmetry_law_validation"]["errors"].append("LAW-016 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "reconstruction candidate", "asymmetry condition",
                "loss accumulation condition", "non-unique prehistory clause",
                "irreversibility projection clause", "no entropy equivalence", "no physics claim"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "warning"
                    results["law016_channel_reconstruction_asymmetry_law_validation"]["warnings"].append(f"Term '{term}' missing from law document.")
        results["law016_channel_reconstruction_asymmetry_law_validation"]["checks"].append("LAW-016 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "fail"
        results["law016_channel_reconstruction_asymmetry_law_validation"]["errors"].append("LAW-016 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f)
                if res.get("status") != "simulated_pass":
                     results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "fail"
                     results["law016_channel_reconstruction_asymmetry_law_validation"]["errors"].append("LAW-016 execution result indicates failure.")
            results["law016_channel_reconstruction_asymmetry_law_validation"]["checks"].append("LAW-016 execution result verified.")
        except Exception as e:
            results["law016_channel_reconstruction_asymmetry_law_validation"]["status"] = "fail"
            results["law016_channel_reconstruction_asymmetry_law_validation"]["errors"].append(f"Result parse error: {e}")

    return results

if __name__ == "__main__":
    res = validate_law016()
    print(json.dumps(res, indent=2))
