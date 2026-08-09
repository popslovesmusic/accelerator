import json
import os
import argparse

def validate_law004():
    results = {
        "law004_csi_summation_finite_flux_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registry_path = "registry/math/law004_csi_summation_finite_flux_law_registry.json"
    law_doc_path = "docs/math/law004_csi_summation_finite_flux_law.md"
    result_path = "outputs/math_tests/law004_csi_summation_finite_flux_law_result.json"

    # 1. Registry check
    if not os.path.exists(registry_path):
        results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
        results["law004_csi_summation_finite_flux_law_validation"]["errors"].append("LAW-004 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f).get("law004_csi_summation_finite_flux_law", {})
                
                # Check law conditions
                conds = data.get("law_conditions", [])
                if len(conds) < 8:
                    results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
                    results["law004_csi_summation_finite_flux_law_validation"]["errors"].append(f"Insufficient law conditions: {len(conds)}/8")
                
                # Check failure modes
                fms = data.get("failure_modes_to_preserve", [])
                if len(fms) < 8:
                    results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
                    results["law004_csi_summation_finite_flux_law_validation"]["errors"].append(f"Insufficient failure modes: {len(fms)}/8")
                
                # Check candidate symbolic form presence
                if not data.get("candidate_law_statement", {}).get("symbolic_candidate"):
                     results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
                     results["law004_csi_summation_finite_flux_law_validation"]["errors"].append("Symbolic candidate missing from registry.")

                results["law004_csi_summation_finite_flux_law_validation"]["checks"].append("LAW-004 registry content verified.")
        except Exception as e:
            results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
            results["law004_csi_summation_finite_flux_law_validation"]["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(law_doc_path):
        results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
        results["law004_csi_summation_finite_flux_law_validation"]["errors"].append("LAW-004 document missing.")
    else:
        with open(law_doc_path, 'r') as f:
            content = f.read()
            required_terms = ["CSI", "beta", "finite flux", "weighting", "decay", "Pi_A"]
            for term in required_terms:
                if term not in content:
                    results["law004_csi_summation_finite_flux_law_validation"]["status"] = "warning"
                    results["law004_csi_summation_finite_flux_law_validation"]["warnings"].append(f"Term '{term}' missing from law document.")
        results["law004_csi_summation_finite_flux_law_validation"]["checks"].append("LAW-004 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
        results["law004_csi_summation_finite_flux_law_validation"]["errors"].append("LAW-004 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f).get("law004_csi_summation_finite_flux_law_result", {})
                if res.get("status") != "success":
                     results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
                     results["law004_csi_summation_finite_flux_law_validation"]["errors"].append("LAW-004 execution result indicates failure.")
            results["law004_csi_summation_finite_flux_law_validation"]["checks"].append("LAW-004 execution result verified.")
        except Exception as e:
            results["law004_csi_summation_finite_flux_law_validation"]["status"] = "fail"
            results["law004_csi_summation_finite_flux_law_validation"]["errors"].append(f"Result parse error: {e}")

    return results

if __name__ == "__main__":
    res = validate_law004()
    print(json.dumps(res, indent=2))
