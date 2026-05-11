import sqlite3
import json
import argparse
import os
from datetime import datetime

def run_registry_runtime_trace(db_path, query=None, limit=20):
    if not os.path.exists(db_path):
        return {"error": f"Database not found at {db_path}"}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    report = {
        "trace_report": {
            "task_id": f"TRACE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "query": query,
            "mode": "read_only_traceability",
            "registry_sources_read": [],
            "runtime_sources_read": [],
            "db_sources_read": [db_path],
            "trace_entities": [],
            "trace_edges": [],
            "resolved_links": [],
            "missing_links": [],
            "conflicts": [],
            "residue_only_sources": [],
            "supersession_cautions": [],
            "ssot_boundary_status": "pass",
            "recommended_next_actions": [],
            "warnings": []
        }
    }

    # 1. Read SSOT Registries (Read-only)
    registries = {
        "tool_manifest": "registry/tool_manifest.json",
        "lexicon": "registry/lexicon_canonical.json",
        "math": "registry/math_registry.json",
        "compliance": "registry/compliance_charter_v2_3.json"
    }

    tool_names = []
    lexicon_terms = []

    for key, path in registries.items():
        if os.path.exists(path):
            report["trace_report"]["registry_sources_read"].append(path)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if key == "tool_manifest":
                        for t in data.get("tools", []):
                            name = t.get("name")
                            if name:
                                tool_names.append(name)
                                report["trace_report"]["trace_entities"].append({
                                    "id": f"reg:tool:{name}",
                                    "type": "tool_manifest_entry",
                                    "source": path,
                                    "data": {"certification_level": t.get("certification_level")}
                                })
                    elif key == "lexicon":
                        for t in data.get("terms", []):
                            term = t.get("term")
                            if term:
                                lexicon_terms.append(term)
                                report["trace_report"]["trace_entities"].append({
                                    "id": f"reg:term:{term}",
                                    "type": "lexicon_term",
                                    "source": path
                                })
            except Exception as e:
                report["trace_report"]["warnings"].append(f"Error reading registry {path}: {e}")

    # 2. Query DB for matches
    if query:
        cursor.execute("SELECT * FROM artifacts WHERE path LIKE ? OR metadata LIKE ?", (f"%{query}%", f"%{query}%"))
    else:
        cursor.execute("SELECT * FROM artifacts LIMIT ?", (limit,))
    
    db_artifacts = cursor.fetchall()
    for art in db_artifacts:
        path = art["path"]
        status = art["orientation_status"]
        report["trace_report"]["trace_entities"].append({
            "id": f"db:art:{path}",
            "type": "db_artifact_row",
            "orientation": status,
            "scope": art["authority_scope"]
        })
        
        # Link tools to artifacts
        for t_name in tool_names:
            if t_name.lower() in path.lower():
                report["trace_report"]["trace_edges"].append({
                    "from": f"reg:tool:{t_name}",
                    "to": f"db:art:{path}",
                    "relation": "observed_by"
                })
                report["trace_report"]["resolved_links"].append(f"Tool '{t_name}' matched artifact '{path}'")

    # 3. Check Tool Health
    cursor.execute("SELECT * FROM tool_health")
    health_rows = cursor.fetchall()
    for hr in health_rows:
        t_name = hr["tool_name"]
        status = hr["status"]
        report["trace_report"]["trace_entities"].append({
            "id": f"db:health:{t_name}",
            "type": "tool_health_snapshot",
            "status": status,
            "source": hr["evidence_source_path"]
        })
        
        report["trace_report"]["trace_edges"].append({
            "from": f"reg:tool:{t_name}",
            "to": f"db:health:{t_name}",
            "relation": "status_monitored_as"
        })

    # 4. Detect Gaps
    for t_name in tool_names:
        found = False
        for hr in health_rows:
            if hr["tool_name"] == t_name:
                found = True
                break
        if not found:
            report["trace_report"]["missing_links"].append({
                "entity": f"reg:tool:{t_name}",
                "missing": "tool_health_snapshot",
                "severity": "warning"
            })

    conn.close()
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate registry-to-runtime traceability report.")
    parser.add_argument("--query", help="Keyword for trace lookup.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=20, help="Limit DB artifact lookup.")
    
    args = parser.parse_args()
    
    report = run_registry_runtime_trace(args.db, args.query, args.limit)
    print(json.dumps(report, indent=2))
