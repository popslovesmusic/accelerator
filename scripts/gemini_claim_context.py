import argparse
import json
import os

try:
    from scripts.query_governance import build_governed_context_capsule_v1
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from query_governance import build_governed_context_capsule_v1


def generate_gemini_packet(query, db_path, limit=20):
    capsule = build_governed_context_capsule_v1(db_path, query=query, limit=limit)
    artifacts = capsule.get("relevant_artifacts", [])
    graph_summary = capsule.get("runtime_trace", {}).get("claim_graph_summary", {})
    trace_report = capsule.get("runtime_trace", {}).get("trace_report", {})
    orientation_distribution = {}
    cautions = []

    for artifact in artifacts:
        status = artifact.get("orientation_status")
        if status:
            orientation_distribution[status] = orientation_distribution.get(status, 0) + 1
        if status in ["historical_residue", "superseded", "deprecated", "archived"]:
            cautions.append(f"Query returned {status} artifact: {artifact.get('path')}")
        cautions.extend(artifact.get("cautions", []))

    cautions.extend(trace_report.get("supersession_cautions", []))
    cautions.extend(capsule.get("warnings", []))
    cautions = list(dict.fromkeys([item for item in cautions if item]))

    packet = {
        "reasoning_context": {
            "query": query,
            "top_artifacts": artifacts,
            "graph_summary": {
                "nodes_count": graph_summary.get("nodes_count", 0),
                "edges_count": graph_summary.get("edges_count", 0),
            },
            "orientation_distribution": orientation_distribution,
            "cautions": cautions,
        }
    }

    print(json.dumps(packet, indent=2))
    return packet


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Gemini-safe reasoning packets.")
    parser.add_argument("--query", required=True, help="Query for context generation.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=10, help="Limit results.")

    args = parser.parse_args()
    generate_gemini_packet(args.query, args.db, args.limit)
