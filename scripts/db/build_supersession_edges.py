import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path, PureWindowsPath

try:
    from scripts.orientation_status_check import classify_path
except ImportError:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from orientation_status_check import classify_path


ID_TOKEN_RE = re.compile(r"\b([LPT]\d{3})(?:\s*\((draft)\))?\b", re.IGNORECASE)
CERT_TOKEN_RE = re.compile(r"\b(ACC-CERT-\d{4}-P\d+-R\d+)\b", re.IGNORECASE)
UPPER_VERSION_RE = re.compile(r"\b(V\d+(?:[._]\d+)+)\b")
LOWER_VERSION_RE = re.compile(r"\b(v\d{2,})\b")
FAMILY_VERSION_RE = re.compile(r"\b([A-Za-z0-9_]+_v\d{2,})\b")


def repo_root():
    return Path(__file__).resolve().parents[2]


def normalize_relpath(path):
    return str(path).replace("/", "\\")


def db_connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def file_checksum(path):
    sha256_hash = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4096), b""):
            sha256_hash.update(block)
    return sha256_hash.hexdigest()


def load_artifact_indexes(conn):
    rows = conn.execute("SELECT id, path FROM artifacts").fetchall()
    path_to_id = {}
    basename_to_paths = {}
    stem_to_paths = {}
    id_to_paths = {}

    for row in rows:
        artifact_id = row["id"]
        artifact_path = row["path"]
        path_to_id[artifact_path] = artifact_id
        win_name = PureWindowsPath(artifact_path).name
        win_stem = PureWindowsPath(artifact_path).stem
        basename_to_paths.setdefault(win_name, []).append(artifact_path)
        stem_to_paths.setdefault(win_stem, []).append(artifact_path)

        match = re.match(r"^([LPT]\d{3})(?:_|\.|\b)", win_name, re.IGNORECASE)
        if match:
            token = match.group(1).upper()
            id_to_paths.setdefault(token, []).append(artifact_path)

    return {
        "path_to_id": path_to_id,
        "basename_to_paths": basename_to_paths,
        "stem_to_paths": stem_to_paths,
        "id_to_paths": id_to_paths,
    }


def candidate_files(root):
    patterns = [
        "docs/**/*.md",
        "registry/**/*.md",
    ]
    seen = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            rel = normalize_relpath(path.relative_to(root))
            if rel in seen:
                continue
            seen.add(rel)
            yield path


