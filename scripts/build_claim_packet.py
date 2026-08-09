import json
import os
import argparse
import sqlite3

def build_claim_packet(claim_id, db_path="registry/db/acellorator_index.sqlite"):
    # This is a read-only assembler
    packet = {
        "claim_id": claim_id,
        "assembled_at": os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip(),
        "registry_entries": {},
        "evidence_links": [],
        "supersession_cautions": [],
        "orientation_status": "unknown",
        "evidence_confidence": "not_checked",
        "recommended_classification": "no_promotion"
    }
    
    # 1. SSOT Registry Lookup
    claim_registry_path = 'registry/claim_registry.json'
    if os.path.exists(claim_registry_path):
        with open(claim_registry_path, 'r') as f:
            claims = json.load(f).get('claims', [])
            for c in claims:
                if c.get('claim_id') == claim_id:
                    packet["registry_entries"]["claim"] = c
                    break

    # 2. Database Projection Lookup
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get evidence links
        cursor.execute("SELECT * FROM claim_evidence_links WHERE claim_id = ?", (claim_id,))
        links = cursor.fetchall()
        for link in links:
            packet["evidence_links"].append({
                "path": link["source_path"],
                "status": link["orientation_status"]
            })
            
            # Check for supersession
            cursor.execute("""
                SELECT a2.path as active_path, s.relation
                FROM supersession_edges s
                JOIN artifacts a1 ON s.from_artifact_id = a1.id
                JOIN artifacts a2 ON s.to_artifact_id = a2.id
                WHERE a1.path = ?
            """, (link["source_path"],))
            shadow = cursor.fetchone()
            if shadow:
                packet["supersession_cautions"].append(f"Evidence {link['source_path']} is {shadow['relation']} {shadow['active_path']}")

        conn.close()
                    
    print(json.dumps(packet, indent=2))
    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble a claim evidence packet.")
    parser.add_argument("claim_id", help="ID of the claim to assemble.")
    args = parser.parse_args()
    
    build_claim_packet(args.claim_id)
