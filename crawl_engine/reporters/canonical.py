import json

def write_json(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def write_summary(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Governed Crawl Report", "", "## Repository Snapshot", "", f"Commit: `{report['repository_snapshot']['commit_id']}`", f"Snapshot hash: `{report['repository_snapshot']['snapshot_hash']}`", f"Dirty state: `{report['repository_snapshot']['dirty_state']}`", "", "## Scope", "", "Focused crawl: `SymmetryConditionRelation` (`|`).", "", "## Objects Analyzed", ""]
    lines.extend(f"- `{x['object_id']}` — `{x['primary_classification']}` / `{x['formal_status']}` / notation `{x['notation']}`" for x in report["object_inventory"]["analyzed"])
    lines.extend(["", "## Dependency Summary", "", f"Nodes: {len(report['dependency_graph']['nodes'])}; edges: {len(report['dependency_graph']['edges'])}; cycles: {report['cycle_analysis']['cycle_count']}", ""])
    lines.extend(f"- `{x['from']}` --{x['type']}--> `{x['to']}`" for x in report["dependency_graph"]["edges"])
    lines.extend(["", "## Cycle Analysis", "", f"Cycle count: {report['cycle_analysis']['cycle_count']}", "", "## Direct Blockers", ""])
    lines.extend(f"- `{x['blocker_id']}` `{x['blocker_type']}` blocks `{', '.join(x['blocked_objects'])}`" for x in report["blockers"] if x["direct_or_propagated"] == "DIRECT")
    lines.extend(["", "## Propagated Blockers", ""])
    lines.extend(f"- `{x['blocker_id']}` propagates to `{', '.join(x['blocked_objects'])}` via `{x['dependency_paths']}`" for x in report["blockers"] if x["direct_or_propagated"] == "PROPAGATED")
    lines.extend(["", "## Proof State", "", f"Open obligations: {', '.join(report['proof_state']['open_obligations'])}", "", "## Not Established", ""])
    lines.extend(f"- {x}" for x in report["not_established"])
    lines.extend(["", "## Delta Since Prior Crawl", "", f"Added: {report['delta']['added']}", f"Modified: {report['delta']['modified']}", f"Status changed: {report['delta']['status_changed']}", "", "## Validation Results", "", json.dumps(report["validation"], sort_keys=True), "", "## Output Hashes", "", f"Canonical JSON hash: `{report['output_provenance']['canonical_json_hash']}`", f"Markdown hash: `{report['output_provenance']['markdown_hash']}`", "", "## Campaign Assessment", "", f"Outcome: `{report['campaign_assessment']['outcome']}`", f"Reason: {report['campaign_assessment']['reason_stopped']}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
