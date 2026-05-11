import json
import argparse
import os

def check_residue_health(packet_path):
    if not os.path.exists(packet_path):
        return {"status": "fail", "errors": ["File not found."]}
        
    try:
        with open(packet_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return {"status": "fail", "errors": [str(e)]}

    health = {
        "status": "pass",
        "checks": {
            "packet_schema_valid": "residue_packet" in data or ("content" in data and "residue_packet" in data["content"]),
            "orientation_labels_present": False,
            "evidence_links_present": False,
            "non_authority_warnings_present": False
        },
        "warnings": [],
        "recommendations": []
    }
    
    # Unwrap if saved via save_report
    packet = data.get("content", {}).get("residue_packet") or data.get("residue_packet")
    
    if packet:
        health["checks"]["orientation_labels_present"] = bool(packet.get("orientation_context"))
        health["checks"]["evidence_links_present"] = bool(packet.get("evidence_links"))
        health["checks"]["non_authority_warnings_present"] = any("not source of truth" in w.lower() for w in packet.get("warnings", []))
    
    if not all(health["checks"].values()):
        health["status"] = "warning"
        health["warnings"].append("Residue packet is missing mandatory governance labels or links.")
        
    return health

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Residue health checker.")
    parser.add_argument("--path", required=True, help="Path to residue packet.")
    
    args = parser.parse_args()
    health = check_residue_health(args.path)
    print(json.dumps({"residue_health": health}, indent=2))
