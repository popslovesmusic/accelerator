import json
import os
import argparse

def validate_law005():
    results = {
        "law005_admissibility_boundary_transition_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registry_path = "registry/math/law005_admissibility_boundary_transition_law_registry.json"
    law_doc_path = "docs/math/law005_admissibility_boundary_transition_law.md"
    result_path = "outputs/math_tests/law005_admissibility_boundary_transition_law_result.json"

    # 1. Registry check
    if not os.path.exists(registry_path):
        results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
        results["law005_admissibility_boundary_transition_law_validation"]["errors"].append("LAW-005 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f).get("law005_admissibility_boundary_transition_law", {})
                
                # Check law conditions
                conds = data.get("law_conditions", [])
                if len(conds) < 8:
                    results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
                    results["law005_admissibility_boundary_transition_law_validation"]["errors"].append(f"Insufficient law conditions: {len(conds)}/8")
                
                # Check failure modes
                fms = data.get("failure_modes_to_preserve", [])
                if len(fms) < 8:
                    results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
                    results["law005_admissibility_boundary_transition_law_validation"]["errors"].append(f"Insufficient failure modes: {len(fms)}/8")
                
                # Check candidate symbolic form presence
                if not data.get("candidate_law_statement", {}).get("boundary_definition"):
                     results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
                     results["law005_admissibility_boundary_transition_law_validation"]["errors"].append("Boundary definition missing from registry.")

                results["law005_admissibility_boundary_transition_law_validation"]["checks"].append("LAW-005 registry content verified.")
        except Exception as e:
            results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
            results["law005_admissibility_boundary_transition_law_validation"]["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(law_doc_path):
        results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
        results["law005_admissibility_boundary_transition_law_validation"]["errors"].append("LAW-005 document missing.")
    else:
        with open(law_doc_path, 'r') as f:
            content = f.read()
            required_terms = ["partial A", "margin", "splitting", "pruning", "multi-valued", "Pi_A"]
            for term in required_terms:
                if term not in content:
                    results["law005_admissibility_boundary_transition_law_validation"]["status"] = "warning"
                    results["law005_admissibility_boundary_transition_law_validation"]["warnings"].append(f"Term '{term}' missing from law document.")
        results["law005_admissibility_boundary_transition_law_validation"]["checks"].append("LAW-005 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
        results["law005_admissibility_boundary_transition_law_validation"]["errors"].append("LAW-005 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f).get("law005_admissibility_boundary_transition_law_result", {})
                if res.get("status") != "success":
                     results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
                     results["law005_admissibility_boundary_transition_law_validation"]["errors"].append("LAW-005 execution result indicates failure.")
            results["law005_admissibility_boundary_transition_law_validation"]["checks"].append("LAW-005 execution result verified.")
        except Exception as e:
            results["law005_admissibility_boundary_transition_law_validation"]["status"] = "fail"
            results["law005_admissibility_boundary_transition_law_validation"]["errors"].append(f"Result parse error: {e}")

    return results

if __name__ == "__main__":
    res = validate_law005()
    print(json.dumps(res, indent=2))
