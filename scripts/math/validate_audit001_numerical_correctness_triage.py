import json
import os
import sys

def validate_triage():
    registry_path = "registry/math/audit001_numerical_correctness_triage_registry.json"
    audit_doc_path = "docs/math/numerical_conventions_audit.md"
    test_path = "tests/test_rd_moving_boundary_short_runs.py"
    
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
            report["checks"]["high_confidence_fix_count"] = len([f for f in registry["audit_findings"] if f["status"] == "resolved"])
            report["checks"]["staged_issue_count"] = len([f for f in registry["audit_findings"] if f["status"] == "documented"])

    # Check audit doc existence
    if not os.path.exists(audit_doc_path):
        report["status"] = "fail"
        report["errors"].append(f"Audit document missing: {audit_doc_path}")
        report["checks"]["audit_doc_exists"] = "fail"
    else:
        report["checks"]["audit_doc_exists"] = "pass"
        with open(audit_doc_path, "r") as f:
            content = f.read()
            if "periodic boundary conditions" in content:
                report["checks"]["boundary_documented"] = "pass"
            else:
                report["checks"]["boundary_documented"] = "fail"
                report["errors"].append("Boundary condition convention not documented in audit doc")

    # Check test existence
    if not os.path.exists(test_path):
        report["status"] = "fail"
        report["errors"].append(f"Regression test missing: {test_path}")
        report["checks"]["regression_test_exists"] = "fail"
    else:
        report["checks"]["regression_test_exists"] = "pass"

    # Check RD fix in sim.py
    sim_path = "tools/rd_moving_boundary_sim_v1/sim.py"
    if os.path.exists(sim_path):
        with open(sim_path, "r") as f:
            content = f.read()
            if "history[-1] if history else engine.get_metrics()" in content:
                report["checks"]["rd_crash_fix_detected"] = "pass"
            else:
                report["status"] = "fail"
                report["checks"]["rd_crash_fix_detected"] = "fail"
                report["errors"].append("RD crash fix not detected in sim.py")

    output_path = "outputs/audits/math_program_numerical_correctness_triage.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(validate_triage())
