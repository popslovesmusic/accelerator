import json
import os
from datetime import datetime

def generate_human_attention_queue():
    queue_path = "outputs/audits/human_attention_queue.json"
    manifest_path = "registry/tool_manifest.json"
    failures_dir = "outputs/audits/equivalence/failures/"
    
    queue = {
        "timestamp": datetime.now().isoformat(),
        "items": []
    }

    # 1. Failed Equivalence Runs
    if os.path.exists(failures_dir):
        for file in os.listdir(failures_dir):
            queue["items"].append({
                "type": "FAILED_EQUIVALENCE",
                "artifact": file,
                "judgment_required": "Review divergence and determine if tolerance adjustment or code fix is needed."
            })

    # 2. C4 tools with NO reference baseline
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8-sig') as f:
            manifest = json.load(f)
        for tool in manifest.get("tools", []):
            if tool.get("certification_level") == "C4" and tool.get("implementation_language") in ["cpp", "hybrid"]:
                if tool.get("reference_baseline") == "NOT_DECLARED":
                    queue["items"].append({
                        "type": "MISSING_REFERENCE_BASELINE",
                        "tool": tool["name"],
                        "judgment_required": "Assign an authoritative Python reference baseline for this C4 tool."
                    })

    os.makedirs(os.path.dirname(queue_path), exist_ok=True)
    with open(queue_path, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2)
        
    return queue

if __name__ == "__main__":
    generate_human_attention_queue()
