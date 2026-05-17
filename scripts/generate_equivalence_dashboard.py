import json
import os
from pathlib import Path
from datetime import datetime

def generate_equivalence_dashboard():
    manifest_path = "registry/tool_manifest.json"
    dashboard_path = "outputs/audits/equivalence_dashboard.json"
    
    if not os.path.exists(manifest_path):
        return {"status": "error", "message": "Tool manifest missing."}

    with open(manifest_path, 'r', encoding='utf-8-sig') as f:
        manifest = json.load(f)

    c4_tools = []
    for tool in manifest.get("tools", []):
        if tool.get("certification_level") == "C4" and tool.get("implementation_language") in ["cpp", "hybrid", "cuda"]:
            status = "CLEARED" if tool.get("latest_equivalence_packet") != "NONE" else "WARNING"
            c4_tools.append({
                "name": tool["name"],
                "status": status,
                "packet": tool.get("latest_equivalence_packet"),
                "reference": tool.get("reference_baseline")
            })

    warnings_count = sum(1 for t in c4_tools if t["status"] == "WARNING")
    
    dashboard = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_c4_performance_tools": len(c4_tools),
            "warnings_remaining": warnings_count,
            "cleared_count": len(c4_tools) - warnings_count
        },
        "tool_states": c4_tools,
        "governance_boilerplate": {
            "source_relation": "(E≠0) ⇔R δ(E>0)",
            "non_separability_acknowledged": True
        }
    }

    os.makedirs(os.path.dirname(dashboard_path), exist_ok=True)
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2)
        
    return dashboard

if __name__ == "__main__":
    generate_equivalence_dashboard()
