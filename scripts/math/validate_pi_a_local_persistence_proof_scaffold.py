import json
import os
from datetime import datetime

def validate_scaffold():
    registry_path = "registry/math/pi_a_local_persistence_proof_scaffold_registry.json"
    doc_path = "docs/math/pi_a_local_idempotent_persistence_proof_scaffold.md"
    result_path = "validation/results/pi_a_local_persistence_proof_scaffold_result.json"
    
    report = {
        "validation_id": "VAL-LTC-SCAFFOLD-001",
        "status": "pass",
        "proof_obligations_open": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing proof scaffold registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing proof scaffold document")

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        
        # Check for NOT_PROVEN status
        if registry["governance"]["theorem_status"] != "NOT_PROVEN":
            report["status"] = "fail"
            report["governance_violations"].append("forbidden theorem status promotion")

        # Check for open proof obligations
        for po in registry["proof_obligations"]:
            if po["status"] == "OPEN":
                report["proof_obligations_open"] += 1
            else:
                 report["status"] = "fail"
                 report["governance_violations"].append(f"proof obligation {po['id']} is not OPEN")

        # Check for mandatory dependencies
        deps = registry["law_dependencies"]
        if "MT-001" not in deps or "LAW002" not in deps or "MT-LAW-A" not in deps:
            report["status"] = "fail"
            report["governance_violations"].append("missing core law dependencies (MT-001, LAW002, or MT-LAW-A)")

    # Check for forbidden claims in doc
    forbidden_claims = ["proven", "global closure", "physical stability"]
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        if "status**: **proven**" in content:
             report["status"] = "fail"
             report["governance_violations"].append("forbidden 'proven' status in document")

    # Final result
    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_scaffold()
    print(json.dumps(res, indent=2))
