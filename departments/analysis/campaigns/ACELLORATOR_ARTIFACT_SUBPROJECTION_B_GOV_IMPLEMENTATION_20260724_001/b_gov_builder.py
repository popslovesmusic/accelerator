import hashlib
import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
DB = ROOT / "registry" / "db" / "acellorator_index.sqlite"
BUILDER_ID = "B-GOV"
VERSION = "B-GOV-1.0.0"


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(path):
    value = str(path).replace("\\", "/").strip()
    while value.startswith("./"):
        value = value[2:]
    return value


def metadata(path, data, source_type):
    if source_type == "json":
        try:
            value = json.loads(data.decode("utf-8-sig"))
            return {
                "json_valid": True,
                "top_level_type": type(value).__name__,
                "top_level_keys": sorted(value)[:100] if isinstance(value, dict) else [],
            }
        except Exception:
            return {"json_valid": False, "top_level_type": "invalid", "top_level_keys": []}
    text = data.decode("utf-8", errors="replace")
    return {
        "json_valid": None,
        "top_level_type": "markdown",
        "top_level_keys": [],
        "line_count": text.count("\n") + 1,
        "heading_count": sum(line.lstrip().startswith("#") for line in text.splitlines()),
    }


def discover_paths():
    paths = []
    for root_name in ("docs", "registry"):
        root = ROOT / root_name
        for base, dirs, names in os.walk(root, topdown=True, followlinks=False):
            dirs.sort()
            names.sort()
            for name in names:
                path = Path(base) / name
                if path.is_symlink() or path.suffix.lower() not in {".md", ".json"}:
                    continue
                paths.append(normalize(path.relative_to(ROOT)))
    return sorted(set(paths), key=lambda item: (item.lower(), item))


def build():
    paths = discover_paths()
    records = []
    rows_hash = hashlib.sha256()
    for relative in paths:
        path = ROOT / relative
        data = path.read_bytes()
        source_type = "markdown" if path.suffix.lower() == ".md" else "json"
        content_hash = digest_bytes(data)
        record = {
            "canonical_identity": f"governed_source:{relative}",
            "normalized_path": relative,
            "source_path": relative,
            "source_type": source_type,
            "bytes": len(data),
            "sha256": content_hash,
            "authority_class": "AUTHORITATIVE",
            "authority_scope": "governed_source_corpus",
            "source_status": "AUTHORITATIVE_SOURCE_CORPUS",
            "provenance": {
                "source_root": relative.split("/", 1)[0],
                "builder_id": BUILDER_ID,
                "builder_version": VERSION,
                "content_hash": content_hash,
            },
            "metadata": metadata(path, data, source_type),
        }
        records.append(record)
        rows_hash.update((json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode())
    output = {
        "schema_version": VERSION,
        "builder_id": BUILDER_ID,
        "subprojection_id": "governed_source_inventory",
        "authority": "AUTHORITATIVE",
        "input_roots": ["docs", "registry"],
        "input_extensions": [".md", ".json"],
        "ordering_rule": "case-insensitive normalized path ascending, case-sensitive tie-break",
        "record_count": len(records),
        "records": records,
        "ordered_rows_sha256": rows_hash.hexdigest(),
    }
    encoded = json.dumps(output, indent=2, ensure_ascii=False).encode()
    return output, encoded, paths, rows_hash.hexdigest()


if __name__ == "__main__":
    result, encoded, paths, rows_hash = build()
    (OUT / "b_gov_candidate_output.json").write_bytes(encoded)
    print(json.dumps({"record_count": len(paths), "ordered_rows_sha256": rows_hash, "output_sha256": digest_bytes(encoded)}))
