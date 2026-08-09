import json
import os
from datetime import datetime

def monitor_campaign_progress():
    campaigns_dir = "outputs/evidence_campaigns/"
    monitor_path = "outputs/audits/campaign_progress_monitor.json"
    
    progress = {
        "timestamp": datetime.now().isoformat(),
        "active_campaigns": [],
        "completed_campaigns": [],
        "blockers": []
    }

    if os.path.exists(campaigns_dir):
        for file in os.listdir(campaigns_dir):
            if file.endswith("_result.json"):
                with open(os.path.join(campaigns_dir, file), 'r') as f:
                    res = json.load(f)
                progress["completed_campaigns"].append({
                    "id": res.get("campaign_id"),
                    "verdict": res.get("overall_status"),
                    "timestamp": res.get("timestamp")
                })

    os.makedirs(os.path.dirname(monitor_path), exist_ok=True)
    with open(monitor_path, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2)
        
    return progress

if __name__ == "__main__":
    monitor_campaign_progress()
