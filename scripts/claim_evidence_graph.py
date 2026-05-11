import sqlite3
import json
import argparse
import os

def build_claim_evidence_graph(db_path, claim_id=None):
    if not os.path.exists(db_path):
        return {"error": f"Database not found at {db_path}"}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    graph = {
        "nodes": [],
        "edges": []
    }

    # 1. Get Claims (from SSOT if possible, or DB if indexed)
    # For now, we assume claims are identified by claim_id and linked in DB
    sql = "SELECT DISTINCT claim_id FROM claim_evidence_links"
    if claim_id:
        sql += " WHERE claim_id = ?"
        cursor.execute(sql, (claim_id,))
    else:
        cursor.execute(sql)
    
    claims = cursor.fetchall()
    for c in claims:
        cid = c["claim_id"]
        graph["nodes"].append({"id": cid, "type": "claim", "label": cid})
        
        # Link to evidence artifacts
        cursor.execute("SELECT * FROM claim_evidence_links WHERE claim_id = ?", (cid,))
        links = cursor.fetchall()
        for link in links:
            graph["edges"].append({
                "from": cid,
                "to": link["source_path"],
                "type": "supported_by",
                "orientation": link["orientation_status"]
            })

    # 2. Get Artifacts and their orientation
    cursor.execute("SELECT * FROM artifacts")
    artifacts = cursor.fetchall()
    for a in artifacts:
        graph["nodes"].append({
            "id": a["path"],
            "type": "artifact",
            "label": os.path.basename(a["path"]),
            "orientation": a["orientation_status"],
            "confidence": a["evidence_confidence"]
        })

    # 3. Get Supersession Edges
    cursor.execute("""
        SELECT a1.path as from_path, a2.path as to_path, s.relation, s.confidence
        FROM supersession_edges s
        JOIN artifacts a1 ON s.from_artifact_id = a1.id
        JOIN artifacts a2 ON s.to_artifact_id = a2.id
    """)
    s_edges = cursor.fetchall()
    for se in s_edges:
        graph["edges"].append({
            "from": se["from_path"],
            "to": se["to_path"],
            "type": se["relation"],
            "confidence": se["confidence"]
        })

    # 4. Get Tool Health
    cursor.execute("SELECT * FROM tool_health")
    healths = cursor.fetchall()
    for h in healths:
        t_id = f"tool:{h['tool_name']}"
        graph["nodes"].append({
            "id": t_id,
            "type": "tool",
            "label": h["tool_name"],
            "status": h["status"]
        })
        if h["evidence_source_path"]:
            graph["edges"].append({
                "from": t_id,
                "to": h["evidence_source_path"],
                "type": "status_evidenced_by"
            })

    conn.close()
    return graph

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a read-only claim-evidence graph.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--claim_id", help="Filter by specific claim ID.")
    args = parser.parse_args()
    
    graph = build_claim_evidence_graph(args.db, args.claim_id)
    print(json.dumps(graph, indent=2))
