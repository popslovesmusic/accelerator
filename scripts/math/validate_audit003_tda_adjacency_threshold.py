import json
import os
import sys

def validate_threshold():
    registry_path = "registry/math/audit003_tda_adjacency_threshold_registry.json"
    policy_path = "docs/math/tda_adjacency_threshold_policy.md"
    test_path = "tests/test_tda_adjacency_threshold.py"
    engine_path = "tools/tda_module_v1/tda_engine.py"
    
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
            report["checks"]["id_match"] = registry.get("id") == "AUDIT-003"

    # Check policy existence
    if not os.path.exists(policy_path):
        report["status"] = "fail"
        report["errors"].append(f"Policy document missing: {policy_path}")
        report["checks"]["policy_exists"] = "fail"
    else:
        report["checks"]["policy_exists"] = "pass"
        with open(policy_path, "r") as f:
            content = f.read()
            if "adjacency_threshold" in content and "Default Behavior" in content:
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
            if "adjacency_threshold=0.0" in content and "np.where(np.abs(adj_matrix) > adjacency_threshold" in content:
                report["checks"]["threshold_logic_detected"] = "pass"
            else:
                report["status"] = "fail"
                report["checks"]["threshold_logic_detected"] = "fail"
                report["errors"].append("Threshold logic not detected in tda_engine.py")

    output_path = "outputs/audits/math_program_validation_after_audit003_tda_adjacency_threshold.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"audit003_tda_adjacency_threshold_validation": report}, f, indent=2)
    
    print(json.dumps({"audit003_tda_adjacency_threshold_validation": report}, indent=2))
    return 0 if report["status"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(validate_threshold())
