import json
import os
import subprocess
from datetime import datetime

def generate_session_report():
    report_path = "outputs/audits/session_oversight_report.json"
    
    # 1. Run all sub-monitors
    scripts = [
        "scripts/generate_equivalence_dashboard.py",
        "scripts/monitor_campaign_progress.py",
        "scripts/generate_human_attention_queue.py",
        "scripts/suggest_next_action.py",
        "scripts/translate_governance_state.py",
        "scripts/track_evidence_gaps.py"
    ]
    
    for script in scripts:
        subprocess.run(["python", script])

    # 2. Aggregate into concise summary
    report = {
        "session_timestamp": datetime.now().isoformat(),
        "executive_summary": "",
        "key_metrics": {},
        "human_attention_needed": False,
        "next_step": ""
    }

    # Load dash for metrics
    with open("outputs/audits/equivalence_dashboard.json", 'r') as f:
        dash = json.load(f)
        report["key_metrics"]["warnings_remaining"] = dash["summary"]["warnings_remaining"]

    # Load queue for attention
    with open("outputs/audits/human_attention_queue.json", 'r') as f:
        queue = json.load(f)
        report["human_attention_needed"] = len(queue["items"]) > 0

    # Load next action
    with open("outputs/audits/next_best_action.json", 'r') as f:
        action = json.load(f)
        report["next_step"] = action["recommended_action"]

    # Final summary text
    if report["key_metrics"]["warnings_remaining"] > 0:
        report["executive_summary"] = f"Stabilization phase is active. {report['key_metrics']['warnings_remaining']} C4 tools are still awaiting equivalence baseline emission."
    else:
        report["executive_summary"] = "All C4 core engine families have verified equivalence. System is at peak operational integrity."

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    print(f"Session Oversight Report generated: {report_path}")
    return report

if __name__ == "__main__":
    generate_session_report()
