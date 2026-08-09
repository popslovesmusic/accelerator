import json
import os
import re
from datetime import datetime

def run_drift_audit():
    """
    Runner for Recursive Governance Drift Audit.
    Scans documentation and registries for premature closure language and scope inflation.
    """
    registry_path = "registry/math/recursive_governance_drift_registry.json"
    result_path = "validation/results/recursive_governance_drift_audit_result.json"
    
    if not os.path.exists(registry_path):
        return {"status": "fail", "reason": "drift registry missing"}

    with open(registry_path, 'r') as f:
        registry_data = json.load(f)

    patterns = registry_data["closure_language_patterns"]
    
    report = {
        "audit_summary_id": "RGD-AUDIT-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "status": "pass",
        "artifacts_scanned": 0,
        "drift_detections": [],
        "severity_score": "G0",
        "governance_compliance": True
    }

    # Directories to scan for theorem-facing language
    scan_dirs = ["docs/math", "registry/math"]
    
    for s_dir in scan_dirs:
        if not os.path.exists(s_dir):
            continue
        for filename in os.listdir(s_dir):
            if filename.endswith(".md") or filename.endswith(".json"):
                report["artifacts_scanned"] += 1
                f_path = os.path.join(s_dir, filename)
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as rf:
                    content = rf.read()
                    
                    # 1. Detect closure language patterns
                    for pattern in patterns:
                        if pattern in content.lower():
                            # Check if it's qualified by "strictly local" or similar
                            # This is a heuristic check
                            if "strictly local" not in content.lower() and "restricted domain" not in content.lower():
                                detection = {
                                    "artifact": filename,
                                    "pattern": pattern,
                                    "type": "closure_language_unqualified",
                                    "severity": "G1"
                                }
                                report["drift_detections"].append(detection)
                                report["status"] = "warning"
                                report["severity_score"] = "G1"

                    # 2. Detect global behavior claims
                    if "global behavior" in content.lower() and "unresolved" not in content.lower():
                        detection = {
                            "artifact": filename,
                            "type": "unqualified_global_claim",
                            "severity": "G2"
                        }
                        report["drift_detections"].append(detection)
                        report["status"] = "fail"
                        report["severity_score"] = "G2"

    # Final logic: systemic drift check
    if len(report["drift_detections"]) > 5:
        report["severity_score"] = "G3"
        report["status"] = "fail"

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Recursive governance drift audit complete. Results in {result_path}")
    return report

if __name__ == "__main__":
    run_drift_audit()
