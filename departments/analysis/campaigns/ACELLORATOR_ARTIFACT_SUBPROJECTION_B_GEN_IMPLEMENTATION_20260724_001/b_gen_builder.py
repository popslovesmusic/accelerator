import argparse
import hashlib
import json
import os
from pathlib import Path


BUILDER_ID = "B-GEN"
BUILDER_VERSION = "B-GEN-1.0.0"
CAMPAIGN_PATH = "departments/analysis/campaigns/ACELLORATOR_ARTIFACT_SUBPROJECTION_B_GEN_IMPLEMENTATION_20260724_001"
GENERATED_ROOTS = {
    "audit_outputs", "audits", "outputs", "reports", "results", "validation",
    "zenodo", "governance_backups", "patches", "proofs",
}
EXCLUDED_PARTS = {
    ".git", ".venv", ".pytest_cache", "__pycache__", "node_modules", ".tmp",
    "registry", "docs", "scratch", "state", "runtime", "experiments",
}
GENERATED_NAME_TOKENS = (
    "report", "result", "manifest", "audit", "campaign", "validation", "output",
    "summary", "freeze", "comparison", "evidence", "patch", "hash", "archive",
)
GENERATED_EXTENSIONS = {".json", ".md", ".zip", ".csv", ".log", ".html", ".xml", ".parquet", ".pdf", ".obj", ".exe", ".pyd"}
DATABASE_EXTENSIONS = {".sqlite", ".sqlite3", ".db", ".wal", ".shm", ".journal"}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def path_key(value):
    return (value.casefold(), value)


def relative(path, root):
    return path.relative_to(root).as_posix()


def generated_class(rel, is_dir=False):
    parts = rel.split("/")
    root = parts[0]
    name = Path(parts[-1]).name.casefold()
    suffix = Path(parts[-1]).suffix.casefold()
    if suffix in DATABASE_EXTENSIONS or name.endswith(("-wal", "-shm", "-journal")):
        return None
    if root in {"outputs", "results", "validation"} and not any(token in name for token in GENERATED_NAME_TOKENS) and suffix not in {".md", ".zip"}:
        return None
    if root in GENERATED_ROOTS:
        if suffix == ".zip" or suffix in {".tar", ".gz", ".7z"}:
            return "ARCHIVE"
        if "manifest" in name:
            return "GENERATED_MANIFEST"
        if "campaign" in rel.casefold() or root == "outputs":
            return "CAMPAIGN_OUTPUT"
        if "report" in name or root in {"reports", "audits"}:
            return "GENERATED_REPORT"
        return "DERIVED_DELIVERABLE"
    if root == "departments" and "analysis/campaigns/" in rel.casefold():
        return "ARCHIVE" if suffix == ".zip" else "CAMPAIGN_OUTPUT"
    if root == "" and any(token in name for token in GENERATED_NAME_TOKENS) and suffix in GENERATED_EXTENSIONS:
        return "BUILD_PRODUCT" if suffix in {".obj", ".exe", ".pyd"} else "DERIVED_DELIVERABLE"
    return None


def excluded(rel):
    if rel == CAMPAIGN_PATH or rel.startswith(CAMPAIGN_PATH + "/"):
        return True
    parts = rel.split("/")
    return any(part in EXCLUDED_PARTS for part in parts)


def build(root, checkpoint_path):
    records = []
    errors = []
    visited_roots = []
    for base, dirs, names in os.walk(root, topdown=True, followlinks=False):
        rel_base = relative(Path(base), root) if Path(base) != root else ""
        dirs[:] = sorted([name for name in dirs if not excluded((rel_base + "/" + name).strip("/"))], key=path_key)
        names = sorted(names, key=path_key)
        for name in names:
            path = Path(base) / name
            rel = relative(path, root)
            if excluded(rel) or path.is_symlink():
                continue
            try:
                kind = generated_class(rel)
                if not kind:
                    continue
                info = path.stat()
                record = {
                    "canonical_identity": f"generated_artifact:{rel}:{kind}",
                    "generator_id": rel.split("/", 1)[0] if "/" in rel else "root_generated",
                    "normalized_output_path": rel,
                    "artifact_class": kind,
                    "physical_or_logical": "PHYSICAL_FILE",
                    "size_bytes": info.st_size,
                    "sha256": digest(path),
                    "mtime_ns": info.st_mtime_ns,
                    "provenance": {
                        "builder_id": BUILDER_ID,
                        "builder_version": BUILDER_VERSION,
                        "observation": "read_only_generated_artifact_observation",
                        "source_root": rel.split("/", 1)[0] if "/" in rel else ".",
                    },
                }
                records.append(record)
            except OSError as exc:
                errors.append({"path": rel, "error": str(exc)})
        visited_roots.append(rel_base or ".")
        checkpoint_path.write_text(json.dumps({"builder_id": BUILDER_ID, "status": "CHECKPOINT", "completed_root": rel_base or ".", "records_so_far": len(records), "errors": len(errors)}, indent=2) + "\n", encoding="utf-8")
    records.sort(key=lambda item: path_key(item["normalized_output_path"]) + (item["artifact_class"],))
    ordered = "\n".join(json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for item in records).encode()
    return records, errors, digest_bytes(ordered), visited_roots


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    records, errors, ordered_hash, visited = build(root, out / "b_gen_checkpoint.json")
    catalog = {
        "schema_version": BUILDER_VERSION,
        "builder_id": BUILDER_ID,
        "subprojection_id": "generated_artifact_catalog",
        "authority": "DERIVED",
        "included_roots": sorted(GENERATED_ROOTS),
        "identity_rule": "generator identifier plus canonical output path plus artifact class",
        "ordering_rule": "case-insensitive path ascending, case-sensitive tie-break, artifact class tie-break",
        "record_count": len(records),
        "records": records,
        "ordered_rows_sha256": ordered_hash,
        "errors": errors,
        "visited_root_count": len(visited),
        "checkpoint_resume": True,
    }
    catalog_bytes = json.dumps(catalog, indent=2, ensure_ascii=False).encode()
    (out / "b_gen_generated_catalog.json").write_bytes(catalog_bytes)
    manifest = {
        "builder_id": BUILDER_ID,
        "builder_version": BUILDER_VERSION,
        "subprojection_id": "generated_artifact_catalog",
        "authority": "DERIVED_NON_PRODUCTION",
        "record_count": len(records),
        "ordered_rows_sha256": ordered_hash,
        "catalog_sha256": digest_bytes(catalog_bytes),
        "errors": len(errors),
        "status": "IMPLEMENTED_NON_PRODUCTION",
        "checkpoint_resume": True,
    }
    (out / "b_gen_builder_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
