import json
import os
import argparse
import subprocess
import sys
import tempfile


def _run_json_command(cmd):
    with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".json", delete=False) as stdout_tmp:
        stdout_path = stdout_tmp.name
    try:
        with open(stdout_path, "w", encoding="utf-8") as stdout_handle:
            result = subprocess.run(cmd, stdout=stdout_handle, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return {"status": "fail", "errors": [f"Script crashed: {result.stderr}"]}
        with open(stdout_path, "r", encoding="utf-8") as stdout_handle:
            return json.load(stdout_handle)
    finally:
        if os.path.exists(stdout_path):
            os.remove(stdout_path)

def run_validator(script_name):
    script_path = os.path.join("scripts/math", script_name)
    if not os.path.exists(script_path):
        return {"status": "fail", "errors": [f"Validator script missing: {script_name}"]}
    
    try:
        cmd = [sys.executable, script_path]
        return _run_json_command(cmd)
    except Exception as e:
        return {"status": "fail", "errors": [str(e)]}

def validate_rc002_readiness():
    results = {
        "rc002_proof_candidate_review_ready_validation": {
            "status": "pass",
            "foundations_checked": [],
            "warnings": [],
            "errors": []
        }
    }

    criteria_path = "registry/math/rc002_proof_candidate_readiness_criteria.json"
    supported_path = "registry/math/rc002_derivation_supported_registry.json"

    try:
        with open(criteria_path, 'r') as f: criteria = json.load(f).get("readiness_criteria", {})
        with open(supported_path, 'r') as f: supported = json.load(f).get("rc002_derivation_supported", {})
    except Exception as e:
        results["rc002_proof_candidate_review_ready_validation"]["status"] = "fail"
        results["rc002_proof_candidate_review_ready_validation"]["errors"].append(f"Load error: {e}")
        return results

    if supported.get("status") != "derivation_supported":
        results["rc002_proof_candidate_review_ready_validation"]["status"] = "fail"
        results["rc002_proof_candidate_review_ready_validation"]["errors"].append("RC-002 status is not derivation_supported.")

    for foundation in criteria.get("required_foundations", []):
        f_id = foundation["id"]
        f_desc = foundation["description"]
        v_script = foundation["validation_script"]
        
        res = run_validator(v_script)
        
        # Check if the validator passed
        # Validators usually return a dict where one key ends in _validation
        sub_key = next((k for k in res.keys() if "_validation" in k), None)
        v_res = res[sub_key] if sub_key else res
        
        found_status = v_res.get("status", "fail")
        results["rc002_proof_candidate_review_ready_validation"]["foundations_checked"].append({
            "id": f_id,
            "description": f_desc,
            "status": found_status
        })

        if found_status == "fail":
            results["rc002_proof_candidate_review_ready_validation"]["status"] = "fail"
            results["rc002_proof_candidate_review_ready_validation"]["errors"].append(f"Foundation {f_id} ({f_desc}) failed validation.")

    return results

if __name__ == "__main__":
    res = validate_rc002_readiness()
    print(json.dumps(res, indent=2))
