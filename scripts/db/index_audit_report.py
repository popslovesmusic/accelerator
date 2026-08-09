import sqlite3
import json
import os
import argparse
from datetime import datetime

def index_audit_report(db_path, report_path, task_id=None):
    if not os.path.exists(report_path):
        print(f"Error: Report not found at {report_path}")
        return

    with open(report_path, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {report_path} is not a valid JSON report.")
            return

    report_id = data.get('audit_metadata', {}).get('id') or data.get('audit_report_id')
    timestamp_str = data.get('audit_metadata', {}).get('timestamp') or data.get('timestamp')
    summary = data.get('executive_summary') or data.get('inventory_summary', {}).get('summary')
    
    # Try to parse timestamp
    try:
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except:
        timestamp = datetime.now()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO audit_reports (report_id, path, timestamp, task_id, evidence_orientation, summary, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        report_id,
        report_path,
        timestamp,
        task_id,
        'current_command_evidence',
        summary,
        json.dumps(data)
    ))
    
    conn.commit()
    conn.close()
    print(f"Indexed audit report: {report_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index an audit report in the database.")
    parser.add_argument("report_path", help="Path to the JSON audit report.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--task_id", help="Optional task ID associated with the report.")
    
    args = parser.parse_args()
    index_audit_report(args.db, args.report_path, args.task_id)
