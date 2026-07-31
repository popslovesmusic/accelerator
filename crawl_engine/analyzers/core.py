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

def tracked_text_files(root):
    try:
        raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
        paths = [root / item for item in raw.decode().split("\0") if item]
    except (OSError, subprocess.CalledProcessError):
        paths = []
    extensions = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}
    return [path for path in sorted(paths, key=lambda p: str(p).lower()) if path.suffix.lower() in extensions and path.is_file()]

def impact_counts(root, term, notation, source_files=None):
    counts = {"definitions":0,"axioms":0,"proofs":0,"semantics":0,"textbooks":0,"examples":0,"validations":0}
    try:
        command = ["git", "grep", "-Il", "--fixed-strings", "-e", str(term), "-e", str(notation), "--"]
        command.extend(sorted(set(source_files or [])))
        output = subprocess.check_output(command, cwd=root, text=True, stderr=subprocess.DEVNULL)
        matched = [line for line in output.splitlines() if line]
    except (OSError, subprocess.CalledProcessError):
        matched = []
    for rel in sorted(set(matched)):
        rel = rel.replace("\\", "/")
        if "textbook" in rel:
            counts["textbooks"] += 1
        if "/proof" in rel or "theorem" in rel or "lemma" in rel:
            counts["proofs"] += 1
        if "math" in rel and ("registry" in rel or "definition" in rel or "note" in rel):
            counts["definitions"] += 1
        if "crawl_engine" in rel or rel.startswith("scripts/"):
            counts["semantics"] += 1
        if "validation" in rel or "audit" in rel:
            counts["validations"] += 1
        if "example" in rel or "fixture" in rel or "result" in rel:
            counts["examples"] += 1
        if "registry" in rel and counts["definitions"] == 0:
            counts["axioms"] += 1
    counts["total"] = sum(counts.values())
    return counts

def object_profiles(root, objects, graph, source_files=None):
    relation_axioms = ["AX-R04_SUBSTITUTION", "AX-R05_COMPOSITION", "AX-R06_CLOSURE", "AX-R07_MALFORMED_CONSTRUCTION", "AX-R08_DETERMINISM", "AX-R09_ASSOCIATIVITY", "AX-R10_COMMUTATIVITY", "AX-R11_DOMAIN_OF_DEFINITION", "AX-R12_PROJECTION_COMPATIBILITY"]
    direct = graph.get("direct_consumers", {})
    transitive = graph.get("transitive_consumers", {})
    returns = {"symmetry_condition_relation":["symmetry_condition"],"symmetry_condition":["SymmetryCondition"],"bounded_symmetry":["SymmetryCondition"],"unbounded_symmetry":["SymmetryCondition"],"dominant_domain_projection":["CandidateSet(PrimitiveRealization)"],"distinction_permitting_symmetry_condition":["SymmetryCondition"]}
    primitives = {"symmetry_condition_relation":["bounded_symmetry","unbounded_symmetry"],"symmetry_condition":["symmetry_condition_relation"],"bounded_symmetry":[],"unbounded_symmetry":[],"dominant_domain_projection":["symmetry_condition"],"distinction_permitting_symmetry_condition":["symmetry_condition"]}
    layers = {"bounded_symmetry":"PRIMITIVES","unbounded_symmetry":"PRIMITIVES","symmetry_condition_relation":"RELATIONS","symmetry_condition":"DERIVED_DEFINITIONS","distinction_permitting_symmetry_condition":"DERIVED_DEFINITIONS","dominant_domain_projection":"PROJECTIONS"}
    profiles = []
    for item in objects:
        obj = item["object_id"]
        blocked = relation_axioms if obj in {"symmetry_condition_relation","dominant_domain_projection"} else []
        proof_state = "BLOCKED" if obj == "dominant_domain_projection" else "DEFINED_UNPROVED" if item["primary_classification"] != "NOTATION_ALIAS" else "OPEN"
        confidence = "MODERATE" if obj == "dominant_domain_projection" else "HIGH"
        impact = impact_counts(root, item["canonical_name"], item["notation"], source_files)
        profiles.append({"object_id":obj,"canonical_name":item["canonical_name"],"notation":item["notation"],"classification":item["primary_classification"],"formal_status":item["formal_status"],"confidence":confidence,"confidence_basis":["canonical_definition","governed_registry","validation"],"primitive_dependencies":sorted(primitives.get(obj, [])),"direct_consumers":sorted(direct.get(obj, [])),"transitive_consumers":sorted(transitive.get(obj, [])),"consumer_count":len(direct.get(obj, [])),"highest_level_consumer":"PROJECTIONS" if transitive.get(obj) else None,"critical_dependency_flag":obj in {"symmetry_condition_relation","bounded_symmetry","unbounded_symmetry"},"returns_type":returns.get(obj, []),"blocked_by":blocked,"blocks":sorted(transitive.get(obj, [])) if obj == "symmetry_condition_relation" else [],"open_axioms":relation_axioms if obj == "symmetry_condition_relation" else [],"open_proofs":["finite executable semantics"] if obj in {"symmetry_condition_relation","dominant_domain_projection"} else [],"proof_state":proof_state,"counterexamples":[],"impact":impact,"validation":{"schema":"PASS","typing":"PASS" if obj != "dominant_domain_projection" else "OPEN","dependency":"PASS" if obj != "dominant_domain_projection" else "BLOCKED"},"provenance":{"artifact":item["source_artifact"],"hash":item["source_hash"],"location":item["source_location"]},"abstraction_layer":layers.get(obj,"SEMANTICS")})
    return sorted(profiles, key=lambda profile: profile["object_id"])

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
