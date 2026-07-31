import json

def write_json(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def write_summary(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Governed Crawl Report", "", "## Current State", "", f"Objects analyzed: {len(report['mathematical_inventory'])}", f"Cycles: {len(report['cycle_analysis']['cycles'])}", f"Outcome: {report['campaign_assessment']['outcome']}", "", "## Blockers", ""]
    lines.extend(f"- `{x['blocker_type']}`: {x['dependency']}" for x in report["blockers"])
    lines.extend(["", "## Not Established", ""])
    lines.extend(f"- {x}" for x in report["not_established"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
