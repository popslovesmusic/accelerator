import sqlite3
import json
import os
import argparse
from datetime import datetime

def ingest_tool_health(db_path, report_paths):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for path in report_paths:
        if not os.path.exists(path):
            continue
            
        for root, _, files in os.walk(path):
            for name in files:
                if not name.endswith('.json'): continue
                
                file_path = os.path.join(root, name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except: continue

                # Look for tool health patterns (e.g., global_health_report or tool_certification)
                tools_data = []
                
                # Pattern 1: global_health_report.json
                if "engine_validation" in data:
                    engine_val = data["engine_validation"]
                    status = "PASS" if engine_val.get("status") == "success" else "FAIL"
                    timestamp = data.get("timestamp", datetime.now().isoformat())
                    
                    for t_name in engine_val.get("tools_tested", []):
                        tools_data.append({
                            "tool_name": t_name,
                            "status": "PASS",
                            "evidence": file_path,
                            "timestamp": timestamp
                        })
                    for failure in engine_val.get("failures", []):
                        tools_data.append({
                            "tool_name": failure.get("tool"),
                            "status": "FAIL",
                            "evidence": file_path,
                            "timestamp": timestamp,
                            "error": str(failure.get("error"))
                        })

                # Pattern 2: Generic tool status in metadata
                if not tools_data and "db_health" in data:
                    # Could extract from DB health if needed
                    pass

                for t in tools_data:
                    cursor.execute("""
                        INSERT INTO tool_health (
                            tool_name, status, evidence_source_path, 
                            last_check, error_log
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        t["tool_name"], t["status"], t["evidence"],
                        t["timestamp"], t.get("error")
                    ))

    conn.commit()
    conn.close()
    print("Tool health data ingested.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest tool health from reports.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--paths", nargs="+", default=["outputs/audits", "reports"], help="Directories to scan.")
    args = parser.parse_args()
    ingest_tool_health(args.db, args.paths)