def ensure_artifact_rows(conn, root, paths):
    missing = []
    for path in paths:
        rel = normalize_relpath(path.relative_to(root))
        row = conn.execute("SELECT id FROM artifacts WHERE path=?", (rel,)).fetchone()
        if row is None:
            missing.append((path, rel))

    for path, rel in missing:
        status, scope, confidence = classify_path(rel)
        ext = path.suffix.lower().lstrip(".") or "file"
        conn.execute(
            """
            INSERT OR REPLACE INTO artifacts (
                path,
                artifact_type,
                orientation_status,
                authority_scope,
                evidence_confidence,
                checksum
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (rel, ext, status, scope, confidence, file_checksum(path)),
        )

    if missing:
        conn.commit()

    return len(missing)


def extract_target_tokens(text):
    tokens = []
    lines = text.splitlines()
    for line in lines:
        if "Supersedes" not in line:
            continue
        suffix_match = re.search(r"Supersedes\s*:?\s*(.+)", line, re.IGNORECASE)
        if not suffix_match:
            continue
        suffix = suffix_match.group(1).strip()
        if not suffix or "Superseded-by" in suffix:
            continue
        if suffix.lower().startswith("none"):
            continue

        for match in ID_TOKEN_RE.finditer(suffix):
            token = match.group(1).upper()
            if match.group(2):
                token = f"{token} (draft)"
            tokens.append(token)

        for match in CERT_TOKEN_RE.finditer(suffix):
            tokens.append(match.group(1).upper())

        for match in FAMILY_VERSION_RE.finditer(suffix):
            tokens.append(match.group(1))

        for match in UPPER_VERSION_RE.finditer(suffix):
            tokens.append(match.group(1))

        for match in LOWER_VERSION_RE.finditer(suffix):
            tokens.append(match.group(1))

    deduped = []
    seen = set()
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        deduped.append(token)
    return deduped


def score_path(path, source_path, token):
    score = 0
    name = PureWindowsPath(path).name
    source_parts = PureWindowsPath(source_path).parts
    target_parts = PureWindowsPath(path).parts

    shared = 0
    for left, right in zip(source_parts, target_parts):
        if left != right:
            break
        shared += 1
    score += shared * 10

    if token.upper().startswith(("L", "P", "T")) and name.upper().startswith(token.split()[0]):
        score += 20

    if "_v" not in name.lower():
        score += 5

    if name.endswith(".md"):
        score += 2

    return score


def resolve_id_token(token, source_path, indexes):
    base_token = token.split()[0].upper()
    candidates = [path for path in indexes["id_to_paths"].get(base_token, []) if path != source_path]
    if not candidates:
        return None, f"no indexed artifact for {base_token}"

    ranked = sorted(candidates, key=lambda p: (-score_path(p, source_path, base_token), p))
    if "(draft)" in token.lower():
        for candidate in ranked:
            if "_v" not in PureWindowsPath(candidate).name.lower():
                return candidate, None
    return ranked[0], None


def resolve_version_token(token, source_path, indexes):
    source_name = PureWindowsPath(source_path).name
    basename_candidates = []

    if token.startswith("V"):
        target_fragment = token.replace(".", "_")
        source_match = re.search(r"V\d+(?:_\d+)+", source_name)
        if source_match:
            basename_candidates.append(source_name.replace(source_match.group(0), target_fragment))

    family_match = FAMILY_VERSION_RE.fullmatch(token)
    if family_match:
        basename_candidates.append(f"{family_match.group(1)}.md")
        basename_candidates.append(f"{family_match.group(1)}.docx")

    lower_match = LOWER_VERSION_RE.fullmatch(token)
    if lower_match:
        source_match = re.search(r"v\d{2,}", source_name)
        if source_match:
            basename_candidates.append(source_name.replace(source_match.group(0), lower_match.group(1)))

    for basename in basename_candidates:
        paths = indexes["basename_to_paths"].get(basename, [])
        if paths:
            ranked = sorted(paths, key=lambda p: (-score_path(p, source_path, token), p))
            return ranked[0], None

    stem_paths = indexes["stem_to_paths"].get(token, [])
    if stem_paths:
        ranked = sorted(stem_paths, key=lambda p: (-score_path(p, source_path, token), p))
        return ranked[0], None

    return None, f"no indexed artifact matched version token {token}"


def resolve_target(token, source_path, indexes):
    if re.fullmatch(r"[LPT]\d{3}(?: \(draft\))?", token, re.IGNORECASE):
        return resolve_id_token(token, source_path, indexes)
    if CERT_TOKEN_RE.fullmatch(token):
        paths = indexes["stem_to_paths"].get(token, [])
        if paths:
            return paths[0], None
        return None, f"no indexed artifact for certificate token {token}"
    return resolve_version_token(token, source_path, indexes)


def collect_explicit_edges(root, indexes):
    edges = []
    unresolved = []
    for path in candidate_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        tokens = extract_target_tokens(text)
        if not tokens:
            continue

        source_rel = normalize_relpath(path.relative_to(root))
        source_id = indexes["path_to_id"].get(source_rel)
        if source_id is None:
            unresolved.append(
                {
                    "source_path": source_rel,
                    "target_token": None,
                    "reason": "source artifact missing from artifacts table",
                }
            )
            continue

        for token in tokens:
            target_path, reason = resolve_target(token, source_rel, indexes)
            if target_path is None:
                unresolved.append(
                    {
                        "source_path": source_rel,
                        "target_token": token,
                        "reason": reason,
                    }
                )
                continue

            target_id = indexes["path_to_id"].get(target_path)
            if target_id is None:
                unresolved.append(
                    {
                        "source_path": source_rel,
                        "target_token": token,
                        "reason": f"resolved path missing from artifacts table: {target_path}",
                    }
                )
                continue

            if source_id == target_id:
                unresolved.append(
                    {
                        "source_path": source_rel,
                        "target_token": token,
                        "reason": f"resolved self-edge for token {token}",
                    }
                )
                continue

            edges.append(
                {
                    "from_artifact_id": source_id,
                    "to_artifact_id": target_id,
                    "relation": "supersedes",
                    "evidence_path": source_rel,
                    "confidence": "verified",
                    "reason": "Explicit Supersedes metadata in source artifact.",
                    "from_path": source_rel,
                    "to_path": target_path,
                    "target_token": token,
                }
            )

    deduped = {}
    for edge in edges:
        key = (edge["from_artifact_id"], edge["to_artifact_id"], edge["relation"])
        deduped[key] = edge

    return list(deduped.values()), unresolved


def apply_edges(conn, edges):
    conn.execute("DELETE FROM supersession_edges")
    conn.executemany(
        """
        INSERT INTO supersession_edges (
            from_artifact_id,
            to_artifact_id,
            relation,
            evidence_path,
            confidence,
            reason
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                edge["from_artifact_id"],
                edge["to_artifact_id"],
                edge["relation"],
                edge["evidence_path"],
                edge["confidence"],
                edge["reason"],
            )
            for edge in edges
        ],
    )
    conn.commit()


def build_report(edges, unresolved, apply_mode):
    by_relation = {}
    by_target_token = {}
    for edge in edges:
        by_relation[edge["relation"]] = by_relation.get(edge["relation"], 0) + 1
        by_target_token[edge["target_token"]] = by_target_token.get(edge["target_token"], 0) + 1

    return {
        "mode": "apply" if apply_mode else "dry_run",
        "edge_count": len(edges),
        "by_relation": by_relation,
        "unique_target_tokens": len(by_target_token),
        "unresolved_count": len(unresolved),
        "sample_edges": edges[:20],
        "sample_unresolved": unresolved[:20],
    }


def main():
    parser = argparse.ArgumentParser(description="Rebuild supersession_edges from explicit supersession declarations only.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--apply", action="store_true", help="Replace current supersession_edges contents.")
    args = parser.parse_args()

    root = repo_root()
    conn = db_connect(str(root / args.db))
    try:
        source_files = list(candidate_files(root))
        synced = ensure_artifact_rows(conn, root, source_files)
        indexes = load_artifact_indexes(conn)
        edges, unresolved = collect_explicit_edges(root, indexes)
        if args.apply:
            apply_edges(conn, edges)
        report = build_report(edges, unresolved, args.apply)
        report["artifact_rows_synced"] = synced
        print(json.dumps(report, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
