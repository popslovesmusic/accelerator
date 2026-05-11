import json
import argparse
import os
try:
    from scripts.orientation_retrieval import retrieve_artifacts
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from orientation_retrieval import retrieve_artifacts

def retrieve_memory_context(db_path, query, limit=20):
    """
    Retrieve orientation-aware context for agent memory.
    Prioritizes current evidence and canonical authority.
    """
    retrieval = retrieve_artifacts(db_path, query, limit=limit, explain=True)
    
    context = {
        "query": query,
        "retrieved_at": os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip(),
        "artifacts": retrieval.get("results", []),
        "warnings": retrieval.get("warnings", [])
    }
    
    # Identify residue
    for art in context["artifacts"]:
        if art["orientation_status"] in ["historical_residue", "superseded", "deprecated", "archived"]:
            art["is_residue"] = True
        else:
            art["is_residue"] = False
            
    return context

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Governed memory retrieval.")
    parser.add_argument("--query", required=True, help="Query for memory context.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=20, help="Result limit.")
    
    args = parser.parse_args()
    ctx = retrieve_memory_context(args.db, args.query, args.limit)
    print(json.dumps(ctx, indent=2))
