from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SURFACE_INVENTORY_PATH = ROOT / "outputs" / "governance_inventory" / "governance_surface_inventory.json"
DEFAULT_AMBIGUITY_REGISTER_PATH = ROOT / "outputs" / "governance_inventory" / "governance_ambiguity_register.json"
DEFAULT_SOURCE_SNAPSHOT_FILES = [
    "docs/manual_repository_audit_2026_07_13.md",
    "docs/textbook/mono_process_textbook_complete.md",
    "governance/core_rules/GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001.json",
    "governance/evidence_sets/GOVERNANCE_GLOBAL_INVENTORY_2026_07_13.json",
    "governance/provenance/governance_inventory_2026_07_13_provenance.json",
    "patches/PATCH_GOVERNANCE_INVENTORY_PROVENANCE_AND_ADDITIVE_AUTHORITY_004.json",
    "outputs/governance_inventory/governance_ambiguity_register.json",
    "outputs/governance_inventory/governance_authority_relationships.json",
    "outputs/governance_inventory/governance_inventory_summary.json",
    "outputs/governance_inventory/governance_surface_inventory.json",
    "registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json",
]

DEFAULT_EXECUTION_ANCHORS = {
    "scripts/global_validate.py",
    "scripts/query_governance.py",
    "scripts/db/db_health_check.py",
    "scripts/db/db_maintenance.py",
    "scripts/db/snapshot_registries.py",
    "scripts/governance/enforce_governance_integrity.py",
    "tools/inference_governance/deterministic_router.py",
}

DEFAULT_VALIDATION_ANCHORS = {
    "AGENTS.md",
    "GEMINI.md",
    "MATH_PROGRAM_NARRATIVE.md",
    "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
    "governance/live/program_task_registry.json",
    "registry/governance_change_ledger.json",
    "registry/governance_hash_registry.json",
    "registry/db/README.md",
    "scripts/global_validate.py",
    "scripts/query_governance.py",
    "tests/",
}

DEFAULT_WRITE_ANCHORS = {
    "docs/governance/",
    "governance/",
    "registry/",
    "scripts/db/",
    "scripts/governance/",
    "tools/inference_governance/",
}


def load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_surface_inventory(path: str | Path | None = None) -> dict[str, Any]:
    payload = load_json(path or DEFAULT_SURFACE_INVENTORY_PATH)
    return payload if payload else {"records": []}


def load_ambiguity_register(path: str | Path | None = None) -> dict[str, Any]:
    payload = load_json(path or DEFAULT_AMBIGUITY_REGISTER_PATH)
    return payload if payload else {"ambiguities": []}


