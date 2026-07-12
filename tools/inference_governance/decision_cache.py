from __future__ import annotations

import json
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional

from .cache_policy import (
    CACHE_EVENT_TYPES,
    CACHE_NAMESPACE_DEFAULT,
    CACHE_POLICY_VERSION,
    CLASS_A_DETERMINISTIC_RESULT,
    CLASS_B_ACCEPTED_CONSTRAINED_OUTPUT,
    CLASS_C_REJECTED_OR_FAILED_OUTPUT,
    CLASS_D_FORBIDDEN,
    DECISION_CACHE_ENTRY_SCHEMA_ID,
    DECISION_CACHE_EVENT_SCHEMA_ID,
    DECISION_CACHE_KEY_SCHEMA_ID,
    DECISION_CACHE_SCHEMA_VERSION,
    DEFAULT_BOUNDARY_POLICY_VERSION,
    DEFAULT_DETERMINISTIC_METHOD_VERSION,
    DEFAULT_OUTPUT_SCHEMA_VERSION,
    DEFAULT_VALIDATOR_ID,
    DEFAULT_VALIDATOR_VERSION,
    REPLY_SOURCE_CACHED_ACCEPTED_OUTPUT,
    REPLY_SOURCE_CACHED_DETERMINISTIC,
    SOURCE_ACCEPTED_CONSTRAINED_INFERENCE,
    SOURCE_DETERMINISTIC,
    SOURCE_NEGATIVE_RESULT,
    build_cached_result_payload,
    build_invalidation_dependency_record,
    build_provenance_record,
    build_validation_record,
    classify_semantic_readout_result,
    hash_json_value,
    normalize_string,
    validate_semantic_readout_reply_payload,
)


LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DECISION_CACHE_DB_PATH = ROOT / "state" / "inference_governance" / "decision_cache.sqlite3"
DEFAULT_CACHE_TIMEOUT_S = 5.0


