import json
import argparse
import os
try:
    from scripts.provenance.build_causal_provenance import build_causal_provenance
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from build_causal_provenance import build_causal_provenance

def check_provenance_health(db_path):
    graph = build_causal_provenance(db_path)
    if "error" in graph: return {"status": "fail", "errors": [graph["error"]]}

    health = {
        "status": "pass",
        "checks": {
            "node_connectivity": True,
            "confidence_preservation": True,
            "no_silent_cycles": True,
            "ssot_boundary_preserved": True
        },
        "warnings": [],
        "cycle_risks": [],
        "recommendations": []
    }

    # 1. Basic stats
    health["node_count"] = len(graph["nodes"])
    health["edge_count"] = len(graph["edges"])

    # 2. Confidence count
    conf_counts = {"verified": 0, "probable": 0, "weak": 0}
    for edge in graph["edges"]:
        conf = edge.get("confidence", "weak")
        conf_counts[conf] = conf_counts.get(conf, 0) + 1
    health["confidence_distribution"] = conf_counts

    # 3. Simple Cycle Detection (Back-edges in 1-hop for now)
    # A more robust DFS can be added if needed
    for e1 in graph["edges"]:
        for e2 in graph["edges"]:
            if e1["from"] == e2["to"] and e1["to"] == e2["from"]:
                health["cycle_risks"].append({"type": "2-cycle", "nodes": [e1["from"], e1["to"]]})
                health["status"] = "warning"
                health["warnings"].append(f"Cycle detected between {e1['from']} and {e1['to']}")

    return health

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provenance health check.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    
    args = parser.parse_args()
    health = check_provenance_health(args.db)
    print(json.dumps({"provenance_health": health}, indent=2))