def normalize_path_like(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\\", "/").strip()


def normalized_basename(path_like: Any) -> str:
    path = normalize_path_like(path_like)
    if "::" in path:
        path = path.split("::", 1)[0]
    base = os.path.basename(path)
    base_lower = base.lower()
    for suffix in (".json", ".md", ".py", ".pyc", ".sqlite"):
        if base_lower.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return base.lower()


def _build_lookup_indexes(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_path: dict[str, dict[str, Any]] = {}
    by_id: dict[str, dict[str, Any]] = {}
    by_title: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_basename: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if not isinstance(record, Mapping):
            continue
        path = normalize_path_like(record.get("path_or_table"))
        surface_id = normalize_path_like(record.get("surface_id"))
        if path:
            by_path[path] = dict(record)
        if surface_id:
            by_id[surface_id] = dict(record)
        title = normalize_path_like(record.get("title_or_name")).lower()
        if title:
            by_title[title].append(dict(record))
        base = normalized_basename(path)
        if base:
            by_basename[base].append(dict(record))
    return {
        "by_path": by_path,
        "by_id": by_id,
        "by_title": by_title,
        "by_basename": by_basename,
    }


def build_surface_indexes(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return _build_lookup_indexes(records)


def _resolve_prefix_matches(reference: str, path_index: Mapping[str, Mapping[str, Any]]) -> list[str]:
    ref = normalize_path_like(reference)
    if not ref:
        return []
    candidates: list[str] = []
    prefixes = {ref}
    if not ref.endswith("/"):
        prefixes.add(ref + "/")
    for path, record in path_index.items():
        if path == ref:
            candidates.append(normalize_path_like(record.get("surface_id")))
            continue
        if any(path.startswith(prefix) for prefix in prefixes):
            candidates.append(normalize_path_like(record.get("surface_id")))
    return sorted({candidate for candidate in candidates if candidate})


def resolve_reference_paths(reference: Any, path_index: Mapping[str, Mapping[str, Any]]) -> list[str]:
    ref = normalize_path_like(reference)
    if not ref:
        return []
    exact = path_index.get(ref)
    if exact:
        surface_id = normalize_path_like(exact.get("surface_id"))
        return [surface_id] if surface_id else []
    return _resolve_prefix_matches(ref, path_index)


def resolve_related_surface_ids(
    record: Mapping[str, Any],
    path_index: Mapping[str, Mapping[str, Any]],
    *,
    include_dependents: bool = False,
) -> list[str]:
    candidate_paths: list[str] = []
    for key in ("dependencies", "registry_references", "supersedes", "superseded_by"):
        value = record.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            candidate_paths.extend(normalize_path_like(item) for item in value if normalize_path_like(item))
    if include_dependents:
        value = record.get("dependents")
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            candidate_paths.extend(normalize_path_like(item) for item in value if normalize_path_like(item))
    related: set[str] = set()
    for candidate in candidate_paths:
        related.update(resolve_reference_paths(candidate, path_index))
    surface_id = normalize_path_like(record.get("surface_id"))
    if surface_id:
        related.add(surface_id)
    return sorted(related)


def _path_matches_anchor(path: str, anchors: Sequence[str]) -> bool:
    normalized = normalize_path_like(path)
    for anchor in anchors:
        normalized_anchor = normalize_path_like(anchor)
        if not normalized_anchor:
            continue
        if normalized == normalized_anchor:
            return True
        if normalized_anchor.endswith("/") and normalized.startswith(normalized_anchor):
            return True
        if not normalized_anchor.endswith("/") and normalized.startswith(normalized_anchor + "/"):
            return True
    return False


def classify_reachability(
    record: Mapping[str, Any],
    indexes: Mapping[str, Any],
    *,
    execution_anchors: Sequence[str] = tuple(DEFAULT_EXECUTION_ANCHORS),
    validation_anchors: Sequence[str] = tuple(DEFAULT_VALIDATION_ANCHORS),
    write_anchors: Sequence[str] = tuple(DEFAULT_WRITE_ANCHORS),
) -> dict[str, Any]:
    path = normalize_path_like(record.get("path_or_table"))
    surface_type = normalize_path_like(record.get("surface_type")).upper()
    authority_state = normalize_path_like(record.get("authority_state")).upper()
    direct_paths: list[str] = []
    for key in ("dependencies", "registry_references", "supersedes", "superseded_by"):
        values = record.get(key)
        if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
            direct_paths.extend(normalize_path_like(item) for item in values if normalize_path_like(item))
    execution_matches = sorted({
        candidate for candidate in [path, *direct_paths] if _path_matches_anchor(candidate, execution_anchors)
    })
    validation_matches = sorted({
        candidate for candidate in [path, *direct_paths] if _path_matches_anchor(candidate, validation_anchors)
    })
    write_matches = sorted({
        candidate for candidate in [path, *direct_paths] if _path_matches_anchor(candidate, write_anchors)
    })

    execution_reachable = bool(execution_matches)
    derived_authority_state = authority_state in {"GENERATED_VIEW", "PROPOSAL", "HISTORICAL"}
    validation_reachable = bool(validation_matches) and not derived_authority_state
    write_reachable = bool(write_matches) and not derived_authority_state

    return {
        "execution_reachable": execution_reachable,
        "execution_reachability_status": "PROVEN" if execution_reachable else "UNPROVEN",
        "execution_evidence_paths": execution_matches,
        "write_reachable": write_reachable,
        "write_reachability_status": "PROVEN" if write_reachable else "UNPROVEN",
        "write_evidence_paths": write_matches if write_reachable else [],
        "validation_reachable": validation_reachable,
        "validation_reachability_status": "PROVEN" if validation_reachable else "UNPROVEN",
        "validation_evidence_paths": validation_matches,
    }


def build_source_snapshot(
    source_files: Sequence[str],
    *,
    workspace_root_identity: str,
    repository_commit: str,
    included_roots: Sequence[str],
    excluded_roots: Sequence[str],
    file_count_scanned: int,
    surface_count_detected: int,
    working_tree_dirty: bool,
    unrelated_changes_preserved: bool,
) -> dict[str, Any]:
    artifact_hashes: dict[str, str] = {}
    for relative_path in sorted({normalize_path_like(path) for path in source_files if normalize_path_like(path)}):
        artifact_hashes[relative_path] = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
    basis = {
        "workspace_root_identity": workspace_root_identity,
        "repository_commit": repository_commit,
        "included_roots": sorted({normalize_path_like(path) for path in included_roots if normalize_path_like(path)}),
        "excluded_roots": sorted({normalize_path_like(path) for path in excluded_roots if normalize_path_like(path)}),
        "source_artifact_hashes": artifact_hashes,
        "file_count_scanned": int(file_count_scanned),
        "surface_count_detected": int(surface_count_detected),
        "working_tree_dirty": bool(working_tree_dirty),
        "unrelated_changes_preserved": bool(unrelated_changes_preserved),
    }
    logical = json.dumps(basis, sort_keys=True, separators=(",", ":")).encode("utf-8")
    basis["logical_snapshot_sha256"] = hashlib.sha256(logical).hexdigest()
    return basis
