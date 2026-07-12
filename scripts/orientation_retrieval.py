import sqlite3
import json
import argparse
import os
import datetime
try:
    from db.orientation_scoring import calculate_orientation_score
except ImportError:
    from scripts.db.orientation_scoring import calculate_orientation_score
try:
    from tools.inference_governance.candidate_builder import build_bounded_candidate_set_v1
    from tools.inference_governance.candidate_policy import get_candidate_policy, hash_candidate_universe
    from tools.inference_governance.request_normalization import hash_json_value, normalize_text
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from tools.inference_governance.candidate_builder import build_bounded_candidate_set_v1
    from tools.inference_governance.candidate_policy import get_candidate_policy, hash_candidate_universe
    from tools.inference_governance.request_normalization import hash_json_value, normalize_text

def get_text_match_score(path, query):
    normalized_query = normalize_text(query, lowercase=True)
    if not normalized_query:
        return 0.5 # Neutral if no query
    path_lower = normalize_text(path, lowercase=True)
    if normalized_query in path_lower:
        # Simple match: better match if it's in the filename vs directory
        filename = os.path.basename(path_lower)
        if normalized_query in filename:
            return 1.0
        return 0.8
    return 0.0

def get_freshness_score(timestamp_str):
    if not timestamp_str:
        return 0.5
    try:
        # Assuming ISO format from SQLite CURRENT_TIMESTAMP or similar
        ts = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
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

    normalized_query = normalize_text(query)
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
    candidate_universe = []
    authority_scope_values = []
    freshness_markers = []
    for row in rows:
        artifact_id = row["id"]
        path = row['path']
        o_status = row['orientation_status']
        a_scope = row['authority_scope']
        e_conf = row['evidence_confidence']
        indexed_at = row['indexed_at']
        
        text_score = get_text_match_score(path, normalized_query)
        fresh_score = get_freshness_score(indexed_at)
        
        score_data = calculate_orientation_score(o_status, a_scope, e_conf, fresh_score, text_score)
        
        # Filter out 0 matches if a query was provided
        if normalized_query and text_score == 0:
            continue
            
        result = {
            "artifact_id": artifact_id,
            "path": path,
            "artifact_type": row['artifact_type'],
            "orientation_status": o_status,
            "authority_scope": a_scope,
            "evidence_confidence": e_conf,
            "score": score_data["score"],
            "normalized_query": normalized_query,
        }
        candidate_universe.append(
            {
                "candidate_id": path,
                "canonical_name": path,
                "eligibility_status": "ELIGIBLE",
                "authority_status": str(a_scope or "").strip().upper() or "UNKNOWN",
                "freshness_status": "FRESH" if fresh_score >= 0.7 else ("STALE" if fresh_score <= 0.3 else "UNKNOWN"),
                "compatibility_status": str(o_status or "").strip().upper() or "UNKNOWN",
                "rank_score": score_data["score"],
                "rank_components": score_data["breakdown"],
                "provenance": {
                    "artifact_id": artifact_id,
                    "path": path,
                    "query": normalized_query,
                    "indexed_at": indexed_at,
                    "orientation_status": o_status,
                    "authority_scope": a_scope,
                },
                "policy_rule_id": "artifact_text_match",
            }
        )
        authority_scope_values.append(str(a_scope or "").strip())
        freshness_markers.append(
            {
                "indexed_at": indexed_at,
                "freshness_score": fresh_score,
            }
        )
        
        if explain:
            result["score_breakdown"] = score_data["breakdown"]
            result["why_ranked"] = [
                f"Orientation: {o_status} (weighted)",
                f"Scope: {a_scope} (weighted)",
                f"Confidence: {e_conf} (weighted)",
                f"Freshness: {fresh_score} (calculated from {indexed_at})",
                f"Text Match: {text_score} (query: {normalized_query})"
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

    # Sort by score descending with deterministic tie-breakers.
    results.sort(key=lambda x: (-float(x.get("score", 0.0) or 0.0), str(x.get("path") or ""), str(x.get("artifact_id") or "")))

    candidate_policy = dict(get_candidate_policy("governed_context_artifact_candidates_v1"))
    try:
        request_limit = max(0, int(limit if limit is not None else candidate_policy.get("maximum_candidates", 20)))
    except Exception:
        request_limit = int(candidate_policy.get("maximum_candidates", 20) or 20)
    candidate_policy["maximum_candidates"] = min(
        request_limit,
        int(candidate_policy.get("maximum_candidates", request_limit) or request_limit),
    )
    authority_hash = hash_json_value(sorted(set(authority_scope_values))) if authority_scope_values else hash_json_value([])
    freshness_hash = hash_json_value(freshness_markers)
    universe_hash = hash_candidate_universe(
        candidate_universe,
        candidate_type="ARTIFACT",
        candidate_policy_id="governed_context_artifact_candidates_v1",
        policy_version=str(candidate_policy.get("policy_version") or "1.0.0"),
    )
    candidate_set = build_bounded_candidate_set_v1(
        candidate_type="ARTIFACT",
        candidate_policy=candidate_policy,
        universe_candidates=candidate_universe,
        authority_hash=authority_hash,
        freshness_hash=freshness_hash,
        universe_hash=universe_hash,
        operation_code="artifact_retrieval",
        candidate_policy_id="governed_context_artifact_candidates_v1",
        candidate_policy_version=str(candidate_policy.get("policy_version") or "1.0.0"),
    )
    results = results[: candidate_policy["maximum_candidates"]]

    conn.close()

    output = {
        "query": query,
        "normalized_query": normalized_query,
        "db_path": db_path,
        "results": results,
        "warnings": [],
        "candidate_policy_id": candidate_set.get("candidate_policy_id"),
        "candidate_policy_version": candidate_set.get("candidate_policy_version"),
        "candidate_set_hash": candidate_set.get("candidate_set_hash"),
        "candidate_set": candidate_set,
    }

    if explain:
        output["warnings"].append("Supersession edges are advisory unless verified.")
        output["warnings"].append("Pattern-detected lineage must not be treated as source of truth.")
        if not supersession_table_present:
            output["warnings"].append("No supersession_edges table detected; lineage analysis skipped.")
        output["candidate_provenance"] = candidate_set.get("eligible_candidates", [])
        output["candidate_exclusions"] = candidate_set.get("excluded_candidates", [])

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
