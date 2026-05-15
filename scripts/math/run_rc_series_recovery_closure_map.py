import json
import os
from datetime import datetime

def run_recovery_map():
    """
    Inventory and classify RC001-RC031.
    """
    registry_path = "registry/math/rc_series_recovery_closure_map_registry.json"
    result_path = "validation/results/rc_series_recovery_closure_map_result.json"
    
    # Define RC range
    rc_ids = [f"RC{str(i).zfill(3)}" for i in range(1, 32)]
    
    report = {
        "audit_id": "MPF-DEP-002",
        "timestamp": datetime.now().isoformat(),
        "rc_entries": [],
        "summary": {
            "clear_count": 0,
            "partial_count": 0,
            "symbolic_count": 0,
            "blocked_count": 0,
            "requires_simulation_count": 0,
            "requires_reconciliation_count": 0
        },
        "governance": {
            "theorem_status": "NOT_PROVEN",
            "scope_status": "STRICTLY_LOCAL_RESTRICTED_DOMAIN",
            "physics_status": "NON_PHYSICAL_ANALOG_MODEL"
        }
    }

    for rc_id in rc_ids:
        entry = {
            "rc_id": rc_id,
            "artifact_presence": {
                "registry": "missing",
                "doc": "missing",
                "validator": "missing",
                "result": "missing"
            },
            "closure_class": "RC-INCOMPLETE",
            "required_next_action": "Audit missing artifacts."
        }
        
        # 1. Check Registry
        # Look for files starting with rcXXX or containing rcXXX in registry/math
        found_reg = False
        for f in os.listdir("registry/math/"):
            if rc_id.lower() in f.lower() and f.endswith(".json"):
                entry["artifact_presence"]["registry"] = "present"
                found_reg = True
                break
        
        # 2. Check Doc
        # (Docs are often summarized in volumes, but we check for individual md files as well)
        for f in os.listdir("docs/math/"):
            if rc_id.lower() in f.lower() and f.endswith(".md"):
                entry["artifact_presence"]["doc"] = "present"
                break
        
        # 3. Check Validator
        for f in os.listdir("scripts/math/"):
            if "validate_" + rc_id.lower() in f.lower() and f.endswith(".py"):
                entry["artifact_presence"]["validator"] = "present"
                break

        # 4. Check Result
        for f in os.listdir("validation/results/"):
             if rc_id.lower() in f.lower() and f.endswith(".json"):
                 entry["artifact_presence"]["result"] = "present"
                 break

        # Classification Logic (Simplified)
        if entry["artifact_presence"]["registry"] == "present":
            if entry["artifact_presence"]["validator"] == "present" and entry["artifact_presence"]["result"] == "present":
                 entry["closure_class"] = "RC-CLEAR"
                 report["summary"]["clear_count"] += 1
                 entry["required_next_action"] = "None"
            else:
                 entry["closure_class"] = "RC-PARTIAL"
                 report["summary"]["partial_count"] += 1
                 entry["required_next_action"] = "Complete validator/result stack."
        else:
            entry["closure_class"] = "RC-SYMBOLIC"
            report["summary"]["symbolic_count"] += 1
            entry["required_next_action"] = "Create formal registry."

        report["rc_entries"].append(entry)

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"RC Series Recovery Map complete. Results in {result_path}")
    return report

if __name__ == "__main__":
    run_recovery_map()
