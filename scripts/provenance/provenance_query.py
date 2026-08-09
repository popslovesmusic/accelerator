import json
import argparse
import os
try:
    from scripts.provenance.build_causal_provenance import build_causal_provenance
except ImportError:
    import sys
    sys.path.append(os.path.dirname(__file__))
    from build_causal_provenance import build_causal_provenance

def query_provenance(query, db_path, limit=20):
    graph = build_causal_provenance(db_path)
    if "error" in graph: return graph

    # Filter graph for relevant chains
    results = {
        "query": query,
        "matching_nodes": [],
        "lineage_chains": []
    }

    # Find nodes matching query
    for node in graph["nodes"]:
        if query.lower() in node["id"].lower() or query.lower() in node.get("label", "").lower():
            results["matching_nodes"].append(node)

    # For each matching node, find direct neighbors (1-hop for now)
    for node in results["matching_nodes"]:
        chain = {"origin": node, "edges": []}
        for edge in graph["edges"]:
            if edge["from"] == node["id"] or edge["to"] == node["id"]:
                chain["edges"].append(edge)
        results["lineage_chains"].append(chain)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query causal provenance.")
    parser.add_argument("--query", required=True, help="Keyword for lineage lookup.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=20, help="Limit results.")
    
    args = parser.parse_args()
    res = query_provenance(args.query, args.db, args.limit)
    print(json.dumps(res, indent=2))
