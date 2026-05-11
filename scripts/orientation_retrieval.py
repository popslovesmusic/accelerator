import sqlite3
import json
import argparse
import os
from datetime import datetime, timezone
try:
    from db.orientation_scoring import calculate_orientation_score
except ImportError:
    from scripts.db.orientation_scoring import calculate_orientation_score

def get_text_match_score(path, query):
    if not query:
        return 0.5 # Neutral if no query
    path_lower = path.lower()
    query_lower = query.lower()
    if query_lower in path_lower:
        # Simple match: better match if it's in the filename vs directory
        filename = os.path.basename(path_lower)
        if query_lower in filename:
            return 1.0
        return 0.8
    return 0.0

def get_freshness_score(timestamp_str):
    if not timestamp_str:
        return 0.5
    try:
        # Assuming ISO format from SQLite CURRENT_TIMESTAMP or similar
        ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = now - ts
        # Score 1.0 for < 1 day, 0.5 for 1 week, 0.1 for > 1 month
        days = delta.days
        if days < 1: return 1.0
        if days < 7: return 0.7
        if days < 30: return 0.3
        return 0.1
    except:
        return 0.5

def _table_exists(cursor, table_name):
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table_name,))
    return cursor.fetchone() is not None

def _supersession_summary(cursor, artifact_id):
    # Advisory lineage metadata only: counts + cautions; does not change retrieval inclusion.
    empty = {
        "edge_count": 0,
        "relations": [],
        "confidence_labels": [],
        "has_verified_edge": False,
        "has_probable_edge": False,
        "has_weak_edge": False,
        "pattern_only": False,
        "cycle_risk": False
    }
    if artifact_id is None:
        return empty

    # Count edges (either direction)
    cursor.execute(
        "SELECT COUNT(*) FROM supersession_edges WHERE from_artifact_id=? OR to_artifact_id=?",
        (artifact_id, artifact_id),
    )
    edge_count = cursor.fetchone()[0]
    if edge_count == 0:
        return empty

    # Relations/confidence counts
    cursor.execute(
        "SELECT relation, COUNT(*) AS c FROM supersession_edges WHERE from_artifact_id=? OR to_artifact_id=? GROUP BY relation",
        (artifact_id, artifact_id),
    )
    rel_counts = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute(
        "SELECT COALESCE(confidence,'weak') AS confidence, COUNT(*) AS c FROM supersession_edges WHERE from_artifact_id=? OR to_artifact_id=? GROUP BY COALESCE(confidence,'weak')",
        (artifact_id, artifact_id),
    )
    conf_counts = {r[0].lower(): r[1] for r in cursor.fetchall()}

    has_verified = conf_counts.get("verified", 0) > 0
    has_probable = conf_counts.get("probable", 0) > 0
    has_weak = conf_counts.get("weak", 0) > 0

    # Pattern-only heuristic: no evidence_path and no reason (for non-verified edges)
    cursor.execute(
        """
        SELECT COUNT(*) FROM supersession_edges
        WHERE (from_artifact_id=? OR to_artifact_id=?)
          AND lower(COALESCE(confidence,'weak')) IN ('weak','probable')
          AND (evidence_path IS NULL OR trim(evidence_path) = '')
          AND (reason IS NULL OR trim(reason) = '')
        """,
        (artifact_id, artifact_id),
    )
    pattern_only_count = cursor.fetchone()[0]
    pattern_only = (pattern_only_count == edge_count) and (not has_verified)

    # Cycle-risk heuristic: detect reciprocal pair(s) involving this artifact.
    cursor.execute(
        """
        SELECT 1
        FROM supersession_edges se1
        JOIN supersession_edges se2
          ON se1.from_artifact_id = se2.to_artifact_id
         AND se1.to_artifact_id = se2.from_artifact_id
        WHERE (se1.from_artifact_id = ? OR se1.to_artifact_id = ?)
        LIMIT 1
        """,
        (artifact_id, artifact_id),
    )
    cycle_risk = cursor.fetchone() is not None

    return {
        "edge_count": int(edge_count),
        "relations": [{"relation": k, "count": int(v)} for k, v in sorted(rel_counts.items(), key=lambda kv: (-kv[1], kv[0]))],
        "confidence_labels": [{"confidence": k, "count": int(v)} for k, v in sorted(conf_counts.items(), key=lambda kv: (-kv[1], kv[0]))],
        "has_verified_edge": bool(has_verified),
        "has_probable_edge": bool(has_probable),
        "has_weak_edge": bool(has_weak),
        "pattern_only": bool(pattern_only),
        "cycle_risk": bool(cycle_risk),
    }

