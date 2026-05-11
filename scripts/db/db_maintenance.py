import sqlite3
import argparse
import os
import json
import sys

def run_maintenance(db_path, mode="report_only", mutate=False):
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    report = {
        "timestamp": os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip(),
        "db_path": db_path,
        "mode": mode,
        "diagnostics": {},
        "actions_taken": []
    }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Safe Diagnostics
        cursor.execute("PRAGMA integrity_check")
        report["diagnostics"]["integrity"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM artifacts")
        report["diagnostics"]["artifact_count"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM audit_reports")
        report["diagnostics"]["report_count"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM registry_snapshots")
        report["diagnostics"]["registry_snapshot_count"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tool_health")
        report["diagnostics"]["tool_health_count"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM supersession_edges")
        report["diagnostics"]["supersession_edge_count"] = cursor.fetchone()[0]

        # Supersession diagnostics (report-only; advisory lineage metadata)
        try:
            from scripts.db.audit_supersession_edges import audit_supersession_edges
        except ImportError:
            try:
                from audit_supersession_edges import audit_supersession_edges
            except ImportError:
                audit_supersession_edges = None

        if audit_supersession_edges is not None:
            edge_report = audit_supersession_edges(db_path, sample=0)
            edge_audit = edge_report.get("supersession_edge_audit", {})
            report["diagnostics"]["supersession_edge_quality"] = {
                "status": edge_audit.get("status", "unknown"),
                "total_edges": edge_audit.get("total_edges", 0),
                "by_relation": edge_audit.get("by_relation", {}),
                "by_confidence": edge_audit.get("by_confidence", {}),
                "reference_integrity": edge_audit.get("reference_integrity", {}),
                "risk_summary": edge_audit.get("risk_summary", []),
            }

        if mutate:
            print(f"Running mutating maintenance on {db_path}...")
            cursor.execute("VACUUM")
            report["actions_taken"].append("VACUUM")
            cursor.execute("ANALYZE")
            report["actions_taken"].append("ANALYZE")
            conn.commit()
            print("Maintenance complete.")
        else:
            print(f"Running report-only diagnostics on {db_path}...")

        conn.close()
        print(json.dumps(report, indent=2))
        
    except Exception as e:
        print(f"Error during maintenance: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database maintenance utility.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--report-only", action="store_true", default=True, help="Run diagnostics without mutating (default).")
    parser.add_argument("--mutate", action="store_true", help="Run VACUUM/ANALYZE (requires explicit flag).")
    
    args = parser.parse_args()
    
    # Enforce safe default
    mode = "mutate" if args.mutate else "report_only"
    run_maintenance(args.db, mode, args.mutate)
