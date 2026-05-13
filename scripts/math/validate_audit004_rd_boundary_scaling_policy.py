import json
import os
import sys

def validate_rd_policy():
    registry_path = "registry/math/audit004_rd_boundary_scaling_policy_registry.json"
    policy_path = "docs/math/rd_boundary_scaling_policy.md"
    test_path = "tests/test_rd_boundary_scaling_policy.py"
    engine_path = "tools/rd_moving_boundary_sim_v1/rd_engine.py"
    
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
            report["checks"]["id_match"] = registry.get("id") == "AUDIT-004"

    # Check policy existence
    if not os.path.exists(policy_path):
        report["status"] = "fail"
        report["errors"].append(f"Policy document missing: {policy_path}")
        report["checks"]["policy_exists"] = "fail"
    else:
        report["checks"]["policy_exists"] = "pass"
        with open(policy_path, "r") as f:
            content = f.read()
            if "Default Mode" in content and "periodic" in content and "Default Scaling" in content and "Unit-grid spacing" in content:
                report["checks"]["policy_content_verified"] = "pass"
            else:
                report["checks"]["policy_content_verified"] = "fail"
                report["errors"].append("Policy document lacks required parameters or sections")

    # Check test existence
    if not os.path.exists(test_path):
        report["status"] = "fail"
        report["errors"].append(f"Regression test missing: {test_path}")
        report["checks"]["regression_test_exists"] = "fail"
    else:
        report["checks"]["regression_test_exists"] = "pass"

    # Check engine implementation
    if not os.path.exists(engine_path):
        report["status"] = "fail"
        report["errors"].append(f"Engine file missing: {engine_path}")
        report["checks"]["engine_exists"] = "fail"
    else:
        report["checks"]["engine_exists"] = "pass"
        with open(engine_path, "r") as f:
            content = f.read()
            if "boundary_mode" in content and "dx" in content and "dy" in content:
                report["checks"]["convention_fields_detected"] = "pass"
            else:
                report["status"] = "fail"
                report["checks"]["convention_fields_detected"] = "fail"
                report["errors"].append("Boundary or scaling fields not detected in rd_engine.py")

    output_path = "outputs/audits/math_program_validation_after_audit004_rd_boundary_scaling_policy.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"audit004_rd_boundary_scaling_policy_validation": report}, f, indent=2)
    
    print(json.dumps({"audit004_rd_boundary_scaling_policy_validation": report}, indent=2))
    return 0 if report["status"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(validate_rd_policy())
