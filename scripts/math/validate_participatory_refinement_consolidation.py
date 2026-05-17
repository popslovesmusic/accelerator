import json
import os
import subprocess
from datetime import datetime

def validate_participatory_refinement_consolidation():
    result_path = "validation/results/participatory_refinement_consolidation_result.json"
    
    report = {
        "validation_id": "VAL-PAR-AGGREGATE-001",
        "status": "pass",
        "sub_validators": [
            "validate_participatory_refinement_phase.py",
            "run_operator_necessity_audit.py",
            "run_semantic_redundancy_compression.py",
            "run_process_relation_language_refinement.py",
            "run_admissibility_compression_mapping.py",
            "run_failure_class_structural_compression.py",
            "run_interpretive_stability_audit.py",
            "validate_framework_compression_synthesis.py",
            "run_post_compression_adversarial_audit.py"
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
    res = validate_participatory_refinement_consolidation()
    print(json.dumps(res, indent=2))
