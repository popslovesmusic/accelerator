import json
import os
import argparse
from datetime import datetime
try:
    from scripts.orientation_status_check import classify_path
except ImportError:
    from orientation_status_check import classify_path

def audit_current_state():
    # Gather evidence of the current state
    evidence = {
        "timestamp": datetime.now(datetime.UTC).isoformat() + "Z",
        "active_command_evidence": [],
        "system_inventory": {
            "registry_count": len(os.listdir('registry')) if os.path.exists('registry') else 0,
            "script_count": len(os.listdir('scripts')) if os.path.exists('scripts') else 0,
            "tool_count": len(os.listdir('tools')) if os.path.exists('tools') else 0
        }
    }
    
    # Find recently modified files as "current evidence"
    for root, dirs, files in os.walk('.'):
        for name in files:
            p = os.path.relpath(os.path.join(root, name), '.')
            if classify_path(p) == 'current_command_evidence':
                evidence["active_command_evidence"].append(p)
                
    # Include DB health summary
    db_path = "registry/db/acellorator_index.sqlite"
    schema_path = "registry/db/schema.sql"
    try:
        from scripts.db.db_health_check import run_db_health_check
        health, _ = run_db_health_check(db_path, schema_path)
        evidence["db_health_summary"] = {
            "status": health["status"],
            "artifact_count": health["row_counts"].get("artifacts", 0),
            "report_count": health["row_counts"].get("audit_reports", 0)
        }
    except Exception as e:
        evidence["db_health_summary"] = {"status": "error", "error": str(e)}

    return evidence

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit current platform state.")
    parser.add_argument("--output", default="outputs/audits/current_state_audit.json", help="Path to save audit.")
    args = parser.parse_args()
    
    audit = audit_current_state()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(audit, f, indent=2)
    print(f"Current state audit saved to {args.output}")
