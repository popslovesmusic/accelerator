import hashlib
import json
import subprocess
from pathlib import Path

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()

def load(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)

def snapshot(root, relative_paths):
    entries = []
    for rel in sorted(relative_paths):
        path = root / rel
        entries.append({"path": rel, "exists": path.is_file(), "sha256": sha256(path) if path.is_file() else None})
    manifest = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    return {"repository_root": str(root), "commit_id": commit, "snapshot_hash": hashlib.sha256(manifest).hexdigest().upper(), "dirty_state": dirty, "included_paths": sorted(relative_paths), "excluded_paths": [".git", "crawl_engine/cache"], "source_files": entries}

def inventory(root, focus, config):
    lexicon = load(root / "registry/lexicon_gap_queue.json")
    wanted = set(focus or config.get("focus_objects", []))
    aliases = {"symmetry_condition_relation": "symmetry_condition_relation", "symmetry_condition": "symmetry_condition", "bounded_symmetry": "bounded_symmetry", "unbounded_symmetry": "unbounded_symmetry", "dominant_domain_projection": "dominant_domain_projection", "distinction_permitting_symmetry_condition": "distinction_permitting_symmetry_condition"}
    items = []
    for entry in lexicon.get("queue", []):
        term = entry.get("term")
        if term not in wanted:
            continue
        status = entry.get("status", "GAP_OPEN")
        formal = "PROVISIONALLY_DEFINED" if status == "C1_DEFINED_PROVISIONAL" else "BLOCKED" if status == "GAP_OPEN" else "SUPERSEDED" if status == "RESOLVED_TO_ALIAS" else "UNDEFINED"
        classification = "NOTATION_ALIAS" if term == "distinction_permitting_symmetry_condition" else "PRIMITIVE_DEFINITION" if term in {"bounded_symmetry", "unbounded_symmetry"} else "DERIVED_DEFINITION"
        object_id = aliases.get(term, term)
        notation = {"symmetry_condition_relation":"|","symmetry_condition":"S","bounded_symmetry":"<S>","unbounded_symmetry":">S<","dominant_domain_projection":"Π_(D,A_D)","distinction_permitting_symmetry_condition":"(*|*)"}.get(object_id)
        items.append({"object_id": object_id, "canonical_name": term, "notation": notation, "primary_classification": classification, "formal_status": formal, "epistemic_status": "SOURCE_REPORTED", "proof_status": "OBLIGATIONS_IDENTIFIED" if formal != "SUPERSEDED" else "NOT_ATTEMPTED", "confidence": "HIGH", "risk": "CRITICAL" if term in {"symmetry_condition_relation", "dominant_domain_projection"} else "HIGH", "source_artifact":"registry/lexicon_gap_queue.json", "source_location":f"queue term={term}"})
    return sorted(items, key=lambda item: item["object_id"])

def enrich_source_hashes(items, snapshot_data):
    source_hash = next((x["sha256"] for x in snapshot_data["source_files"] if x["path"] == "registry/lexicon_gap_queue.json"), None)
    for item in items:
        item["source_hash"] = source_hash
    return items

def cycles(graph):
    raw_nodes = graph.get("nodes", [])
    node_ids = [node.get("id") if isinstance(node, dict) else node for node in raw_nodes]
    adjacency = {}
    for edge in graph.get("edges", []):
        adjacency.setdefault(edge["from"], []).append(edge["to"])
    found = []
    def visit(node, path, active):
        if node in active:
            found.append(path[path.index(node):] + [node])
            return
        if node in path:
            return
        for child in sorted(adjacency.get(node, [])):
            visit(child, path + [node], active | {node})
    for node in sorted(node_ids):
        visit(node, [], set())
    unique = {}
    for path in found:
        ring = path[:-1]
        rotations = [tuple(ring[i:] + ring[:i]) for i in range(len(ring))]
        key = min(rotations)
        unique[key] = list(key) + [key[0]]
    return [unique[key] for key in sorted(unique)]

def delta(current, previous):
    now = {x["object_id"]: x for x in current}
    old = {x["object_id"]: x for x in previous.get("object_inventory", [])}
    return {"baseline_report": "departments/analysis/crawl_reports/analysis_crawl_20260731_symmetry_relation_refined_001.json", "added": sorted(set(now)-set(old)), "modified": sorted(k for k in set(now)&set(old) if now[k] != old[k]), "superseded": sorted(k for k in set(now)&set(old) if now[k].get("formal_status") == "SUPERSEDED" and old[k].get("formal_status") != "SUPERSEDED"), "removed": sorted(set(old)-set(now)), "status_changed": sorted(k for k in set(now)&set(old) if now[k].get("formal_status") != old[k].get("formal_status")), "newly_blocked": sorted(k for k in set(now)&set(old) if now[k].get("formal_status") == "BLOCKED" and old[k].get("formal_status") != "BLOCKED"), "newly_unblocked": [], "unchanged_critical_objects": sorted(k for k in set(now)&set(old) if now[k] == old[k])}
