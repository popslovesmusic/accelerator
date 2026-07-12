import argparse
import json
import os

try:
    from scripts.query_governance import build_governed_context_capsule_v1
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from query_governance import build_governed_context_capsule_v1


def generate_execution_context(query, db_path, limit=10):
    capsule = build_governed_context_capsule_v1(db_path, query=query, limit=limit)
    claim_reasoning = {
        "query": query,
        "top_artifacts": capsule.get("relevant_artifacts", []),
        "graph_summary": capsule.get("runtime_trace", {}).get("claim_graph_summary", {}),
        "orientation_distribution": {},
        "cautions": [],
    }

    for artifact in claim_reasoning["top_artifacts"]:
        status = artifact.get("orientation_status")
        if status:
            claim_reasoning["orientation_distribution"][status] = claim_reasoning["orientation_distribution"].get(status, 0) + 1
        if status in ["historical_residue", "superseded", "deprecated", "archived"]:
            claim_reasoning["cautions"].append(f"Query returned {status} artifact: {artifact.get('path')}")
        claim_reasoning["cautions"].extend(artifact.get("cautions", []))

    claim_reasoning["cautions"].extend(capsule.get("runtime_trace", {}).get("trace_report", {}).get("supersession_cautions", []))
    claim_reasoning["cautions"].extend(capsule.get("warnings", []))
    claim_reasoning["cautions"] = list(dict.fromkeys([item for item in claim_reasoning["cautions"] if item]))

    database_health = capsule.get("database_health", {})
    packet = {
        "gemini_execution_context": {
            "query": query,
            "claim_reasoning": claim_reasoning,
            "runtime_health": {
                "db_status": database_health.get("status", "unknown"),
                "integrity": database_health.get("integrity_check", "unknown"),
                "stale_warnings": database_health.get("stale_index_warnings", []),
            },
            "governance_recommendations": [
                f"{action.get('action_id')}: {action.get('reason')}"
                for action in capsule.get("candidate_actions", [])
            ],
        }
    }

    print(json.dumps(packet, indent=2))
    return packet


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Gemini-safe execution context.")
    parser.add_argument("--query", required=True, help="Query for context generation.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=10, help="Limit results.")

    args = parser.parse_args()
    generate_execution_context(args.query, args.db, args.limit)
