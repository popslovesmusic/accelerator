import json
import os
import argparse

def build_claim_packet(claim_id):
    # This is a read-only assembler
    packet = {
        "claim_id": claim_id,
        "assembled_at": os.popen('date /t').read().strip() + " " + os.popen('time /t').read().strip(),
        "registry_entries": {},
        "evidence_links": []
    }
    
    # Mock lookup in claim registry (read-only)
    claim_registry_path = 'registry/claim_registry.json'
    if os.path.exists(claim_registry_path):
        with open(claim_registry_path, 'r') as f:
            claims = json.load(f).get('claims', [])
            for c in claims:
                if c.get('claim_id') == claim_id:
                    packet["registry_entries"]["claim"] = c
                    break
                    
    print(json.dumps(packet, indent=2))
    return packet

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble a claim evidence packet.")
    parser.add_argument("claim_id", help="ID of the claim to assemble.")
    args = parser.parse_args()
    
    build_claim_packet(args.claim_id)
