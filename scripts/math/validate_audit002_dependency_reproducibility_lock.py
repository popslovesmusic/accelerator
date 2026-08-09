import json
import os
import sys

def validate_reproducibility():
    registry_path = "registry/math/audit002_dependency_reproducibility_lock_registry.json"
    lockfile_path = "requirements.lock.txt"
    policy_path = "docs/math/dependency_reproducibility_policy.md"
    
    report = {
        "status": "pass",
        "checks": {},
        "errors": []
    }
    
    # Check registry existence
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append(f"Registry missing: {registry_path}")
        report["checks"]["registry_exists"] = "fail"
    else:
        report["checks"]["registry_exists"] = "pass"
        with open(registry_path, "r") as f:
            registry = json.load(f)
            report["checks"]["id_match"] = registry.get("id") == "AUDIT-002"

    # Check lockfile existence
    if not os.path.exists(lockfile_path):
        report["status"] = "fail"
        report["errors"].append(f"Lockfile missing: {lockfile_path}")
        report["checks"]["lockfile_exists"] = "fail"
    else:
        report["checks"]["lockfile_exists"] = "pass"
        try:
            with open(lockfile_path, "r", encoding="utf-8-sig") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(lockfile_path, "r", encoding="utf-16") as f:
                content = f.read()
        
        # Verify some core dependencies are pinned
        pinned_found = 0
        for dep in ["numpy", "pandas", "scipy", "networkx", "pytest"]:
            if f"{dep}==" in content.lower():
                pinned_found += 1
        report["checks"]["pinned_dependencies_count"] = pinned_found
        if pinned_found < 3:
             report["status"] = "fail"
             report["errors"].append(f"Fewer than 3 core dependencies found pinned in lockfile (found {pinned_found})")

    # Check policy existence
    if not os.path.exists(policy_path):
        report["status"] = "fail"
        report["errors"].append(f"Policy document missing: {policy_path}")
        report["checks"]["policy_exists"] = "fail"
    else:
        report["checks"]["policy_exists"] = "pass"
        with open(policy_path, "r") as f:
            content = f.read()
            if "implementation_verified" in content and "requirements.lock.txt" in content:
                report["checks"]["policy_content_verified"] = "pass"
            else:
                report["checks"]["policy_content_verified"] = "fail"
                report["errors"].append("Policy document lacks required blocking rules or artifact references")

    output_path = "outputs/audits/math_program_validation_after_audit002_dependency_reproducibility_lock.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"audit002_dependency_reproducibility_lock_validation": report}, f, indent=2)
    
    print(json.dumps({"audit002_dependency_reproducibility_lock_validation": report}, indent=2))
    return 0 if report["status"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(validate_reproducibility())
