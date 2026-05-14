import json
import os
import argparse

def validate_review_infrastructure():
    results = {
        "proof_candidate_review_infrastructure_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/proof_candidate_review_standard_registry.json",
        "registry/math/proof_candidate_rejection_criteria.json",
        "registry/math/proof_candidate_counterexample_obligation_registry.json",
        "registry/math/proof_candidate_incompleteness_handling_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["proof_candidate_review_infrastructure_validation"]["status"] = "fail"
            results["proof_candidate_review_infrastructure_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["proof_candidate_review_infrastructure_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["proof_candidate_review_infrastructure_validation"]["status"] = "fail"
                results["proof_candidate_review_infrastructure_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific field checks for review standards
    standard_reg = "registry/math/proof_candidate_review_standard_registry.json"
    if os.path.exists(standard_reg):
        with open(standard_reg, 'r') as f:
            data = json.load(f).get("proof_candidate_review_standards", {})
            required_keys = ["admissible_proof_artifact_types", "required_dependency_resolution", "required_counterexample_review"]
            for rk in required_keys:
                if rk not in data:
                     results["proof_candidate_review_infrastructure_validation"]["status"] = "fail"
                     results["proof_candidate_review_infrastructure_validation"]["errors"].append(f"Missing key {rk} in {standard_reg}")

    # Governance check: ensure no theorem/RC status changed in existing registries (Audit only check)
    # This script validates the infrastructure presence, not the targets themselves.

    return results

if __name__ == "__main__":
    res = validate_review_infrastructure()
    print(json.dumps(res, indent=2))
