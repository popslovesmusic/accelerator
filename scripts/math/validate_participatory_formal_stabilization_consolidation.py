import json
import os
import subprocess
from datetime import datetime

def validate_participatory_formal_stabilization_consolidation():
    result_path = "validation/results/participatory_formal_stabilization_consolidation_result.json"
    
    report = {
        "validation_id": "VAL-PSTAB-AGGREGATE-001",
        "status": "pass",
        "sub_validators": [
            "validate_formal_stabilization_phase.py",
            "run_semantic_drift_sentinel.py",
            "validate_operator_stability_lock.py",
            "validate_law_family_stability_lock.py",
            "validate_failure_family_stability_preservation.py",
            "run_minimal_assumption_preservation_audit.py",
            "run_cross_series_consistency_audit.py",
            "validate_minimal_framework_canonicalization.py",
            "run_long_horizon_adversarial_stability_test.py"
        ],
        "results": {},
        "timestamp": datetime.now().isoformat()
    }
    
    python_exe = os.path.join(".venv", "Scripts", "python.exe")
    
    for script in report["sub_validators"]:
        script_path = os.path.join("scripts", "math", script)
        try:
            res = subprocess.run([python_exe, script_path], capture_output=True, text=True, check=True)
            script_report = json.loads(res.stdout)
            report["results"][script] = script_report["status"]
            if script_report["status"] != "pass":
                report["status"] = "fail"
        except Exception as e:
            report["status"] = "fail"
            report["results"][script] = f"error: {str(e)}"

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_participatory_formal_stabilization_consolidation()
    print(json.dumps(res, indent=2))
