import json
import os
from datetime import datetime

def validate_boundary_mapping():
    registry_path = "registry/math/pi_a_proof_obligation_boundary_map.json"
    doc_path = "docs/math/pi_a_proof_obligation_boundary_mapping.md"
    result_path = "validation/results/pi_a_proof_obligation_boundary_mapping_result.json"
    
    report = {
        "validation_id": "VAL-PO-BOUNDARY-MAP-001",
        "status": "pass",
        "obligations_mapped": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing boundary mapping registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing boundary mapping document")

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["obligations_mapped"] = len(registry["boundary_map"])
        
        # Check for NOT_PROVEN status
        if registry["governance"]["theorem_status"] != "NOT_PROVEN":
            report["status"] = "fail"
            report["governance_violations"].append("forbidden theorem status promotion")

        # Check for specific obligations
        expected_pos = ["PO-010-001", "PO-010-002", "PO-010-003", "PO-010-004"]
        found_pos = [entry["obligation_id"] for entry in registry["boundary_map"]]
        for po in expected_pos:
            if po not in found_pos:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mapping for obligation {po}")

    # Check doc for non-universality
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        if "not_proven" not in content or "strictly_local" not in content:
            report["status"] = "fail"
            report["governance_violations"].append("missing non-universality or local-scope declaration in document")

    # Final result
    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_boundary_mapping()
    print(json.dumps(res, indent=2))
