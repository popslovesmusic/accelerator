import json
import argparse
import os
try:
    from scripts.claim_evidence_graph import build_claim_evidence_graph
    from scripts.orientation_retrieval import retrieve_artifacts
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from claim_evidence_graph import build_claim_evidence_graph
    from orientation_retrieval import retrieve_artifacts

def generate_gemini_packet(query, db_path, limit=20):
    # 1. Retrieve relevant artifacts using orientation-aware scoring
    retrieval = retrieve_artifacts(db_path, query, limit=limit, explain=True)
    
    # 2. Build graph context
    graph = build_claim_evidence_graph(db_path)
    
    packet = {
        "reasoning_context": {
            "query": query,
            "top_artifacts": retrieval["results"],
            "graph_summary": {
                "nodes_count": len(graph.get("nodes", [])),
                "edges_count": len(graph.get("edges", []))
            },
            "orientation_distribution": {},
            "cautions": []
        }
    }
    
    # Calculate orientation distribution
    for res in retrieval["results"]:
        status = res["orientation_status"]
        packet["reasoning_context"]["orientation_distribution"][status] = packet["reasoning_context"]["orientation_distribution"].get(status, 0) + 1
        if status in ["historical_residue", "superseded", "deprecated"]:
            packet["reasoning_context"]["cautions"].append(f"Query returned {status} artifact: {res['path']}")

    print(json.dumps(packet, indent=2))
    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Gemini-safe reasoning packets.")
    parser.add_argument("--query", required=True, help="Query for context generation.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=10, help="Limit results.")
    
    args = parser.parse_args()
    generate_gemini_packet(args.query, args.db, args.limit)
