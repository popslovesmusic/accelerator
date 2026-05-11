import json
import argparse
import os
try:
    from scripts.registry_runtime_trace import run_registry_runtime_trace
    from scripts.db.db_health_check import run_db_health_check
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from registry_runtime_trace import run_registry_runtime_trace
    from db.db_health_check import run_db_health_check

def generate_trace_context(query, db_path, limit=20):
    # 1. Run Traceability Report
    trace = run_registry_runtime_trace(db_path, query, limit)
    
    # 2. Get DB Health context
    db_health, _ = run_db_health_check(db_path, "registry/db/schema.sql")
    
    packet = {
        "gemini_trace_context": {
            "query": query,
            "trace_summary": {
                "entities_count": len(trace["trace_report"]["trace_entities"]),
                "edges_count": len(trace["trace_report"]["trace_edges"]),
                "resolved_links_count": len(trace["trace_report"]["resolved_links"]),
                "missing_links_count": len(trace["trace_report"]["missing_links"])
            },
            "resolved_links": trace["trace_report"]["resolved_links"][:10], # Top 10
            "missing_links": trace["trace_report"]["missing_links"][:10],
            "orientation_cautions": trace["trace_report"]["supersession_cautions"],
            "db_status": db_health["status"],
            "governance_rules": [
                "Traceability is advisory and observational only.",
                "Registry definitions (lexicon/math) are SSOT and must not be overridden by DB links.",
                "Missing links indicate gaps in runtime evidence or validation, not framework failure."
            ]
        },
        "raw_trace": trace
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
