import json
import os
import argparse

def validate_hidden_discovery():
    results = {
        "hidden_proof_blocker_discovery_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/hidden_proof_blocker_discovery_registry.json",
        "registry/math/hidden_incompleteness_candidate_registry.json",
        "registry/math/unclassified_blocker_risk_registry.json",
        "registry/math/hidden_counterexample_obligation_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["hidden_proof_blocker_discovery_validation"]["status"] = "fail"
            results["hidden_proof_blocker_discovery_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["hidden_proof_blocker_discovery_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["hidden_proof_blocker_discovery_validation"]["status"] = "fail"
                results["hidden_proof_blocker_discovery_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: address the sparse blocker warning
    discovery_reg = "registry/math/hidden_proof_blocker_discovery_registry.json"
    if os.path.exists(discovery_reg):
        with open(discovery_reg, 'r') as f:
            logs = json.load(f).get("hidden_proof_blocker_discovery", {}).get("discovery_log", [])
            if len(logs) >= 5:
                results["hidden_proof_blocker_discovery_validation"]["checks"].append("Hidden blocker discovery log has sufficient entries to address sparse warning.")
            else:
                 results["hidden_proof_blocker_discovery_validation"]["status"] = "warning"
                 results["hidden_proof_blocker_discovery_validation"]["warnings"].append("Discovery log still relatively sparse.")

    return results

if __name__ == "__main__":
    res = validate_hidden_discovery()
    print(json.dumps(res, indent=2))
