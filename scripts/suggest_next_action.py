import json
import os
from datetime import datetime

def suggest_next_action():
    manifest_path = "registry/tool_manifest.json"
    action_path = "outputs/audits/next_best_action.json"
    
    suggestion = {
        "timestamp": datetime.now().isoformat(),
        "recommended_action": "None",
        "reason": "System is stable and all baselines are emitted.",
        "risk": "Low",
        "expected_impact": "None"
    }

    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8-sig') as f:
            manifest = json.load(f)
        
        # Priority 1: Clear C4 warnings
        next_tool = None
        for tool in manifest.get("tools", []):
            if tool.get("certification_level") == "C4" and tool.get("implementation_language") in ["cpp", "hybrid"]:
                if tool.get("latest_equivalence_packet") == "NONE" and tool.get("reference_baseline") != "NOT_DECLARED":
                    next_tool = tool["name"]
                    break
        
        if next_tool:
            suggestion["recommended_action"] = f"Emit equivalence baseline for {next_tool}."
            suggestion["reason"] = f"Tool is marked C4 but lacks recoverable equivalence evidence required by current governance."
            suggestion["expected_impact"] = "Reduces remaining C4 health warnings in global audit."

    os.makedirs(os.path.dirname(action_path), exist_ok=True)
    with open(action_path, 'w', encoding='utf-8') as f:
        json.dump(suggestion, f, indent=2)
        
    return suggestion

if __name__ == "__main__":
    suggest_next_action()
