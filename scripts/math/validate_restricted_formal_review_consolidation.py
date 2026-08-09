import json
import os
import subprocess
import tempfile
from datetime import datetime


def _run_json_validator(python_exe, script_path):
    with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".json", delete=False) as stdout_tmp:
        stdout_path = stdout_tmp.name
    try:
        with open(stdout_path, "w", encoding="utf-8") as stdout_handle:
            res = subprocess.run([python_exe, script_path], stdout=stdout_handle, stderr=subprocess.PIPE, text=True, check=True)
        with open(stdout_path, "r", encoding="utf-8") as stdout_handle:
            return json.load(stdout_handle)
    finally:
        if os.path.exists(stdout_path):
            os.remove(stdout_path)

def validate_restricted_formal_review_consolidation():
    result_path = "validation/results/restricted_formal_review_consolidation_result.json"
    
    report = {
        "validation_id": "VAL-RFPR-AGGREGATE-001",
        "status": "pass",
        "sub_validators": [
            "validate_restricted_formal_review_phase.py",
            "validate_formal_theorem_statements.py",
            "validate_proof_presentation_normalization.py",
            "validate_mt001_formal_review_package.py",
            "validate_mt002_formal_review_package.py",
            "validate_mt003_formal_review_package.py",
            "validate_counterexample_disclosure.py",
            "validate_review_readability_traceability.py",
            "run_external_review_stress_tests.py"
        ],
        "results": {},
        "timestamp": datetime.now().isoformat()
    }
    
    python_exe = os.path.join(".venv", "Scripts", "python.exe")
    
    for script in report["sub_validators"]:
        script_path = os.path.join("scripts", "math", script)
        try:
            script_report = _run_json_validator(python_exe, script_path)
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
    res = validate_restricted_formal_review_consolidation()
    print(json.dumps(res, indent=2))
