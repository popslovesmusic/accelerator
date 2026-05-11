import sqlite3
import json
import os
import argparse
import hashlib
from datetime import datetime
try:
    from scripts.orientation_status_check import classify_path
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from orientation_status_check import classify_path

def get_hash(path):
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def ingest_reports(db_path, paths):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for base_path in paths:
        if not os.path.exists(base_path):
            continue
            
        for root, _, files in os.walk(base_path):
            for name in files:
                if not name.endswith('.json'):
                    continue
                    
                file_path = os.path.relpath(os.path.join(root, name), '.')
                source_hash = get_hash(file_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    continue
                
                if isinstance(data, list):
                    report_id = name.replace('.json', '')
                    ts_str = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    task_id = None
                    orientation = None
                    summary = f"List report with {len(data)} items."
                else:
                    # Extract metadata from dict
                    report_id = data.get('audit_metadata', {}).get('id') or data.get('audit_report_id') or name.replace('.json', '')
                    ts_str = data.get('audit_metadata', {}).get('timestamp') or data.get('timestamp')
                    task_id = data.get('audit_metadata', {}).get('task_id')
                    orientation = data.get('audit_metadata', {}).get('evidence_orientation')
                    summary = data.get('executive_summary') or data.get('inventory_summary', {}).get('summary')
                
                # Standardize timestamp
                try:
                    if ts_str:
                        timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))
                except:
                    timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))

                if not orientation:
                    orientation, _, _ = classify_path(file_path)
                
                # Determine report type
                r_type = "audit"
                if "health" in name.lower(): r_type = "health"
                elif "maintenance" in name.lower(): r_type = "maintenance"

                cursor.execute("""
                    INSERT OR REPLACE INTO audit_reports (
                        report_id, path, timestamp, task_id, report_type, 
                        evidence_orientation, source_hash, summary, metadata
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_id, file_path, timestamp.isoformat(), task_id, r_type,
                    orientation, source_hash, summary, json.dumps(data)
                ))

    conn.commit()
    conn.close()
    print("Audit reports ingested.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest reports into DB.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--paths", nargs="+", default=["outputs/audits", "outputs/reports", "reports"], help="Directories to scan.")
    args = parser.parse_args()
    ingest_reports(args.db, args.paths)
