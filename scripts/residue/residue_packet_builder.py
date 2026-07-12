import json
import argparse
import os
import hashlib
from datetime import datetime
try:
    from scripts.orientation_retrieval import retrieve_artifacts
    from scripts.provenance.build_causal_provenance import build_causal_provenance
    from tools.inference_governance.request_normalization import normalize_text
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from scripts.orientation_retrieval import retrieve_artifacts
    from scripts.provenance.build_causal_provenance import build_causal_provenance
    from tools.inference_governance.request_normalization import normalize_text

def build_residue_packet(query, db_path, mode="lossy_summary", limit=20):
    # 1. Retrieve artifacts and provenance for context
    normalized_query = normalize_text(query, lowercase=True)
    retrieval = retrieve_artifacts(db_path, normalized_query, limit=limit)
    prov = build_causal_provenance(db_path)
    
    packet = {
        "residue_packet": {
            "packet_id": f"RES-{hashlib.md5(f'{normalized_query}{datetime.now()}'.encode()).hexdigest()[:8]}",
            "query": query,
            "normalized_query": normalized_query,
            "generated_at": datetime.now().isoformat(),
            "compression_mode": mode,
            "source_artifacts": [a["path"] for a in retrieval.get("results", [])],
            "source_reports": [], # Logic to find related reports in DB
            "source_provenance_edges": [], # Filter prov edges
            "orientation_context": {
                "current_command_evidence": [a["path"] for a in retrieval.get("results", []) if a["orientation_status"] == "current_command_evidence"],
                "canonical_authority": [a["path"] for a in retrieval.get("results", []) if a["orientation_status"] == "canonical_active"],
                "historical_residue": [a["path"] for a in retrieval.get("results", []) if a["orientation_status"] in ["historical_residue", "archived"]],
                "supersession_cautions": [],
                "traceability_conflicts": []
            },
            "compressed_summary": f"Governance summary for '{normalized_query}' based on {len(retrieval.get('results', []))} artifacts.",
            "structured_facts": [],
            "open_uncertainties": ["Provenance edges are advisory.", "Historical residue requires verification."],
            "conflicts_preserved": [],
            "excluded_or_unread_sources": [],
            "evidence_links": [a["path"] for a in retrieval.get("results", [])],
            "confidence": "partial_summary",
            "candidate_policy_id": retrieval.get("candidate_policy_id"),
            "candidate_set_hash": retrieval.get("candidate_set_hash"),
            "candidate_exclusions": retrieval.get("candidate_exclusions", []),
            "warnings": [
                "Compressed residue is not source of truth.",
                "Original evidence must be consulted for claim promotion."
            ]
        }
    }
    
    # Simple logic to add facts from artifacts
    for res in retrieval.get("results", []):
        if "cautions" in res:
            packet["residue_packet"]["orientation_context"]["supersession_cautions"].extend(res["cautions"])

    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build structured residue packets.")
    parser.add_argument("--query", required=True, help="Topic for residue packet.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to database.")
    parser.add_argument("--mode", default="lossy_summary", help="Compression mode.")
    parser.add_argument("--limit", type=int, default=20, help="Limit sources.")
    
    args = parser.parse_args()
    packet = build_residue_packet(args.query, args.db, args.mode, args.limit)
    print(json.dumps(packet, indent=2))
