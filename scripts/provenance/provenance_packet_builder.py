import json
import argparse
import os
try:
    from scripts.provenance.provenance_query import query_provenance
    from scripts.db.db_health_check import run_db_health_check
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from provenance_query import query_provenance
    from db.db_health_check import run_db_health_check

def build_provenance_packet(query, db_path, limit=20):
    trace = query_provenance(query, db_path, limit)
    db_health, _ = run_db_health_check(db_path, "registry/db/schema.sql")

    packet = {
        "provenance_packet": {
            "packet_id": f"PROV-{os.popen('powershell -Command \"[guid]::NewGuid().ToString()\"').read().strip()[:8]}",
            "query": query,
            "generated_at": os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip(),
            "orientation_context": {
                "current_command_evidence": [],
                "canonical_authority": [],
                "historical_residue": [],
                "supersession_cautions": [],
                "traceability_conflicts": []
            },
            "nodes": trace.get("matching_nodes", []),
            "edges": [],
            "verified_edges": [],
            "probable_edges": [],
            "weak_edges": [],
            "cycle_risks": [],
            "conflicts": [],
            "missing_links": [],
            "recommended_next_actions": [],
            "warnings": []
        }
    }

    # Populate edges and sort by confidence
    for chain in trace.get("lineage_chains", []):
        for edge in chain["edges"]:
            packet["provenance_packet"]["edges"].append(edge)
            conf = edge.get("confidence", "weak")
            if conf == "verified": packet["provenance_packet"]["verified_edges"].append(edge)
            elif conf == "probable": packet["provenance_packet"]["probable_edges"].append(edge)
            else: packet["provenance_packet"]["weak_edges"].append(edge)

    # Orientation classification
    for node in packet["provenance_packet"]["nodes"]:
        orient = node.get("orientation")
        if orient == "current_command_evidence":
            packet["provenance_packet"]["orientation_context"]["current_command_evidence"].append(node["id"])
        elif orient == "canonical_active":
            packet["provenance_packet"]["orientation_context"]["canonical_authority"].append(node["id"])
        elif orient in ["historical_residue", "archived", "deprecated"]:
            packet["provenance_packet"]["orientation_context"]["historical_residue"].append(node["id"])

    packet["provenance_packet"]["recommended_next_actions"].append("Verify probable edges against current command evidence.")
    packet["provenance_packet"]["recommended_next_actions"].append("Report cycle risks in reasoning summaries.")

    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build provenance packet.")
    parser.add_argument("--query", required=True, help="Keyword for provenance packet.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--limit", type=int, default=20, help="Limit lookup depth.")
    
    args = parser.parse_args()
    packet = build_provenance_packet(args.query, args.db, args.limit)
    print(json.dumps(packet, indent=2))
