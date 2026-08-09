import json
import os
import sys

def validate_euler_stability():
    registry_path = "registry/math/audit006_structural_euler_stability_bounds_registry.json"
    policy_path = "docs/math/structural_box_euler_stability_policy.md"
    test_path = "tests/test_structural_box_euler_stability_bounds.py"
    sim_path = "tools/structural_box_sim_v2/sim.py"
    
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
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
            report["checks"]["id_match"] = registry.get("id") == "AUDIT-006"

    # Check policy existence
    if not os.path.exists(policy_path):
        report["status"] = "fail"
        report["errors"].append(f"Policy document missing: {policy_path}")
        report["checks"]["policy_exists"] = "fail"
    else:
        report["checks"]["policy_exists"] = "pass"
        with open(policy_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "explicit euler" in content and "stability" in content and "clamping" in content:
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

    # Check sim implementation
    if not os.path.exists(sim_path):
        report["status"] = "fail"
        report["errors"].append(f"Sim file missing: {sim_path}")
        report["checks"]["sim_exists"] = "fail"
    else:
        report["checks"]["sim_exists"] = "pass"
        with open(sim_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "check_stability" in content and "stability_warnings" in content:
                report["checks"]["diagnostic_logic_detected"] = "pass"
            else:
                report["status"] = "fail"
                report["checks"]["diagnostic_logic_detected"] = "fail"
                report["errors"].append("Stability diagnostic logic not detected in sim.py")

    output_path = "outputs/audits/math_program_validation_after_audit006_structural_euler_stability_bounds.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"audit006_structural_euler_stability_bounds_validation": report}, f, indent=2)
    
    print(json.dumps({"audit006_structural_euler_stability_bounds_validation": report}, indent=2))
    return 0 if report["status"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(validate_euler_stability())