def retrieve_artifacts(db_path, query=None, status_filter=None, limit=20, explain=False):
    if not os.path.exists(db_path):
        return {"error": f"Database not found at {db_path}"}

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM artifacts"
    params = []
    if status_filter:
        placeholders = ', '.join(['?'] * len(status_filter))
        sql += f" WHERE orientation_status IN ({placeholders})"
        params.extend(status_filter)
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()

    supersession_table_present = False
    try:
        supersession_table_present = _table_exists(cursor, "supersession_edges")
    except Exception:
        supersession_table_present = False
    
    results = []
    for row in rows:
        artifact_id = row["id"]
        path = row['path']
        o_status = row['orientation_status']
        a_scope = row['authority_scope']
        e_conf = row['evidence_confidence']
        indexed_at = row['indexed_at']
        
        text_score = get_text_match_score(path, query)
        fresh_score = get_freshness_score(indexed_at)
        
        score_data = calculate_orientation_score(o_status, a_scope, e_conf, fresh_score, text_score)
        
        # Filter out 0 matches if a query was provided
        if query and text_score == 0:
            continue
            
        result = {
            "path": path,
            "artifact_type": row['artifact_type'],
            "orientation_status": o_status,
            "authority_scope": a_scope,
            "evidence_confidence": e_conf,
            "score": score_data["score"]
        }
        
        if explain:
            result["score_breakdown"] = score_data["breakdown"]
            result["why_ranked"] = [
                f"Orientation: {o_status} (weighted)",
                f"Scope: {a_scope} (weighted)",
                f"Confidence: {e_conf} (weighted)",
                f"Freshness: {fresh_score} (calculated from {indexed_at})",
                f"Text Match: {text_score} (query: {query})"
            ]
            result["cautions"] = []
            if o_status in ["historical_residue", "superseded", "deprecated"]:
                result["cautions"].append(f"Artifact is {o_status}; verify against canonical registries.")

            result["supersession"] = {
                "edge_count": 0,
                "relations": [],
                "confidence_labels": [],
                "has_verified_edge": False,
                "has_probable_edge": False,
                "has_weak_edge": False,
                "pattern_only": True,
                "cycle_risk": False
            }

            if supersession_table_present:
                try:
                    sup = _supersession_summary(cursor, artifact_id)
                    result["supersession"] = sup
                    if sup["edge_count"] > 0:
                        result["cautions"].append("Supersession edges are advisory unless verified; do not treat lineage as authority for deletion/suppression.")
                        if sup["has_probable_edge"] or sup["has_weak_edge"]:
                            result["cautions"].append("Artifact has probable/weak supersession edges; treat lineage as retrieval hint only.")
                        if sup["pattern_only"]:
                            result["cautions"].append("Artifact lineage appears pattern-detected only (no explicit evidence_path/reason on edges).")
                        if sup["cycle_risk"]:
                            result["cautions"].append("Artifact participates in a supersession 2-cycle candidate; lineage may be inconsistent.")
                except Exception as e:
                    result["cautions"].append(f"Supersession lookup failed (advisory only): {e}")
            else:
                result["cautions"].append("Supersession edges table missing; lineage cautions unavailable.")

        results.append(result)

    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    results = results[:limit]

    conn.close()
    
    output = {
        "query": query,
        "db_path": db_path,
        "results": results,
        "warnings": []
    }

    if explain:
        output["warnings"].append("Supersession edges are advisory unless verified.")
        output["warnings"].append("Pattern-detected lineage must not be treated as source of truth.")
        if not supersession_table_present:
            output["warnings"].append("No supersession_edges table detected; lineage analysis skipped.")

    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve artifacts ranked by orientation-aware score.")
    parser.add_argument("--query", help="Keyword query for text matching.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--status", nargs="+", help="Filter by orientation status(es).")
    parser.add_argument("--limit", type=int, default=20, help="Limit results.")
    parser.add_argument("--explain", action="store_true", help="Include score breakdown and explanation.")
    
    args = parser.parse_args()
    
    output = retrieve_artifacts(args.db, args.query, args.status, args.limit, args.explain)
    print(json.dumps(output, indent=2))
