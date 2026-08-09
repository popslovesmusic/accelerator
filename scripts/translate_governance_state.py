import json
import os
from datetime import datetime

def translate_governance_state():
    health_path = "outputs/audits/global_health_report.json"
    translation_path = "outputs/audits/plain_english_status.json"
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "summary": "Unknown",
        "details": []
    }

    if os.path.exists(health_path):
        with open(health_path, 'r') as f:
            health = json.load(f)
        
        if health.get("overall_status") == "pass":
            status["summary"] = "The ecosystem is stable and follows all governance rules."
        else:
            status["summary"] = "The ecosystem has active issues requiring attention."
        
        # Translate math validation
        mv = health.get("math_validation", {})
        if mv.get("status") == "success":
            status["details"].append("Mathematical foundations are locked and verified.")
        
        # Translate implementation warnings
        iv = health.get("implementation_validation", {})
        warnings = iv.get("warnings", [])
        if warnings:
            status["details"].append(f"There are {len(warnings)} tools that still need implementation-equivalence proof.")

    os.makedirs(os.path.dirname(translation_path), exist_ok=True)
    with open(translation_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2)
        
    return status

if __name__ == "__main__":
    translate_governance_state()
