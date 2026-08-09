import sqlite3
import json
import argparse
import os
from datetime import datetime
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
    normalized_query = normalize_text(query)

    # 1. Read SSOT Registries (Read-only)
    registries = {
        "tool_manifest": "registry/tool_manifest.json",
        "lexicon": "registry/lexicon_canonical.json",
        "math": "registry/math_source_registry.json",
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
                    elif key == "math":
                        for doc in data.get("documents", []):
                            doc_id = doc.get("doc_id") or doc.get("path")
                            doc_path = doc.get("path")
                            if not doc_id or not doc_path:
                                continue
                            report["trace_report"]["trace_entities"].append({
                                "id": f"reg:math_source:{doc_id}",
                                "type": "math_source_document",
                                "source": path,
                                "data": {
                                    "path": doc_path,
                                    "classification": doc.get("classification"),
                                },
                            })
            except Exception as e:
                report["trace_report"]["warnings"].append(f"Error reading registry {path}: {e}")

    # 2. Query DB for matches
    if normalized_query:
        query_term = f"%{normalized_query.lower()}%"
        cursor.execute(
            "SELECT * FROM artifacts WHERE LOWER(path) LIKE ? OR LOWER(metadata) LIKE ? ORDER BY path ASC, id ASC",
            (query_term, query_term),
        )
    else:
        cursor.execute("SELECT * FROM artifacts ORDER BY path ASC, id ASC LIMIT ?", (limit,))
    
    db_artifacts = cursor.fetchall()
    artifact_candidates = []
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
        artifact_candidates.append(
            {
                "candidate_id": path,
                "canonical_name": path,
                "eligibility_status": "ELIGIBLE" if not normalized_query or normalized_query.lower() in path.lower() else "OUT_OF_SCOPE",
                "authority_status": str(art["authority_scope"] or "").strip().upper() or "UNKNOWN",
                "freshness_status": "FRESH" if str(art["indexed_at"] or "").strip() else "UNKNOWN",
                "compatibility_status": str(status or "").strip().upper() or "UNKNOWN",
                "rank_score": 1.0 if not normalized_query else (1.0 if normalized_query.lower() in path.lower() else 0.0),
                "rank_components": {
                    "query": normalized_query,
                    "orientation_status": status,
                    "authority_scope": art["authority_scope"],
                },
                "provenance": {
                    "artifact_id": art["id"],
                    "path": path,
                    "orientation_status": status,
                    "authority_scope": art["authority_scope"],
                    "indexed_at": art["indexed_at"],
                    "query": normalized_query,
                },
                "policy_rule_id": "registry_runtime_trace_artifact_match",
            }
        )

    # 3. Check Tool Health
    cursor.execute("SELECT * FROM tool_health ORDER BY tool_name ASC")
    health_rows = cursor.fetchall()
    tool_candidates = []
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
        tool_candidates.append(
            {
                "candidate_id": t_name,
                "canonical_name": t_name,
                "eligibility_status": "ELIGIBLE",
                "authority_status": str(status or "").strip().upper() or "UNKNOWN",
                "freshness_status": "FRESH" if str(hr["evidence_source_path"] or "").strip() else "UNKNOWN",
                "compatibility_status": "ACTIVE" if str(status or "").strip().lower() == "active" else str(status or "").strip().upper() or "UNKNOWN",
                "rank_score": 1.0 if str(status or "").strip().lower() == "active" else 0.5,
                "rank_components": {
                    "tool_status": status,
                    "evidence_source_path": hr["evidence_source_path"],
                },
                "provenance": {
                    "tool_name": t_name,
                    "status": status,
                    "evidence_source_path": hr["evidence_source_path"],
                },
                "policy_rule_id": "registry_runtime_trace_tool_match",
            }
        )

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

    artifact_policy = get_candidate_policy("registry_runtime_trace_candidates_v1")
    tool_policy = get_candidate_policy("tool_candidates_v1")
    artifact_candidate_set = build_bounded_candidate_set_v1(
        candidate_type="ARTIFACT",
        candidate_policy=artifact_policy,
        universe_candidates=artifact_candidates,
        authority_hash=hash_json_value(sorted({candidate["authority_status"] for candidate in artifact_candidates})),
        freshness_hash=hash_json_value([candidate["provenance"].get("indexed_at") for candidate in artifact_candidates]),
        universe_hash=hash_candidate_universe(
            artifact_candidates,
            candidate_type="ARTIFACT",
            candidate_policy_id="registry_runtime_trace_candidates_v1",
            policy_version=str(artifact_policy.get("policy_version") or "1.0.0"),
        ),
        operation_code="registry_runtime_trace",
        candidate_policy_id="registry_runtime_trace_candidates_v1",
        candidate_policy_version=str(artifact_policy.get("policy_version") or "1.0.0"),
    )
    tool_candidate_set = build_bounded_candidate_set_v1(
        candidate_type="TOOL",
        candidate_policy=tool_policy,
        universe_candidates=tool_candidates,
        authority_hash=hash_json_value(sorted({candidate["authority_status"] for candidate in tool_candidates})),
        freshness_hash=hash_json_value([candidate["provenance"].get("evidence_source_path") for candidate in tool_candidates]),
        universe_hash=hash_candidate_universe(
            tool_candidates,
            candidate_type="TOOL",
            candidate_policy_id="tool_candidates_v1",
            policy_version=str(tool_policy.get("policy_version") or "1.0.0"),
        ),
        operation_code="registry_runtime_trace",
        candidate_policy_id="tool_candidates_v1",
        candidate_policy_version=str(tool_policy.get("policy_version") or "1.0.0"),
    )
    report["trace_report"]["normalized_query"] = normalized_query
    report["trace_report"]["candidate_sets"] = {
        "artifacts": artifact_candidate_set,
        "tools": tool_candidate_set,
    }
    report["trace_report"]["candidate_policy_ids"] = {
        "artifacts": artifact_candidate_set.get("candidate_policy_id"),
        "tools": tool_candidate_set.get("candidate_policy_id"),
    }
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate registry-to-runtime traceability report.")
    parser.add_argument("--query", help="Keyword for trace lookup.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=20, help="Limit DB artifact lookup.")
    
    args = parser.parse_args()
    
    report = run_registry_runtime_trace(args.db, args.query, args.limit)
    print(json.dumps(report, indent=2))
