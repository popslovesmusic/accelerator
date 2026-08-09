import argparse
import json
import os

try:
    from scripts.query_governance import build_governed_context_capsule_v1
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from query_governance import build_governed_context_capsule_v1


def retrieve_memory_context(db_path, query, limit=20):
    capsule = build_governed_context_capsule_v1(db_path, query=query, limit=limit)
    return {
        "query": query,
        "retrieved_at": capsule.get("provenance", {}).get("built_at"),
        "artifacts": capsule.get("relevant_artifacts", []),
        "warnings": capsule.get("warnings", []),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Governed memory retrieval.")
    parser.add_argument("--query", required=True, help="Query for memory context.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=20, help="Result limit.")

    args = parser.parse_args()
    ctx = retrieve_memory_context(args.db, args.query, args.limit)
    print(json.dumps(ctx, indent=2))
