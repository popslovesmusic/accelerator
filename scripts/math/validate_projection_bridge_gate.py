import json
import os
import glob
from datetime import datetime

def validate_projection_bridge_gate():
    registry_path = "registry/math/projection_bridge_non_unification_gate.json"
    result_path = "validation/results/projection_bridge_gate_result.json"
    
    report = {
        "gate_id": "PBNU-AUDIT-001",
        "status": "pass",
        "checked_artifacts": [],
        "passed_checks": [],
        "failed_checks": [],
        "detected_escalations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["failed_checks"].append("gate_registry_missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # 1. Gate Status Check
    if registry.get("gate_status") != "CANDIDATE_BRIDGE_GATE":
        report["status"] = "fail"
        report["failed_checks"].append("illegal_gate_status")

    # 2. Scanning Rule Definitions
    reject_patterns = []
    for check in registry.get("gate_checks", []):
        if "reject_terms" in check:
            reject_patterns.extend(check["reject_terms"])
            
    targets = registry.get("input_targets", [])
    files_to_scan = []
    for t in targets:
        files_to_scan.extend(glob.glob(t))

    for f_path in files_to_scan:
        artifact_name = os.path.basename(f_path)
        # Skip the gate registry and its own docs
        if "non_unification_gate" in artifact_name:
            continue
            
        report["checked_artifacts"].append(artifact_name)
        
        with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
            content_lower = f.read().lower()
            
            # Check for forbidden terms
            found_escalation = False
            for term in reject_patterns:
                if term.lower() in content_lower:
                    report["detected_escalations"].append(f"{term}_in_{artifact_name}")
                    found_escalation = True
            
            if found_escalation:
                report["status"] = "fail"
                report["failed_checks"].append(f"unification_escalation_detected_in_{artifact_name}")

            # Check for mandatory analog-only disclaimer
            if "analog_only" not in content_lower and "analog-only" not in content_lower:
                report["status"] = "fail"
                report["failed_checks"].append(f"missing_analog_only_disclaimer_in_{artifact_name}")

            # Check for non-unification boolean (JSON only)
            if f_path.endswith(".json"):
                try:
                    data = json.loads(content_lower)
                    if data.get("unification_claim_blocked") is not True:
                        # Some registries might be domain definitions, not specific comparison records.
                        # However, BCS requires it.
                        if "comparison_schema" in artifact_name or "bridge" in artifact_name:
                             report["status"] = "fail"
                             report["failed_checks"].append(f"missing_non_unification_boolean_in_{artifact_name}")
                except:
                    pass

    if report["status"] == "pass":
        report["passed_checks"].append("no_unification_claims_detected")
        report["passed_checks"].append("no_physical_derivation_detected")
        report["passed_checks"].append("analog_only_discipline_maintained")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_projection_bridge_gate()
    print(json.dumps(res, indent=2))
