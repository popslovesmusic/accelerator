import json
import os
import argparse

def validate_audit007_closure():
    results = {
        "audit007_implementation_triage_closure_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registry_path = "registry/math/audit007_implementation_triage_closure_registry.json"
    report_path = "docs/math/tool_audit_closure_report.md"

    # 1. Registry exists
    if not os.path.exists(registry_path):
        results["audit007_implementation_triage_closure_validation"]["status"] = "fail"
        results["audit007_implementation_triage_closure_validation"]["errors"].append("AUDIT-007 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f).get("audit007_implementation_triage_closure", {})
                
                # 2. Dependencies declared
                deps = data.get("depends_on", [])
                required_deps = ["AUDIT-001", "AUDIT-002", "AUDIT-003", "AUDIT-004", "AUDIT-005", "AUDIT-006"]
                for rd in required_deps:
                    if rd not in deps:
                        results["audit007_implementation_triage_closure_validation"]["status"] = "fail"
                        results["audit007_implementation_triage_closure_validation"]["errors"].append(f"Dependency {rd} missing from registry.")
                
                # 3. Unresolved backlog items listed
                if not data.get("unresolved_backlog_items"):
                    results["audit007_implementation_triage_closure_validation"]["status"] = "fail"
                    results["audit007_implementation_triage_closure_validation"]["errors"].append("Unresolved backlog items missing.")
                
                results["audit007_implementation_triage_closure_validation"]["checks"].append("AUDIT-007 registry content verified.")
        except Exception as e:
            results["audit007_implementation_triage_closure_validation"]["status"] = "fail"
            results["audit007_implementation_triage_closure_validation"]["errors"].append(f"Parse error: {e}")

    # 4. Report exists
    if not os.path.exists(report_path):
        results["audit007_implementation_triage_closure_validation"]["status"] = "fail"
        results["audit007_implementation_triage_closure_validation"]["errors"].append("Tool audit closure report missing.")
    else:
        results["audit007_implementation_triage_closure_validation"]["checks"].append("Tool audit closure report exists.")

    # 5. No overreach checks
    # These are qualitative checks that the agent must ensure during creation.
    # The validator confirms the registry exists and has the correct stopping status.
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            data = json.load(f).get("audit007_implementation_triage_closure", {})
            if data.get("status") != "paused_complete":
                 results["audit007_implementation_triage_closure_validation"]["status"] = "fail"
                 results["audit007_implementation_triage_closure_validation"]["errors"].append("AUDIT-007 status is not paused_complete.")

    return results

if __name__ == "__main__":
    res = validate_audit007_closure()
    print(json.dumps(res, indent=2))
