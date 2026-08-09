import json
import os
import sys

def run_checks():
    manifest_path = "registry/runtime_governance_manifest.json"
    if not os.path.exists(manifest_path):
        print(f"CRITICAL ERROR: Governance manifest missing at {manifest_path}")
        sys.exit(1)

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    report = {
        "status": "PASS",
        "failures": [],
        "warnings": []
    }

    checks = manifest["required_checks"]

    # 1. JSON Parse All
    for f in checks["json_parse_all"]["files"]:
        if not os.path.exists(f):
            report["failures"].append({"check": "json_parse_all", "file": f, "level": "BLOCK", "error": "File not found"})
            continue
        try:
            with open(f, 'r', encoding='utf-8') as jf:
                json.load(jf)
        except Exception as e:
            report["failures"].append({"check": "json_parse_all", "file": f, "level": "BLOCK", "error": str(e)})

    # 2. Formal Stack Lock
    lock_file = checks["formal_stack_lock_present"]["target"]
    if not os.path.exists(lock_file):
        report["failures"].append({"check": "formal_stack_lock_present", "level": "BLOCK", "error": "PCD v1 lockfile missing"})

    # 3. Core Terms Validated (Simplified check)
    v_file = checks["core_terms_validated"]["registry"]
    if os.path.exists(v_file):
        with open(v_file, 'r', encoding='utf-8') as f:
            v_reg = json.load(f)
            core_set = v_reg.get("meta", {}).get("core_validation_set", [])
            for term in core_set:
                if term not in v_reg["terms"]:
                    report["failures"].append({"check": "core_terms_validated", "term": term, "level": "BLOCK", "error": "Missing in validation registry"})

    # Determine final status
    if any(f["level"] == "BLOCK" for f in report["failures"]):
        report["status"] = "BLOCK"
    elif any(f["level"] == "DOWNGRADE" for f in report["failures"]):
        report["status"] = "DOWNGRADE"
    elif report["warnings"] or any(f["level"] == "WARN" for f in report["failures"]):
        report["status"] = "WARN"

    return report

if __name__ == "__main__":
    result = run_checks()
    print(json.dumps(result, indent=2))
    if result["status"] == "BLOCK":
        sys.exit(1)
    sys.exit(0)