CACHE_SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS decision_cache_entries (
    cache_key TEXT PRIMARY KEY NOT NULL,
    cache_namespace TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    cache_class TEXT NOT NULL,
    source TEXT NOT NULL,
    boundary_id TEXT NOT NULL,
    purpose_code TEXT NOT NULL,
    caller_policy_class TEXT NOT NULL,
    capsule_hash TEXT NOT NULL,
    request_semantics_hash TEXT NOT NULL,
    candidate_set_hash TEXT NOT NULL,
    authority_hash TEXT NOT NULL,
    freshness_hash TEXT NOT NULL,
    policy_version TEXT NOT NULL,
    validator_id TEXT NOT NULL,
    validator_version TEXT NOT NULL,
    deterministic_method_version TEXT NOT NULL,
    output_schema_version TEXT NOT NULL,
    tool_registry_hash TEXT,
    repository_snapshot_hash TEXT,
    runtime_signature_hash TEXT,
    configuration_hash TEXT,
    request_semantics_json TEXT NOT NULL,
    cache_key_json TEXT NOT NULL,
    result_payload TEXT NOT NULL,
    result_hash TEXT NOT NULL,
    validation_status TEXT NOT NULL,
    validation_json TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    invalidation_dependencies_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_accessed_at TEXT NOT NULL,
    access_count INTEGER NOT NULL DEFAULT 0,
    invalidated_at TEXT,
    invalidation_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_decision_cache_entries_namespace
    ON decision_cache_entries(cache_namespace);

CREATE INDEX IF NOT EXISTS idx_decision_cache_entries_decision_type
    ON decision_cache_entries(decision_type);

CREATE INDEX IF NOT EXISTS idx_decision_cache_entries_boundary_id
    ON decision_cache_entries(boundary_id);

CREATE INDEX IF NOT EXISTS idx_decision_cache_entries_request_semantics_hash
    ON decision_cache_entries(request_semantics_hash);

CREATE INDEX IF NOT EXISTS idx_decision_cache_entries_capsule_hash
    ON decision_cache_entries(capsule_hash);

CREATE INDEX IF NOT EXISTS idx_decision_cache_entries_authority_hash
    ON decision_cache_entries(authority_hash);

CREATE INDEX IF NOT EXISTS idx_decision_cache_entries_freshness_hash
    ON decision_cache_entries(freshness_hash);

CREATE INDEX IF NOT EXISTS idx_decision_cache_entries_invalidated_at
    ON decision_cache_entries(invalidated_at);

CREATE TABLE IF NOT EXISTS decision_cache_events (
    event_id TEXT PRIMARY KEY NOT NULL,
    event_type TEXT NOT NULL,
    cache_key TEXT NOT NULL,
    cache_class TEXT NOT NULL,
    decision_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    caller_id TEXT NOT NULL,
    boundary_id TEXT NOT NULL,
    purpose_code TEXT NOT NULL,
    capsule_hash TEXT NOT NULL,
    request_semantics_hash TEXT NOT NULL,
    outcome TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    lookup_time_ms REAL NOT NULL,
    result_age_ms REAL,
    access_count INTEGER NOT NULL,
    details_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_decision_cache_events_cache_key
    ON decision_cache_events(cache_key);

CREATE INDEX IF NOT EXISTS idx_decision_cache_events_event_type
    ON decision_cache_events(event_type);

CREATE INDEX IF NOT EXISTS idx_decision_cache_events_timestamp
    ON decision_cache_events(timestamp);
"""


def _stable_json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _open_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=DEFAULT_CACHE_TIMEOUT_S)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
    except sqlite3.Error:
        pass
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _load_json_text(raw: str | None) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _dependencies_match(stored: Mapping[str, Any], current: Mapping[str, Any]) -> tuple[bool, str]:
    for key, value in dict(stored or {}).items():
        current_value = (current or {}).get(key)
        if value != current_value:
            return False, f"KEY_MISS_BY_CHANGED_DEPENDENCY:{key}"
    return True, "CACHE_DEPENDENCIES_MATCH"


def _build_event_row(
    *,
    event_type: str,
    cache_key: str,
    cache_class: str,
    decision_type: str,
    timestamp: str,
    caller_id: str,
    boundary_id: str,
    purpose_code: str,
    capsule_hash: str,
    request_semantics_hash: str,
    outcome: str,
    reason_code: str,
    lookup_time_ms: float,
    result_age_ms: float | None,
    access_count: int,
    details: Mapping[str, Any],
) -> Dict[str, Any]:
    return {
        "event_id": uuid.uuid4().hex,
        "event_type": event_type,
        "cache_key": cache_key,
        "cache_class": cache_class,
        "decision_type": decision_type,
        "timestamp": timestamp,
        "caller_id": caller_id,
        "boundary_id": boundary_id,
        "purpose_code": purpose_code,
        "capsule_hash": capsule_hash,
        "request_semantics_hash": request_semantics_hash,
        "outcome": outcome,
        "reason_code": reason_code,
        "lookup_time_ms": float(lookup_time_ms),
        "result_age_ms": result_age_ms,
        "access_count": int(access_count),
        "details_json": _stable_json_text(dict(details or {})),
    }


def _validate_entry_payload(entry: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required = (
        "cache_key",
        "cache_namespace",
        "decision_type",
        "cache_class",
        "source",
        "boundary_id",
        "purpose_code",
        "caller_policy_class",
        "capsule_hash",
        "request_semantics_hash",
        "candidate_set_hash",
        "authority_hash",
        "freshness_hash",
        "policy_version",
        "validator_id",
        "validator_version",
        "deterministic_method_version",
        "output_schema_version",
        "request_semantics_json",
        "cache_key_json",
        "result_payload",
        "result_hash",
        "validation_status",
        "validation_json",
        "provenance_json",
        "invalidation_dependencies_json",
        "created_at",
        "last_accessed_at",
        "access_count",
    )
    for field in required:
        if field not in entry:
            errors.append(f"missing_entry_field:{field}")
    if not isinstance(entry.get("result_payload"), str):
        errors.append("result_payload_not_string")
    if not isinstance(entry.get("validation_json"), str):
        errors.append("validation_json_not_string")
    if not isinstance(entry.get("provenance_json"), str):
        errors.append("provenance_json_not_string")
    if not isinstance(entry.get("invalidation_dependencies_json"), str):
        errors.append("invalidation_dependencies_json_not_string")
    return errors


def _should_write_negative_cache(result: Mapping[str, Any], classification: Dict[str, Any]) -> bool:
    if classification.get("cache_class") != CLASS_C_REJECTED_OR_FAILED_OUTPUT:
        return False
    backend_status = normalize_string(result.get("backend_status"), uppercase=True)
    return backend_status in {"DENIED"}


@dataclass(frozen=True)
class CacheLookupResult:
    hit: bool
    cache_key: str
    cache_class: str
    decision_type: str
    reason_code: str
    result: Dict[str, Any] | None = None
    entry: Dict[str, Any] | None = None
    validation_errors: list[str] | None = None
    lookup_time_ms: float = 0.0
    result_age_ms: float | None = None
    access_count: int = 0
    event_ids: tuple[str, ...] = ()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "hit": self.hit,
            "cache_key": self.cache_key,
            "cache_class": self.cache_class,
            "decision_type": self.decision_type,
            "reason_code": self.reason_code,
            "result": dict(self.result or {}),
            "entry": dict(self.entry or {}),
            "validation_errors": list(self.validation_errors or []),
            "lookup_time_ms": float(self.lookup_time_ms),
            "result_age_ms": self.result_age_ms,
            "access_count": int(self.access_count),
            "event_ids": list(self.event_ids),
        }


class DecisionCacheStore:
    def __init__(
        self,
        db_path: str | Path | None = None,
        *,
        namespace: str = CACHE_NAMESPACE_DEFAULT,
        policy_version: str = CACHE_POLICY_VERSION,
    ) -> None:
        self.db_path = Path(db_path) if db_path is not None else DEFAULT_DECISION_CACHE_DB_PATH
        self.namespace = normalize_string(namespace)
        self.policy_version = normalize_string(policy_version)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with _open_connection(self.db_path) as conn:
            conn.executescript(CACHE_SCHEMA_SQL)
            conn.commit()

    def _emit_event(
        self,
        conn: sqlite3.Connection,
        *,
        event_type: str,
        cache_key: str,
        cache_class: str,
        decision_type: str,
        caller_id: str,
        boundary_id: str,
        purpose_code: str,
        capsule_hash: str,
        request_semantics_hash: str,
        outcome: str,
        reason_code: str,
        lookup_time_ms: float,
        result_age_ms: float | None,
        access_count: int,
        details: Mapping[str, Any],
    ) -> str:
        if event_type not in CACHE_EVENT_TYPES:
            raise ValueError(f"invalid cache event type: {event_type}")
        timestamp = _utc_now()
        row = _build_event_row(
            event_type=event_type,
            cache_key=cache_key,
            cache_class=cache_class,
            decision_type=decision_type,
            timestamp=timestamp,
            caller_id=caller_id,
            boundary_id=boundary_id,
            purpose_code=purpose_code,
            capsule_hash=capsule_hash,
            request_semantics_hash=request_semantics_hash,
            outcome=outcome,
            reason_code=reason_code,
            lookup_time_ms=lookup_time_ms,
            result_age_ms=result_age_ms,
            access_count=access_count,
            details=details,
        )
        conn.execute(
            """
            INSERT INTO decision_cache_events (
                event_id,
                event_type,
                cache_key,
                cache_class,
                decision_type,
                timestamp,
                caller_id,
                boundary_id,
                purpose_code,
                capsule_hash,
                request_semantics_hash,
                outcome,
                reason_code,
                lookup_time_ms,
                result_age_ms,
                access_count,
                details_json
            ) VALUES (
                :event_id,
                :event_type,
                :cache_key,
                :cache_class,
                :decision_type,
                :timestamp,
                :caller_id,
                :boundary_id,
                :purpose_code,
                :capsule_hash,
                :request_semantics_hash,
                :outcome,
                :reason_code,
                :lookup_time_ms,
                :result_age_ms,
                :access_count,
                :details_json
            )
            """,
            row,
        )
        return row["event_id"]

    def lookup(self, cache_request: Mapping[str, Any]) -> CacheLookupResult:
        started = time.perf_counter()
        request = dict(cache_request or {})
        cache_key = normalize_string(request.get("cache_key"))
        decision_type = normalize_string(request.get("decision_type"))
        cache_class = normalize_string(request.get("cache_class_hint") or request.get("cache_class") or CLASS_A_DETERMINISTIC_RESULT, uppercase=True)
        boundary_id = normalize_string(request.get("boundary_id"))
        caller_id = normalize_string(request.get("caller_id"))
        purpose_code = normalize_string(request.get("purpose_code"))
        capsule_hash = normalize_string(request.get("capsule_hash"))
        request_semantics_hash = normalize_string(request.get("request_semantics_hash"))
        current_dependencies = dict(request.get("invalidation_dependencies") or {})

        with _open_connection(self.db_path) as conn:
            lookup_event_ids: list[str] = []
            lookup_event_ids.append(
                self._emit_event(
                    conn,
                    event_type="CACHE_LOOKUP",
                    cache_key=cache_key,
                    cache_class=cache_class,
                    decision_type=decision_type,
                    caller_id=caller_id,
                    boundary_id=boundary_id,
                    purpose_code=purpose_code,
                    capsule_hash=capsule_hash,
                    request_semantics_hash=request_semantics_hash,
                    outcome="LOOKUP",
                    reason_code="LOOKUP_STARTED",
                    lookup_time_ms=0.0,
                    result_age_ms=None,
                    access_count=0,
                    details={"cache_namespace": normalize_string(request.get("cache_namespace", self.namespace))},
                )
            )

            row = conn.execute(
                "SELECT * FROM decision_cache_entries WHERE cache_key = ? LIMIT 1",
                (cache_key,),
            ).fetchone()
            if row is None:
                lookup_time_ms = (time.perf_counter() - started) * 1000.0
                self._emit_event(
                    conn,
                    event_type="CACHE_MISS",
                    cache_key=cache_key,
                    cache_class=cache_class,
                    decision_type=decision_type,
                    caller_id=caller_id,
                    boundary_id=boundary_id,
                    purpose_code=purpose_code,
                    capsule_hash=capsule_hash,
                    request_semantics_hash=request_semantics_hash,
                    outcome="MISS",
                    reason_code="CACHE_KEY_MISS",
                    lookup_time_ms=lookup_time_ms,
                    result_age_ms=None,
                    access_count=0,
                    details={"cache_namespace": normalize_string(request.get("cache_namespace", self.namespace))},
                )
                conn.commit()
                return CacheLookupResult(
                    hit=False,
                    cache_key=cache_key,
                    cache_class=cache_class,
                    decision_type=decision_type,
                    reason_code="CACHE_KEY_MISS",
                    lookup_time_ms=lookup_time_ms,
                    event_ids=tuple(lookup_event_ids),
                )

            entry = dict(row)
            stored_dependencies = _load_json_text(entry.get("invalidation_dependencies_json"))
            dependencies_match, dependency_reason = _dependencies_match(stored_dependencies, current_dependencies)
            if entry.get("invalidated_at") is not None:
                dependencies_match = False
                dependency_reason = normalize_string(entry.get("invalidation_reason") or "CACHE_INVALIDATED")

            if not dependencies_match:
                invalidation_reason = dependency_reason or "CACHE_INVALIDATED"
                conn.execute(
                    """
                    UPDATE decision_cache_entries
                    SET invalidated_at = COALESCE(invalidated_at, ?),
                        invalidation_reason = COALESCE(invalidation_reason, ?)
                    WHERE cache_key = ?
                    """,
                    (_utc_now(), invalidation_reason, cache_key),
                )
                lookup_time_ms = (time.perf_counter() - started) * 1000.0
                self._emit_event(
                    conn,
                    event_type="CACHE_INVALIDATED",
                    cache_key=cache_key,
                    cache_class=normalize_string(entry.get("cache_class"), uppercase=True),
                    decision_type=normalize_string(entry.get("decision_type")),
                    caller_id=caller_id,
                    boundary_id=boundary_id,
                    purpose_code=purpose_code,
                    capsule_hash=capsule_hash,
                    request_semantics_hash=request_semantics_hash,
                    outcome="MISS",
                    reason_code=invalidation_reason,
                    lookup_time_ms=lookup_time_ms,
                    result_age_ms=None,
                    access_count=int(entry.get("access_count", 0) or 0),
                    details={"dependency_reason": dependency_reason},
                )
                self._emit_event(
                    conn,
                    event_type="CACHE_MISS",
                    cache_key=cache_key,
                    cache_class=normalize_string(entry.get("cache_class"), uppercase=True),
                    decision_type=normalize_string(entry.get("decision_type")),
                    caller_id=caller_id,
                    boundary_id=boundary_id,
                    purpose_code=purpose_code,
                    capsule_hash=capsule_hash,
                    request_semantics_hash=request_semantics_hash,
                    outcome="MISS",
                    reason_code=invalidation_reason,
                    lookup_time_ms=lookup_time_ms,
                    result_age_ms=None,
                    access_count=int(entry.get("access_count", 0) or 0),
                    details={"dependency_reason": dependency_reason},
                )
                conn.commit()
                return CacheLookupResult(
                    hit=False,
                    cache_key=cache_key,
                    cache_class=normalize_string(entry.get("cache_class"), uppercase=True),
                    decision_type=normalize_string(entry.get("decision_type")),
                    reason_code=invalidation_reason,
                    lookup_time_ms=lookup_time_ms,
                    access_count=int(entry.get("access_count", 0) or 0),
                    event_ids=tuple(lookup_event_ids),
                )

            result_payload = _load_json_text(entry.get("result_payload"))
            validation_errors = validate_semantic_readout_reply_payload(result_payload)
            stored_result_hash = normalize_string(entry.get("result_hash"))
            computed_result_hash = hash_json_value(result_payload) if result_payload else ""
            if validation_errors or (stored_result_hash and stored_result_hash != computed_result_hash):
                invalidation_reason = "CACHE_REVALIDATION_FAILED" if validation_errors else "CACHE_CORRUPT"
                conn.execute(
                    """
                    UPDATE decision_cache_entries
                    SET invalidated_at = COALESCE(invalidated_at, ?),
                        invalidation_reason = COALESCE(invalidation_reason, ?)
                    WHERE cache_key = ?
                    """,
                    (_utc_now(), invalidation_reason, cache_key),
                )
                lookup_time_ms = (time.perf_counter() - started) * 1000.0
                self._emit_event(
                    conn,
                    event_type="CACHE_REVALIDATION_FAILED" if validation_errors else "CACHE_CORRUPT",
                    cache_key=cache_key,
                    cache_class=normalize_string(entry.get("cache_class"), uppercase=True),
                    decision_type=normalize_string(entry.get("decision_type")),
                    caller_id=caller_id,
                    boundary_id=boundary_id,
                    purpose_code=purpose_code,
                    capsule_hash=capsule_hash,
                    request_semantics_hash=request_semantics_hash,
                    outcome="MISS",
                    reason_code=invalidation_reason,
                    lookup_time_ms=lookup_time_ms,
                    result_age_ms=None,
                    access_count=int(entry.get("access_count", 0) or 0),
                    details={"validation_errors": validation_errors, "hash_mismatch": stored_result_hash != computed_result_hash},
                )
                conn.commit()
                return CacheLookupResult(
                    hit=False,
                    cache_key=cache_key,
                    cache_class=normalize_string(entry.get("cache_class"), uppercase=True),
                    decision_type=normalize_string(entry.get("decision_type")),
                    reason_code=invalidation_reason,
                    validation_errors=validation_errors,
                    lookup_time_ms=lookup_time_ms,
                    access_count=int(entry.get("access_count", 0) or 0),
                    event_ids=tuple(lookup_event_ids),
                )

            access_count = int(entry.get("access_count", 0) or 0) + 1
            now = _utc_now()
            created_at = entry.get("created_at")
            result_age_ms = None
            if created_at:
                try:
                    created_dt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00"))
                    result_age_ms = max(0.0, (datetime.now(timezone.utc) - created_dt).total_seconds() * 1000.0)
                except ValueError:
                    result_age_ms = None
            conn.execute(
                """
                UPDATE decision_cache_entries
                SET last_accessed_at = ?, access_count = ?
                WHERE cache_key = ?
                """,
                (now, access_count, cache_key),
            )
            lookup_time_ms = (time.perf_counter() - started) * 1000.0
            self._emit_event(
                conn,
                event_type="CACHE_HIT",
                cache_key=cache_key,
                cache_class=normalize_string(entry.get("cache_class"), uppercase=True),
                decision_type=normalize_string(entry.get("decision_type")),
                caller_id=caller_id,
                boundary_id=boundary_id,
                purpose_code=purpose_code,
                capsule_hash=capsule_hash,
                request_semantics_hash=request_semantics_hash,
                outcome="HIT",
                reason_code="CACHE_HIT",
                lookup_time_ms=lookup_time_ms,
                result_age_ms=result_age_ms,
                access_count=access_count,
                details={"cache_namespace": normalize_string(entry.get("cache_namespace", self.namespace))},
            )
            conn.commit()
            return CacheLookupResult(
                hit=True,
                cache_key=cache_key,
                cache_class=normalize_string(entry.get("cache_class"), uppercase=True),
                decision_type=normalize_string(entry.get("decision_type")),
                reason_code="CACHE_HIT",
                result=result_payload,
                entry=entry,
                lookup_time_ms=lookup_time_ms,
                result_age_ms=result_age_ms,
                access_count=access_count,
                event_ids=tuple(lookup_event_ids),
            )

    def store_result(
        self,
        cache_request: Mapping[str, Any],
        result: Mapping[str, Any],
        *,
        validator: Callable[[Mapping[str, Any]], list[str]] = validate_semantic_readout_reply_payload,
    ) -> Dict[str, Any]:
        request = dict(cache_request or {})
        result_payload = dict(result or {})
        classification = classify_semantic_readout_result(result_payload)
        if not classification.get("cacheable", False):
            with _open_connection(self.db_path) as conn:
                self._emit_event(
                    conn,
                    event_type="CACHE_WRITE_SKIPPED",
                    cache_key=normalize_string(request.get("cache_key")),
                    cache_class=normalize_string(classification.get("cache_class"), uppercase=True),
                    decision_type=normalize_string(request.get("decision_type")),
                    caller_id=normalize_string(request.get("caller_id")),
                    boundary_id=normalize_string(request.get("boundary_id")),
                    purpose_code=normalize_string(request.get("purpose_code")),
                    capsule_hash=normalize_string(request.get("capsule_hash")),
                    request_semantics_hash=normalize_string(request.get("request_semantics_hash")),
                    outcome="SKIPPED",
                    reason_code=normalize_string(classification.get("reason_code")),
                    lookup_time_ms=0.0,
                    result_age_ms=None,
                    access_count=0,
                    details={"source": classification.get("source")},
                )
                conn.commit()
            return {
                "written": False,
                "reason_code": normalize_string(classification.get("reason_code")),
                "cache_class": classification.get("cache_class"),
                "source": classification.get("source"),
            }

        validation_errors = validator(result_payload)
        if validation_errors:
            with _open_connection(self.db_path) as conn:
                self._emit_event(
                    conn,
                    event_type="CACHE_WRITE_SKIPPED",
                    cache_key=normalize_string(request.get("cache_key")),
                    cache_class=normalize_string(classification.get("cache_class"), uppercase=True),
                    decision_type=normalize_string(request.get("decision_type")),
                    caller_id=normalize_string(request.get("caller_id")),
                    boundary_id=normalize_string(request.get("boundary_id")),
                    purpose_code=normalize_string(request.get("purpose_code")),
                    capsule_hash=normalize_string(request.get("capsule_hash")),
                    request_semantics_hash=normalize_string(request.get("request_semantics_hash")),
                    outcome="SKIPPED",
                    reason_code="RESULT_VALIDATION_FAILED",
                    lookup_time_ms=0.0,
                    result_age_ms=None,
                    access_count=0,
                    details={"validation_errors": validation_errors},
                )
                conn.commit()
            return {
                "written": False,
                "reason_code": "RESULT_VALIDATION_FAILED",
                "cache_class": classification.get("cache_class"),
                "source": classification.get("source"),
                "validation_errors": validation_errors,
            }

        stored_result = build_cached_result_payload(
            result_payload,
            cache_key=normalize_string(request.get("cache_key")),
            cache_class=normalize_string(classification.get("cache_class"), uppercase=True),
            cache_namespace=normalize_string(request.get("cache_namespace", self.namespace)),
            stored_reply_source=normalize_string(classification.get("stored_reply_source")),
            cache_hit=True,
        )
        cache_key = normalize_string(request.get("cache_key"))
        cache_key_payload = request.get("cache_key_payload") or {}
        provenance = build_provenance_record(
            request_semantics_hash=normalize_string(request.get("request_semantics_hash")),
            capsule_hash=normalize_string(request.get("capsule_hash")),
            boundary_id=normalize_string(request.get("boundary_id")),
            purpose_code=normalize_string(request.get("purpose_code")),
            policy_version=normalize_string(request.get("boundary_policy_version") or self.policy_version),
            candidate_set_hash=normalize_string(request.get("candidate_set_hash")),
            authority_hash=normalize_string(request.get("authority_hash")),
            freshness_hash=normalize_string(request.get("freshness_hash")),
            cache_namespace=normalize_string(request.get("cache_namespace", self.namespace)),
            decision_type=normalize_string(request.get("decision_type")),
        )
        validation = build_validation_record(
            validated_at=_utc_now(),
            validator_id=normalize_string(request.get("validator_id") or DEFAULT_VALIDATOR_ID),
            validator_version=normalize_string(request.get("validator_version") or DEFAULT_VALIDATOR_VERSION),
            schema_id=normalize_string(result_payload.get("schema_id") or DEFAULT_RESULT_SCHEMA_ID),
            schema_version=normalize_string(result_payload.get("schema_version") or DECISION_CACHE_SCHEMA_VERSION),
        )
        invalidation_dependencies = dict(request.get("invalidation_dependencies") or {})
        now = _utc_now()
        entry = {
            "cache_key": cache_key,
            "cache_namespace": normalize_string(request.get("cache_namespace", self.namespace)),
            "decision_type": normalize_string(request.get("decision_type")),
            "cache_class": normalize_string(classification.get("cache_class"), uppercase=True),
            "source": normalize_string(classification.get("source")),
            "boundary_id": normalize_string(request.get("boundary_id")),
            "purpose_code": normalize_string(request.get("purpose_code")),
            "caller_policy_class": normalize_string(request.get("caller_policy_class"), uppercase=True),
            "capsule_hash": normalize_string(request.get("capsule_hash")),
            "request_semantics_hash": normalize_string(request.get("request_semantics_hash")),
            "candidate_set_hash": normalize_string(request.get("candidate_set_hash")),
            "authority_hash": normalize_string(request.get("authority_hash")),
            "freshness_hash": normalize_string(request.get("freshness_hash")),
            "policy_version": normalize_string(request.get("boundary_policy_version") or self.policy_version),
            "validator_id": normalize_string(request.get("validator_id") or DEFAULT_VALIDATOR_ID),
            "validator_version": normalize_string(request.get("validator_version") or DEFAULT_VALIDATOR_VERSION),
            "deterministic_method_version": normalize_string(request.get("deterministic_method_version") or DEFAULT_DETERMINISTIC_METHOD_VERSION),
            "output_schema_version": normalize_string(request.get("output_schema_version") or DEFAULT_OUTPUT_SCHEMA_VERSION),
            "tool_registry_hash": normalize_string(request.get("tool_registry_hash")) if request.get("tool_registry_hash") else None,
            "repository_snapshot_hash": normalize_string(request.get("repository_snapshot_hash")) if request.get("repository_snapshot_hash") else None,
            "runtime_signature_hash": normalize_string(request.get("runtime_signature_hash")) if request.get("runtime_signature_hash") else None,
            "configuration_hash": normalize_string(request.get("configuration_hash")) if request.get("configuration_hash") else None,
            "request_semantics_json": _stable_json_text(request.get("request_semantics") or {}),
            "cache_key_json": _stable_json_text(cache_key_payload),
            "result_payload": _stable_json_text(stored_result),
            "result_hash": hash_json_value(stored_result),
            "validation_status": validation["status"],
            "validation_json": _stable_json_text(validation),
            "provenance_json": _stable_json_text(provenance),
            "invalidation_dependencies_json": _stable_json_text(invalidation_dependencies),
            "created_at": now,
            "last_accessed_at": now,
            "access_count": 0,
            "invalidated_at": None,
            "invalidation_reason": None,
        }
        errors = _validate_entry_payload(entry)
        if errors:
            return {
                "written": False,
                "reason_code": "ENTRY_VALIDATION_FAILED",
                "cache_class": classification.get("cache_class"),
                "source": classification.get("source"),
                "validation_errors": errors,
            }

        with _open_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO decision_cache_entries (
                    cache_key,
                    cache_namespace,
                    decision_type,
                    cache_class,
                    source,
                    boundary_id,
                    purpose_code,
                    caller_policy_class,
                    capsule_hash,
                    request_semantics_hash,
                    candidate_set_hash,
                    authority_hash,
                    freshness_hash,
                    policy_version,
                    validator_id,
                    validator_version,
                    deterministic_method_version,
                    output_schema_version,
                    tool_registry_hash,
                    repository_snapshot_hash,
                    runtime_signature_hash,
                    configuration_hash,
                    request_semantics_json,
                    cache_key_json,
                    result_payload,
                    result_hash,
                    validation_status,
                    validation_json,
                    provenance_json,
                    invalidation_dependencies_json,
                    created_at,
                    last_accessed_at,
                    access_count,
                    invalidated_at,
                    invalidation_reason
                ) VALUES (
                    :cache_key,
                    :cache_namespace,
                    :decision_type,
                    :cache_class,
                    :source,
                    :boundary_id,
                    :purpose_code,
                    :caller_policy_class,
                    :capsule_hash,
                    :request_semantics_hash,
                    :candidate_set_hash,
                    :authority_hash,
                    :freshness_hash,
                    :policy_version,
                    :validator_id,
                    :validator_version,
                    :deterministic_method_version,
                    :output_schema_version,
                    :tool_registry_hash,
                    :repository_snapshot_hash,
                    :runtime_signature_hash,
                    :configuration_hash,
                    :request_semantics_json,
                    :cache_key_json,
                    :result_payload,
                    :result_hash,
                    :validation_status,
                    :validation_json,
                    :provenance_json,
                    :invalidation_dependencies_json,
                    :created_at,
                    :last_accessed_at,
                    :access_count,
                    :invalidated_at,
                    :invalidation_reason
                )
                ON CONFLICT(cache_key) DO UPDATE SET
                    cache_namespace = excluded.cache_namespace,
                    decision_type = excluded.decision_type,
                    cache_class = excluded.cache_class,
                    source = excluded.source,
                    boundary_id = excluded.boundary_id,
                    purpose_code = excluded.purpose_code,
                    caller_policy_class = excluded.caller_policy_class,
                    capsule_hash = excluded.capsule_hash,
                    request_semantics_hash = excluded.request_semantics_hash,
                    candidate_set_hash = excluded.candidate_set_hash,
                    authority_hash = excluded.authority_hash,
                    freshness_hash = excluded.freshness_hash,
                    policy_version = excluded.policy_version,
                    validator_id = excluded.validator_id,
                    validator_version = excluded.validator_version,
                    deterministic_method_version = excluded.deterministic_method_version,
                    output_schema_version = excluded.output_schema_version,
                    tool_registry_hash = excluded.tool_registry_hash,
                    repository_snapshot_hash = excluded.repository_snapshot_hash,
                    runtime_signature_hash = excluded.runtime_signature_hash,
                    configuration_hash = excluded.configuration_hash,
                    request_semantics_json = excluded.request_semantics_json,
                    cache_key_json = excluded.cache_key_json,
                    result_payload = excluded.result_payload,
                    result_hash = excluded.result_hash,
                    validation_status = excluded.validation_status,
                    validation_json = excluded.validation_json,
                    provenance_json = excluded.provenance_json,
                    invalidation_dependencies_json = excluded.invalidation_dependencies_json,
                    created_at = excluded.created_at,
                    last_accessed_at = excluded.last_accessed_at,
                    access_count = excluded.access_count,
                    invalidated_at = excluded.invalidated_at,
                    invalidation_reason = excluded.invalidation_reason
                """,
                entry,
            )
            self._emit_event(
                conn,
                event_type="CACHE_WRITE",
                cache_key=cache_key,
                cache_class=normalize_string(classification.get("cache_class"), uppercase=True),
                decision_type=normalize_string(request.get("decision_type")),
                caller_id=normalize_string(request.get("caller_id")),
                boundary_id=normalize_string(request.get("boundary_id")),
                purpose_code=normalize_string(request.get("purpose_code")),
                capsule_hash=normalize_string(request.get("capsule_hash")),
                request_semantics_hash=normalize_string(request.get("request_semantics_hash")),
                outcome="WRITE",
                reason_code=normalize_string(classification.get("reason_code")),
                lookup_time_ms=0.0,
                result_age_ms=None,
                access_count=0,
                details={"source": classification.get("source"), "validation_status": validation["status"]},
            )
            conn.commit()

        return {
            "written": True,
            "reason_code": normalize_string(classification.get("reason_code")),
            "cache_class": classification.get("cache_class"),
            "source": classification.get("source"),
            "stored_result": stored_result,
            "validation": validation,
            "provenance": provenance,
            "entry": entry,
        }

    def invalidate(self, cache_key: str, reason: str) -> Dict[str, Any]:
        key = normalize_string(cache_key)
        now = _utc_now()
        with _open_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT cache_class, decision_type, boundary_id, caller_policy_class, capsule_hash, request_semantics_hash, access_count FROM decision_cache_entries WHERE cache_key = ? LIMIT 1",
                (key,),
            ).fetchone()
            if row is None:
                return {"invalidated": False, "reason_code": "CACHE_KEY_MISSING"}
            conn.execute(
                """
                UPDATE decision_cache_entries
                SET invalidated_at = COALESCE(invalidated_at, ?),
                    invalidation_reason = COALESCE(invalidation_reason, ?)
                WHERE cache_key = ?
                """,
                (now, normalize_string(reason), key),
            )
            self._emit_event(
                conn,
                event_type="CACHE_INVALIDATED",
                cache_key=key,
                cache_class=normalize_string(row["cache_class"], uppercase=True),
                decision_type=normalize_string(row["decision_type"]),
                caller_id="",
                boundary_id=normalize_string(row["boundary_id"]),
                purpose_code="",
                capsule_hash=normalize_string(row["capsule_hash"]),
                request_semantics_hash=normalize_string(row["request_semantics_hash"]),
                outcome="INVALIDATED",
                reason_code=normalize_string(reason),
                lookup_time_ms=0.0,
                result_age_ms=None,
                access_count=int(row["access_count"] or 0),
                details={"invalidation_reason": normalize_string(reason)},
            )
            conn.commit()
        return {"invalidated": True, "reason_code": normalize_string(reason)}
