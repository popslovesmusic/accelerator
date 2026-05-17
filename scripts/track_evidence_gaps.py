import json
import os
from datetime import datetime

def track_evidence_gaps():
    manifest_path = "registry/tool_manifest.json"
    gap_path = "outputs/audits/evidence_gap_report.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "missing_packets": [],
        "stale_packets": [],
        "unlinked_reference": []
    }

    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8-sig') as f:
            manifest = json.load(f)
        
        for tool in manifest.get("tools", []):
            if tool.get("implementation_language") in ["cpp", "hybrid"]:
                # Check for missing packet
                if tool.get("latest_equivalence_packet") == "NONE":
                    report["missing_packets"].append(tool["name"])
                
                # Check for unlinked reference
                if tool.get("reference_baseline") == "NOT_DECLARED":
                    report["unlinked_reference"].append(tool["name"])

    os.makedirs(os.path.dirname(gap_path), exist_ok=True)
    with open(gap_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    track_evidence_gaps()
