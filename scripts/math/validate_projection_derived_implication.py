import json
import os
from datetime import datetime

def validate_projection_derived_implication():
    registry_path = "registry/math/projection_derived_implication_registry.json"
    result_path = "validation/results/projection_derived_implication_result.json"
    
    report = {
        "validation_id": "VAL-PDI-VALID-001",
        "status": "pass",
        "examples_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("projection registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Projection Status Check
    if registry.get("projection_status") != "CANDIDATE_PROJECTION":
        report["status"] = "fail"
        report["governance_violations"].append("illegal projection status in registry")
    
    # 2. Core Rule Check
    definition = registry.get("projection_definition", {})
    if "⇔R" not in definition.get("source_relation", ""):
        report["status"] = "fail"
        report["governance_violations"].append("source_relation must use ⇔R")
    
    if "Π_imply" not in definition.get("projection_form", ""):
        report["status"] = "fail"
        report["governance_violations"].append("missing mandatory projection form")

    # 3. Loss Accounting Check
    loss = registry.get("loss_accounting", {})
    required_losses = ["co-presence", "mutuality", "residue-history"]
    lost_features = " ".join(loss.get("lost_or_abstracted_features", [])).lower()
    for rl in required_losses:
        if rl not in lost_features:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing mandatory loss accounting for: {rl}")

    # 4. Forbidden Claims Check
    forbidden = registry.get("forbidden_uses", [])
    if not any("physical causation" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden physical causation check")
    if not any("transitivity automatically" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden automatic transitivity check")

    # 5. Schema Check
    if not registry.get("implication_projection_schema"):
        report["status"] = "fail"
        report["governance_violations"].append("missing implication projection schema")

    # 6. Governance Status Invariants
    gov = registry.get("governance_status", {})
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_projection_derived_implication()
    print(json.dumps(res, indent=2))
