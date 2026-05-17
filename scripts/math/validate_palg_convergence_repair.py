import json
import os
from datetime import datetime

def validate_palg_convergence_repair():
    result_path = "validation/results/palg_convergence_repair_result.json"
    
    report = {
        "validation_id": "VAL-CONV-REPAIR-001",
        "status": "pass",
        "checks_passed": [],
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Check Operator Disambiguation
    registry_path = "registry/math/operator_registry.json"
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            ops = [o.get("symbol") for o in registry.get("operators", [])]
            if "Delta" in ops:
                report["status"] = "fail"
                report["governance_violations"].append("operator_disambiguation_Delta_remains: FAIL")
            elif "Transition_Operator" not in ops:
                report["status"] = "fail"
                report["governance_violations"].append("operator_disambiguation_Transition_Operator_missing: FAIL")
            else:
                report["checks_passed"].append("operator_disambiguation")
    else:
        report["status"] = "fail"
        report["governance_violations"].append("operator_registry_missing: FAIL")

    # 2. Check Reduction Gaps
    gap_path = "registry/math/reduction_gap_registry.json"
    if os.path.exists(gap_path):
        with open(gap_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            gaps = registry.get("gaps", [])
            all_have_status = all("status" in g for g in gaps)
            if not all_have_status:
                report["status"] = "fail"
                report["governance_violations"].append("reduction_gap_status_missing: FAIL")
            else:
                report["checks_passed"].append("reduction_gap_status_initialization")
    else:
        report["status"] = "fail"
        report["governance_violations"].append("reduction_gap_registry_missing: FAIL")

    # 3. Check Bridge Artifact Hardening
    # Spot check a few critical ones
    bridge_checks = [
        "registry/math/bridge_metrics_phase_declaration.json",
        "registry/math/bridge_comparison_schema.json"
    ]
    for path in bridge_checks:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                if registry.get("source_relation") != "(E≠0) ⇔R δ(E>0)":
                    report["status"] = "fail"
                    report["governance_violations"].append(f"bridge_hardening_source_relation_{os.path.basename(path)}: FAIL")
                if registry.get("non_separability_acknowledged") is not True:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"bridge_hardening_non_separability_{os.path.basename(path)}: FAIL")
                if "no_unification_guardrail" not in registry:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"bridge_hardening_guardrail_missing_{os.path.basename(path)}: FAIL")
                else:
                    report["checks_passed"].append(f"bridge_hardening_{os.path.basename(path)}")
        else:
            report["status"] = "fail"
            report["governance_violations"].append(f"bridge_artifact_missing_{os.path.basename(path)}: FAIL")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_palg_convergence_repair()
    print(json.dumps(res, indent=2))
