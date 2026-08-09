import argparse
import json
import os

try:
    from scripts.query_governance import build_governed_context_capsule_v1
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from query_governance import build_governed_context_capsule_v1


def generate_trace_context(query, db_path, limit=20):
    capsule = build_governed_context_capsule_v1(db_path, query=query, limit=limit)
    trace_report = capsule.get("runtime_trace", {}).get("trace_report", {})
    db_health = capsule.get("database_health", {})

    packet = {
        "gemini_trace_context": {
            "query": query,
            "trace_summary": {
                "entities_count": trace_report.get("trace_summary", {}).get("entities_count", 0),
                "edges_count": trace_report.get("trace_summary", {}).get("edges_count", 0),
                "resolved_links_count": trace_report.get("trace_summary", {}).get("resolved_links_count", 0),
                "missing_links_count": trace_report.get("trace_summary", {}).get("missing_links_count", 0),
            },
            "resolved_links": trace_report.get("resolved_links", [])[:10],
            "missing_links": trace_report.get("missing_links", [])[:10],
            "orientation_cautions": trace_report.get("supersession_cautions", []),
            "db_status": db_health.get("status", "unknown"),
            "governance_rules": [
                "Traceability is advisory and observational only.",
                "Registry definitions (lexicon/math) are SSOT and must not be overridden by DB links.",
                "Missing links indicate gaps in runtime evidence or validation, not framework failure.",
            ],
        },
        "raw_trace": {
            "trace_report": trace_report,
            "claim_graph_summary": capsule.get("runtime_trace", {}).get("claim_graph_summary", {}),
            "database_health": db_health,
        },
    }

    print(json.dumps(packet, indent=2))
    return packet


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Gemini-safe traceability context.")
    parser.add_argument("--query", required=True, help="Topic for trace context.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=20, help="Limit trace depth.")

    args = parser.parse_args()
    generate_trace_context(args.query, args.db, args.limit)
