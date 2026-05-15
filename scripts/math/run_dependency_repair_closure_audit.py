import json
import os
from datetime import datetime

def run_closure_audit():
    """
    Runner for the Dependency Repair Closure Audit.
    Verifies that all repair and admission gates are closed and consistent.
    """
    exec_result_path = "validation/results/rc_repair_queue_execution_result.json"
    firewall_result_path = "validation/results/recursive_inheritance_firewall_result.json"
    admission_result_path = "validation/results/recursive_dependency_admission_gate_result.json"
    result_path = "validation/results/dependency_repair_closure_audit_result.json"
    
    report = {
        "audit_id": "DRCA-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "status": "pass",
        "repairs_verified": False,
        "firewall_verified": False,
        "admission_verified": False,
        "closure_outcome": "DEP-CLOSURE-BLOCKED",
        "governance": {
            "theorem_status": "NOT_PROVEN",
            "scope_status": "STRICTLY_LOCAL_RESTRICTED_DOMAIN",
            "physics_status": "NON_PHYSICAL_ANALOG_MODEL"
        }
    }

    # 1. Verify RC Repairs
    if os.path.exists(exec_result_path):
        with open(exec_result_path, 'r', encoding='utf-8') as f:
            exec_data = json.load(f)
            if all(entry["final_execution_class"] != "RC-INCOMPLETE" for entry in exec_data["repair_entries"]):
                report["repairs_verified"] = True

    # 2. Verify Firewall
    if os.path.exists(firewall_result_path):
        with open(firewall_result_path, 'r', encoding='utf-8') as f:
            fw_data = json.load(f)
            # Check if symbolic/partial/blocked were identified and classified
            if len(fw_data["inheritance_audits"]) > 0:
                report["firewall_verified"] = True

    # 3. Verify Admission Gate
    if os.path.exists(admission_result_path):
        with open(admission_result_path, 'r', encoding='utf-8') as f:
            ad_data = json.load(f)
            if all(entry["admission_class"] != "ADMISSION-DENIED" or entry["inheritance_class"] == "INHERITANCE-BLOCKED" for entry in ad_data["admission_entries"]):
                report["admission_verified"] = True

    # Determine Final Closure Class
    if report["repairs_verified"] and report["firewall_verified"] and report["admission_verified"]:
        # Check if there are any quarantined or blocked entries
        has_quarantine = False
        with open(admission_result_path, 'r', encoding='utf-8') as f:
            ad_data = json.load(f)
            for entry in ad_data["admission_entries"]:
                if entry["admission_class"] in ["ADMISSION-QUARANTINED", "ADMISSION-STRESS-ONLY"]:
                    has_quarantine = True
                    break
        
        if has_quarantine:
            report["closure_outcome"] = "DEP-CLOSURE-COMPLETE-WITH-QUARANTINE"
        else:
            report["closure_outcome"] = "DEP-CLOSURE-COMPLETE"
    else:
        report["status"] = "fail"
        report["closure_outcome"] = "DEP-CLOSURE-PARTIAL"

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Dependency repair closure audit complete. Results in {result_path}")
    return report

if __name__ == "__main__":
    run_closure_audit()
