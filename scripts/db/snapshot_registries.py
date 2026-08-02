import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone

try:
    from scripts.orientation_status_check import classify_path
except ImportError:
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from orientation_status_check import classify_path


def get_hash(path):
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def _utc_iso(dt=None):
    dt = dt or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_refresh_metadata_surface(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS db_snapshot_refresh_metadata (
            scope TEXT PRIMARY KEY,
            refresh_id TEXT NOT NULL,
            last_refresh_attempt TIMESTAMP NOT NULL,
            last_refresh_result TEXT NOT NULL,
            indexed_at TIMESTAMP,
            source_worktree_marker TIMESTAMP,
            runtime_worktree_marker TIMESTAMP,
            error_reason TEXT,
            registry_count INTEGER DEFAULT 0,
            indexed_registry_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute("PRAGMA table_info(db_snapshot_refresh_metadata)")
    columns = {row[1] for row in cursor.fetchall()}
    if "runtime_worktree_marker" not in columns:
        cursor.execute("ALTER TABLE db_snapshot_refresh_metadata ADD COLUMN runtime_worktree_marker TIMESTAMP")
    cursor.execute("DROP VIEW IF EXISTS db_snapshot_refresh_view")
    cursor.execute(
        """
        CREATE VIEW db_snapshot_refresh_view AS
        SELECT
            scope,
            refresh_id,
            last_refresh_attempt,
            last_refresh_result,
            indexed_at,
            source_worktree_marker,
            runtime_worktree_marker,
            error_reason,
            registry_count,
            indexed_registry_count,
            updated_at
        FROM db_snapshot_refresh_metadata
        WHERE scope = 'global'
        """
    )


def upsert_refresh_metadata(cursor, record):
    cursor.execute(
        """
        INSERT INTO db_snapshot_refresh_metadata (
            scope,
            refresh_id,
            last_refresh_attempt,
            last_refresh_result,
            indexed_at,
            source_worktree_marker,
            runtime_worktree_marker,
            error_reason,
            registry_count,
            indexed_registry_count,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(scope) DO UPDATE SET
            refresh_id = excluded.refresh_id,
            last_refresh_attempt = excluded.last_refresh_attempt,
            last_refresh_result = excluded.last_refresh_result,
            indexed_at = excluded.indexed_at,
            source_worktree_marker = excluded.source_worktree_marker,
            runtime_worktree_marker = excluded.runtime_worktree_marker,
            error_reason = excluded.error_reason,
            registry_count = excluded.registry_count,
            indexed_registry_count = excluded.indexed_registry_count,
            updated_at = excluded.updated_at
        """,
        (
            record["scope"],
            record["refresh_id"],
            record["last_refresh_attempt"],
            record["last_refresh_result"],
            record.get("indexed_at"),
            record.get("source_worktree_marker"),
            record.get("runtime_worktree_marker"),
            record.get("error_reason"),
            record.get("registry_count", 0),
            record.get("indexed_registry_count", 0),
            record.get("updated_at"),
        ),
    )


def snapshot_registries(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ensure_refresh_metadata_surface(cursor)

    registries = [
        "registry/tool_manifest.json",
        "registry/lexicon_canonical.json",
        "registry/lexicon_alias_map.json",
        "registry/lexicon_gap_queue.json",
        "registry/lexicon_validation_registry.json",
        "registry/math_source_registry.json",
        "registry/math_hashes.json",
        "registry/math_core_hashes.json",
        "registry/compliance_charter_v2_3.json",
    ]

    refresh_id = f"REFRESH-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    attempt_started = _utc_iso()
    indexed_count = 0
    missing_registries = []
    source_worktree_marker = None
    runtime_worktree_marker = None
    source_worktree_paths = []
    errors = []

    result = {
        "status": "fail",
        "reason": "Snapshot refresh did not run.",
        "refresh_id": refresh_id,
        "last_refresh_attempt": attempt_started,
        "last_refresh_result": "fail",
        "indexed_at": None,
        "source_worktree_marker": None,
        "runtime_worktree_marker": None,
        "registry_count": len(registries),
        "indexed_registry_count": 0,
        "missing_registries": [],
        "error_reason": None,
        "source_worktree_paths": [],
        "evidence_paths": [
            "scripts/db/snapshot_registries.py",
            "registry/db/migrations/20260703_governance_runtime_snapshot_refresh_011.sql",
            "registry/db/migrations/20260703_governance_runtime_refresh_stability_012.sql",
        ],
    }

    try:
        for path in registries:
            if not os.path.exists(path):
                missing_registries.append(path)
                continue

            status, scope, _ = classify_path(path)
            source_hash = get_hash(path)
            modified_dt = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
            modified_at = _utc_iso(modified_dt)
            source_worktree_paths.append(path)
            if source_worktree_marker is None or modified_dt > source_worktree_marker:
                source_worktree_marker = modified_dt

            r_type = "unknown"
            key_count = 0
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "lexicon" in path:
                        r_type = "lexicon"
                    elif "claim" in path:
                        r_type = "claim"
                    elif "manifest" in path:
                        r_type = "tool_manifest"

                    if isinstance(data, dict):
                        for key in ["terms", "tools", "claims", "lemmas", "proofs"]:
                            if key in data and isinstance(data[key], (list, dict)):
                                key_count = len(data[key])
                                break
                        if key_count == 0:
                            key_count = len(data)
                    elif isinstance(data, list):
                        key_count = len(data)
            except Exception as exc:
                errors.append(f"{path}: {exc}")

            cursor.execute(
                """
                INSERT INTO registry_snapshots (
                    registry_path, registry_type, source_hash, key_count,
                    modified_at, orientation_status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (path, r_type, source_hash, key_count, modified_at, status),
            )
            indexed_count += 1

        indexed_at = _utc_iso()
        runtime_worktree_marker = indexed_at
        upsert_refresh_metadata(
            cursor,
            {
                "scope": "global",
                "refresh_id": refresh_id,
                "last_refresh_attempt": attempt_started,
                "last_refresh_result": "success",
                "indexed_at": indexed_at,
                "source_worktree_marker": _utc_iso(source_worktree_marker) if source_worktree_marker else None,
                "runtime_worktree_marker": runtime_worktree_marker,
                "error_reason": None,
                "registry_count": len(registries),
                "indexed_registry_count": indexed_count,
                "updated_at": indexed_at,
            },
        )
        conn.commit()
        try:
            runtime_dt = datetime.fromisoformat(runtime_worktree_marker.replace("Z", "+00:00"))
            os.utime(db_path, (runtime_dt.timestamp(), runtime_dt.timestamp()))
        except Exception as exc:
            errors.append(f"runtime marker normalization failed: {exc}")

        result.update(
            {
                "status": "success",
                "reason": "Registry snapshots indexed and refresh metadata written.",
                "last_refresh_result": "success",
                "indexed_at": indexed_at,
                "source_worktree_marker": _utc_iso(source_worktree_marker) if source_worktree_marker else None,
                "runtime_worktree_marker": runtime_worktree_marker,
                "indexed_registry_count": indexed_count,
                "missing_registries": missing_registries,
                "source_worktree_paths": source_worktree_paths,
                "error_reason": None,
            }
        )
        if errors:
            result["warnings"] = errors
        else:
            result["warnings"] = []
    except Exception as exc:
        conn.rollback()
        error_reason = str(exc)
        failed_at = _utc_iso()
        try:
            upsert_refresh_metadata(
                cursor,
                {
                    "scope": "global",
                    "refresh_id": refresh_id,
                    "last_refresh_attempt": attempt_started,
                    "last_refresh_result": "fail",
                    "indexed_at": None,
                    "source_worktree_marker": _utc_iso(source_worktree_marker) if source_worktree_marker else None,
                    "runtime_worktree_marker": runtime_worktree_marker,
                    "error_reason": error_reason,
                    "registry_count": len(registries),
                    "indexed_registry_count": indexed_count,
                    "updated_at": failed_at,
                },
            )
            conn.commit()
        except sqlite3.Error:
            pass
        result.update(
            {
                "status": "fail",
                "reason": "Registry snapshot refresh failed.",
                "last_refresh_result": "fail",
                "indexed_at": None,
                "source_worktree_marker": _utc_iso(source_worktree_marker) if source_worktree_marker else None,
                "runtime_worktree_marker": runtime_worktree_marker,
                "indexed_registry_count": indexed_count,
                "missing_registries": missing_registries,
                "source_worktree_paths": source_worktree_paths,
                "error_reason": error_reason,
                "warnings": errors + [error_reason],
            }
        )
    finally:
        conn.close()

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snapshot SSOT registry metadata into DB.")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    args = parser.parse_args()
    snapshot_registries(args.db)
