import argparse
import hashlib
import json
import os
import stat
from pathlib import Path


BUILDER_ID = "B-WS"
BUILDER_VERSION = "B-WS-1.0.0"
EXCLUDED_ROOT_NAMES = {
    ".git", ".hg", ".svn", ".venv", "__pycache__", "node_modules",
    "audit_outputs", "outputs", "validation", "audits", "governance_backups",
    "scratch", "state", "runtime", "results", "experiments", "registry", "docs",
    "tmp", ".tmp", "temp", "cache", "caches", ".pytest_cache",
}
EXCLUDED_SUFFIXES = {".obj", ".exe", ".pyd", ".dll", ".so", ".o", ".a"}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical_rel(path, root):
    return path.relative_to(root).as_posix()


def sort_key(value):
    return (value.casefold(), value)


def excluded(rel, is_dir=False):
    parts = rel.split("/")
    if any(part in {".git", ".hg", ".svn", ".venv", "__pycache__", "node_modules", "audit_outputs", "outputs", "validation", "audits", "governance_backups", "scratch", "state", "runtime", "results", "experiments", "registry", "docs", "tmp", ".tmp", "temp", "cache", "caches", ".pytest_cache"} for part in parts):
        return True
    if rel == "registry/db" or rel.startswith("registry/db/") or rel == "registry/registry" or rel.startswith("registry/registry/"):
        return True
    if not is_dir and Path(rel).suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    if rel.startswith("departments/analysis/campaigns/"):
        return True
    return False


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(root):
    records = []
    relationships = []
    hardlinks = {}
    stack = [root]
    errors = []
    while stack:
        current = stack.pop()
        try:
            children = sorted(os.scandir(current), key=lambda entry: sort_key(entry.name))
        except OSError as exc:
            errors.append({"path": canonical_rel(current, root), "error": str(exc)})
            continue
        for entry in children:
            path = Path(entry.path)
            rel = canonical_rel(path, root)
            try:
                is_link = entry.is_symlink()
                is_dir = entry.is_dir(follow_symlinks=False)
            except OSError as exc:
                errors.append({"path": rel, "error": str(exc)})
                continue
            if excluded(rel, is_dir):
                continue
            if is_dir and not is_link:
                stack.append(path)
                kind = "PHYSICAL_DIRECTORY"
            elif is_link:
                kind = "SYMLINK"
            else:
                kind = "PHYSICAL_FILE"
            try:
                info = entry.stat(follow_symlinks=False)
                target = os.readlink(path) if is_link else None
                digest = None if is_dir or is_link else file_hash(path)
                identity = f"workspace_artifact:{rel}:{kind}"
                record = {
                    "canonical_identity": identity,
                    "normalized_workspace_relative_path": rel,
                    "artifact_class": kind,
                    "physical_or_logical": "ALIAS_OR_REFERENCE" if is_link else "PHYSICAL_FILE" if not is_dir else "PHYSICAL_DIRECTORY",
                    "size_bytes": None if is_dir or is_link else info.st_size,
                    "sha256": digest,
                    "mode": stat.S_IMODE(info.st_mode),
                    "mtime_ns": info.st_mtime_ns,
                    "is_symlink": is_link,
                    "symlink_target": target,
                    "provenance": {
                        "builder_id": BUILDER_ID,
                        "builder_version": BUILDER_VERSION,
                        "workspace_root": ".",
                        "observation": "read_only_filesystem_observation",
                    },
                }
                records.append(record)
                if is_link:
                    relationships.append({"type": "symlink", "source": identity, "target": target})
                if not is_dir and not is_link:
                    file_key = (info.st_dev, info.st_ino)
                    hardlinks.setdefault(file_key, []).append(identity)
                parent = path.parent
                if parent != root:
                    parent_rel = canonical_rel(parent, root)
                    relationships.append({"type": "parent_directory", "source": identity, "target": f"workspace_artifact:{parent_rel}:PHYSICAL_DIRECTORY"})
            except OSError as exc:
                errors.append({"path": rel, "error": str(exc)})
    records.sort(key=lambda item: sort_key(item["normalized_workspace_relative_path"]) + (item["artifact_class"],))
    for record in records:
        rel = record["normalized_workspace_relative_path"]
        parent = rel.rsplit("/", 1)[0] if "/" in rel else "."
        relationships.append({"type": "contains", "source": f"workspace_artifact:{parent}:PHYSICAL_DIRECTORY", "target": record["canonical_identity"]})
    for identities in hardlinks.values():
        if len(identities) > 1:
            members = sorted(identities)
            relationships.append({"type": "hardlink_group", "members": members})
    relationships.sort(key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    ordered = "\n".join(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for item in records).encode()
    rel_encoded = "\n".join(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for item in relationships).encode()
    catalog = {
        "schema_version": BUILDER_VERSION,
        "builder_id": BUILDER_ID,
        "subprojection_id": "workspace_artifact_catalog",
        "authority": "DERIVED",
        "workspace_root": ".",
        "exclusion_policy": {
            "generated_and_runtime_roots": sorted(EXCLUDED_ROOT_NAMES),
            "generated_binary_suffixes": sorted(EXCLUDED_SUFFIXES),
            "campaign_output_roots": ["departments/analysis/campaigns"],
            "governed_source_root": "registry and docs are excluded from B-WS; governed-source semantics belong to B-GOV",
            "symlink_policy": "record_without_traversal",
        },
        "identity_rule": "canonical workspace-relative path plus artifact class",
        "ordering_rule": "case-insensitive path ascending, case-sensitive tie-break, artifact class tie-break",
        "record_count": len(records),
        "records": records,
        "ordered_rows_sha256": sha256_bytes(ordered),
        "relationship_count": len(relationships),
        "errors": errors,
    }
    return catalog, relationships


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    catalog, relationships = build(root)
    catalog_bytes = json.dumps(catalog, indent=2, ensure_ascii=False).encode()
    relationship_bytes = json.dumps({"schema_version": BUILDER_VERSION, "relationships": relationships}, indent=2, ensure_ascii=False).encode()
    (out / "b_ws_workspace_catalog.json").write_bytes(catalog_bytes)
    (out / "b_ws_relationship_graph.json").write_bytes(relationship_bytes)
    manifest = {
        "builder_id": BUILDER_ID,
        "builder_version": BUILDER_VERSION,
        "subprojection_id": "workspace_artifact_catalog",
        "authority": "DERIVED_NON_PRODUCTION",
        "root": ".",
        "record_count": catalog["record_count"],
        "relationship_count": len(relationships),
        "ordered_rows_sha256": catalog["ordered_rows_sha256"],
        "catalog_sha256": sha256_bytes(catalog_bytes),
        "relationship_graph_sha256": sha256_bytes(relationship_bytes),
        "errors": len(catalog["errors"]),
        "status": "IMPLEMENTED_NON_PRODUCTION",
    }
    (out / "b_ws_builder_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
