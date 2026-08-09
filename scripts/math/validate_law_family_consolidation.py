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
            subprocess.run([python_exe, script_path], stdout=stdout_handle, stderr=subprocess.PIPE, text=True, check=True)
        with open(stdout_path, "r", encoding="utf-8") as stdout_handle:
            return json.load(stdout_handle)
    finally:
        if os.path.exists(stdout_path):
            os.remove(stdout_path)

def validate_law_family_consolidation():
    result_path = "validation/results/law_family_consolidation_result.json"
    
    report = {
        "validation_id": "VAL-LAW-CONS-AGGREGATE-001",
        "status": "pass",
        "sub_validators": [
            "validate_law_consolidation_phase.py",
            "validate_law_inventory_redundancy.py",
            "validate_law_family_registry.py",
            "validate_law_supersession_trace.py",
            "validate_law_category_reclassification.py",
            "validate_law_family_dependency_graph.py",
            "validate_law_family_counterexample_preservation.py",
            "validate_law_family_readability.py"
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
    res = validate_law_family_consolidation()
    print(json.dumps(res, indent=2))
