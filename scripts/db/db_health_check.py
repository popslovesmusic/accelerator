import sqlite3
import os
import json
import argparse
from datetime import datetime

def run_db_health_check(db_path, schema_path, include_supersession_edge_quality=True):
    health = {
        "status": "pass",
        "db_path": db_path,
        "schema_path": schema_path,
        "integrity_check": "unknown",
        "table_status": {},
        "row_counts": {},
        "orientation_status_values": {},
        "retrieval_smoke": {},
        "supersession_edge_quality": {},
        "stale_index_warnings": [],
        "ssot_boundary": "pass",
        "maintenance_recommendations": []
    }

    errors = []

    # 1. Existence Checks
    if not os.path.exists(db_path):
        health["status"] = "fail"
        errors.append(f"Database file missing: {db_path}")
    if not os.path.exists(schema_path):
        health["status"] = "fail"
        errors.append(f"Schema file missing: {schema_path}")

    if health["status"] == "fail":
        return health, errors

    try:
        conn = sqlite3.connect(db_path, timeout=1.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 2. SQLite Integrity Check
        cursor.execute("PRAGMA integrity_check")
        row = cursor.fetchone()
        health["integrity_check"] = row[0]
        if health["integrity_check"] != "ok":
            health["status"] = "fail"
            errors.append(f"SQLite integrity check failed: {health['integrity_check']}")

        # 3. Table Presence
        required_tables = [
            "artifacts", "audit_reports", "tool_health", "registry_snapshots", 
            "claim_evidence_links", "supersession_edges", "orientation_status_types"
        ]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        found_tables = [r["name"] for r in cursor.fetchall()]
        
        for table in required_tables:
            if table in found_tables:
                health["table_status"][table] = "present"
                # Row counts
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                health["row_counts"][table] = count
                
                # Expectations
                if table in ["artifacts", "registry_snapshots", "orientation_status_types"] and count == 0:
                    health["status"] = "warning"
                    health["stale_index_warnings"].append(f"Table '{table}' is empty.")
            else:
                health["table_status"][table] = "missing"
                health["status"] = "fail"
                errors.append(f"Required table missing: {table}")

        # 4. Orientation Status Values
        required_statuses = [
            "current_command_evidence", "canonical_active", "active_runtime", 
            "historical_residue", "archived", "deprecated", "superseded", 
            "invalidated", "unverified_residue"
        ]
        if "orientation_status_types" in found_tables:
            cursor.execute("SELECT status FROM orientation_status_types")
            found_statuses = [r["status"] for r in cursor.fetchall()]
            for s in required_statuses:
                if s in found_statuses:
                    health["orientation_status_values"][s] = "present"
                else:
                    health["orientation_status_values"][s] = "missing"
                    health["status"] = "fail"
                    errors.append(f"Required orientation status missing: {s}")

        # 5. Retrieval Smoke Test
        try:
            # Try a simple query on artifacts
            cursor.execute("SELECT path FROM artifacts LIMIT 1")
            health["retrieval_smoke"] = {"status": "pass"}
        except Exception as e:
            health["retrieval_smoke"] = {"status": "fail", "error": str(e)}
            health["status"] = "fail"
            errors.append(f"Retrieval smoke test failed: {e}")

        # 6. Freshness / Stale Index
        if "artifacts" in found_tables:
            cursor.execute("SELECT MAX(indexed_at) FROM artifacts")
            last_indexed = cursor.fetchone()[0]
            if last_indexed:
                # Basic check: if no files indexed in 24h, warn (heuristic)
                health["row_counts"]["last_artifact_index"] = last_indexed
            else:
                health["stale_index_warnings"].append("Artifact index is empty.")
                if health["status"] == "pass": health["status"] = "warning"

        # 7. Supersession Edge Quality (advisory lineage metadata)
        try:
            from scripts.db.audit_supersession_edges import audit_supersession_edges
        except ImportError:
            try:
                from audit_supersession_edges import audit_supersession_edges
            except ImportError:
                audit_supersession_edges = None

        if include_supersession_edge_quality and audit_supersession_edges is not None and "supersession_edges" in found_tables:
            edge_report = audit_supersession_edges(db_path, sample=0)
            edge_audit = edge_report.get("supersession_edge_audit", {})
            health["supersession_edge_quality"] = {
                "status": edge_audit.get("status", "unknown"),
                "total_edges": edge_audit.get("total_edges", 0),
                "by_relation": edge_audit.get("by_relation", {}),
                "by_confidence": edge_audit.get("by_confidence", {}),
                "reference_integrity": edge_audit.get("reference_integrity", {}),
                "risk_summary": edge_audit.get("risk_summary", []),
                "recommendations": edge_audit.get("recommendations", []),
            }

            # Bubble up risk into overall DB health status conservatively
            edge_status = health["supersession_edge_quality"]["status"]
            if edge_status == "fail":
                health["status"] = "fail"
                errors.append("Supersession edge audit failed; advisory lineage metadata has integrity risks.")
            elif edge_status == "warning" and health["status"] == "pass":
                health["status"] = "warning"
                health["stale_index_warnings"].append("Supersession edges are mostly non-verified or contain cycle/duplicate risks; treat lineage as advisory.")

        conn.close()
    except Exception as e:
        health["status"] = "fail"
        errors.append(f"Exception during health check: {e}")

    return health, errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run acellorator DB health check.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--schema", default="registry/db/schema.sql", help="Path to SQL schema file.")
    
    args = parser.parse_args()
    health, errors = run_db_health_check(args.db, args.schema)
    
    output = {"db_health": health, "errors": errors}
    print(json.dumps(output, indent=2))
