import os
import sqlite3
from pathlib import Path
from unittest import mock

import pytest

from scripts.db import index_artifacts


class _FakeCursor:
    def execute(self, *args, **kwargs):
        return None


class _FakeConnection:
    def cursor(self):
        return _FakeCursor()

    def commit(self):
        return None

    def close(self):
        return None


def _run_indexer_with_fake_database(monkeypatch, root, db_path, checksum):
    monkeypatch.setattr(index_artifacts.sqlite3, "connect", lambda _: _FakeConnection())
    monkeypatch.setattr(index_artifacts, "classify_path", lambda _: ("", "", ""))
    monkeypatch.setattr(index_artifacts, "get_checksum", checksum)
    index_artifacts.index_artifacts(str(db_path), str(root))


def test_active_database_and_direct_sidecars_are_excluded(tmp_path, monkeypatch):
    db_path = tmp_path / "acellorator_index.sqlite"
    db_path.write_bytes(b"database")
    for suffix in ("-wal", "-shm", "-journal"):
        Path(str(db_path) + suffix).write_bytes(b"sidecar")
    ordinary = tmp_path / "ordinary.json"
    ordinary.write_text("{}", encoding="utf-8")
    seen = []

    def checksum(path):
        seen.append(Path(path).resolve())
        return "checksum"

    _run_indexer_with_fake_database(monkeypatch, tmp_path, db_path, checksum)

    assert db_path.resolve() not in seen
    assert all(Path(str(db_path) + suffix).resolve() not in seen for suffix in ("-wal", "-shm", "-journal"))
    assert ordinary.resolve() in seen


def test_hardlink_alias_is_excluded_when_supported(tmp_path):
    db_path = tmp_path / "acellorator_index.sqlite"
    alias = tmp_path / "alias.sqlite"
    db_path.write_bytes(b"database")
    try:
        os.link(db_path, alias)
    except (OSError, NotImplementedError):
        pytest.skip("hardlinks are unavailable on this filesystem")

    db_abs, sidecars = index_artifacts._self_managed_database_paths(db_path)
    assert index_artifacts._is_self_managed_database_candidate(alias, db_abs, sidecars)


def test_unrelated_sqlite_remains_eligible(tmp_path):
    db_path = tmp_path / "acellorator_index.sqlite"
    unrelated = tmp_path / "unrelated.sqlite"
    db_path.write_bytes(b"database")
    unrelated.write_bytes(b"other")
    db_abs, sidecars = index_artifacts._self_managed_database_paths(db_path)

    assert not index_artifacts._is_self_managed_database_candidate(unrelated, db_abs, sidecars)


def test_permission_error_on_unrelated_candidate_is_not_suppressed(tmp_path, monkeypatch):
    db_path = tmp_path / "acellorator_index.sqlite"
    db_path.write_bytes(b"database")
    ordinary = tmp_path / "ordinary.bin"
    ordinary.write_bytes(b"ordinary")

    def checksum(path):
        if Path(path).resolve() == ordinary.resolve():
            raise PermissionError(13, "Permission denied")
        return "checksum"

    with pytest.raises(PermissionError):
        _run_indexer_with_fake_database(monkeypatch, tmp_path, db_path, checksum)
