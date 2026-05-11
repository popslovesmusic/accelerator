import os
import json
import argparse
from datetime import datetime
try:
    from scripts.orientation_status_check import classify_path
except ImportError:
    from orientation_status_check import classify_path

def save_report(content, path, task_id, orientation=None, force=False):
    if os.path.exists(path) and not force:
        print(f"Error: Report already exists at {path}. Use --force to overwrite.")
        return False
    
    if orientation is None:
        orientation = classify_path(path)
    
    # Wrap content with metadata if it's a dict
    if isinstance(content, dict):
        report_data = {
            "audit_metadata": {
                "id": os.path.basename(path).replace('.json', ''),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "task_id": task_id,
                "evidence_orientation": orientation
            },
            "content": content
        }
    else:
        report_data = content

    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'w') as f:
        if path.endswith('.json'):
            json.dump(report_data, f, indent=2)
        else:
            f.write(report_data)
    
    print(f"Report saved to {path} (Orientation: {orientation})")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save a report with metadata.")
    parser.add_argument("path", help="Path to save the report.")
    parser.add_argument("--task_id", required=True, help="Task ID associated with the report.")
    parser.add_argument("--content", help="JSON string or file path for content.")
    parser.add_argument("--orientation", help="Orientation status (default: auto-classify).")
    parser.add_argument("--force", action="store_true", help="Overwrite existing report.")
    
    args = parser.parse_args()
    
    # Load content
    if args.content.startswith('{'):
        content = json.loads(args.content)
    elif os.path.exists(args.content):
        with open(args.content, 'r') as f:
            content = json.load(f) if args.content.endswith('.json') else f.read()
    else:
        content = args.content
        
    save_report(content, args.path, args.task_id, args.orientation, args.force)
