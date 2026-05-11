import json
import argparse
import os
try:
    from scripts.gemini_claim_context import generate_gemini_packet
    from scripts.db.db_health_check import run_db_health_check
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from gemini_claim_context import generate_gemini_packet
    from db.db_health_check import run_db_health_check

def generate_execution_context(query, db_path, limit=10):
    # 1. Get Claim Context (Reasoning)
    claim_context = generate_gemini_packet(query, db_path, limit=limit)
    
    # 2. Get DB Health
    db_health, _ = run_db_health_check(db_path, "registry/db/schema.sql")
    
    packet = {
        "gemini_execution_context": {
            "query": query,
            "claim_reasoning": claim_context["reasoning_context"],
            "runtime_health": {
                "db_status": db_health["status"],
                "integrity": db_health["integrity_check"],
                "stale_warnings": db_health["stale_index_warnings"]
            },
            "governance_recommendations": [
                "Prioritize current command evidence over historical residue.",
                "Ensure mechanism independence for any proposed simulation.",
                "Verify lexicon L3 status before strong assertions."
            ]
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
