import sqlite3
import json
import argparse
import os

def build_causal_provenance(db_path):
    if not os.path.exists(db_path):
        return {"error": f"Database not found at {db_path}"}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # This script synthesizes provenance from existing DB links and metadata
    # In a real implementation, this might populate a dedicated provenance table.
    # For this patch, we build a structured graph view.

    provenance = {
        "nodes": [],
        "edges": []
    }

    # 1. Claims
    cursor.execute("SELECT DISTINCT claim_id FROM claim_evidence_links")
    for row in cursor.fetchall():
        provenance["nodes"].append({"id": f"claim:{row['claim_id']}", "type": "claim", "label": row['claim_id']})

    # 2. Artifacts (including orientation)
    cursor.execute("SELECT id, path, orientation_status, evidence_confidence FROM artifacts")
    for row in cursor.fetchall():
        provenance["nodes"].append({
            "id": f"art:{row['path']}", 
            "type": "db_artifact", 
            "label": os.path.basename(row['path']),
            "orientation": row['orientation_status'],
            "confidence": row['evidence_confidence']
        })

    # 3. Supersession Edges (Advisory)
    cursor.execute("""
        SELECT a1.path as from_path, a2.path as to_path, s.relation, s.confidence
        FROM supersession_edges s
        JOIN artifacts a1 ON s.from_artifact_id = a1.id
        JOIN artifacts a2 ON s.to_artifact_id = a2.id
    """)
    for row in cursor.fetchall():
        provenance["edges"].append({
            "from": f"art:{row['from_path']}",
            "to": f"art:{row['to_path']}",
            "type": row['relation'],
            "confidence": row['confidence']
        })

    # 4. Evidence Links
    cursor.execute("SELECT claim_id, source_path, orientation_status FROM claim_evidence_links")
    for row in cursor.fetchall():
        provenance["edges"].append({
            "from": f"art:{row['source_path']}",
            "to": f"claim:{row['claim_id']}",
            "type": "supports",
            "confidence": "verified" if row['orientation_status'] == "canonical_active" else "probable"
        })

    # 5. Tool Health Links
    cursor.execute("SELECT tool_name, status, evidence_source_path FROM tool_health")
    for row in cursor.fetchall():
        t_node = f"tool:{row['tool_name']}"
        provenance["nodes"].append({"id": t_node, "type": "tool", "label": row['tool_name']})
        if row['evidence_source_path']:
            provenance["edges"].append({
                "from": f"art:{row['evidence_source_path']}",
                "to": t_node,
                "type": "observed_by",
                "confidence": "verified"
            })

    conn.close()
    return provenance

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build causal provenance graph.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    args = parser.parse_args()
    
    prov = build_causal_provenance(args.db)
    print(json.dumps(prov, indent=2))
