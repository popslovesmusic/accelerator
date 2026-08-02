import argparse
import hashlib
import json
import sqlite3
import sys
import re
import subprocess
import uuid
import time
from fnmatch import fnmatch
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DEFAULT_DB = ROOT / "registry/db/acellorator_index.sqlite"
DEFAULT_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_bootstrap_001.sql"
CURRENT_STATE_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_current_state_002.sql"
AUTHORITY_RESOLUTION_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql"
PATCH_CHAIN_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_patch_chain_004.sql"
DEBT_RUNTIME_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_debt_view_005.sql"
CONTEXT_CAPSULE_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_context_capsule_006.sql"
EVENT_BUS_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_event_bus_007.sql"
EVENT_REPLAY_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_event_replay_008.sql"
EVENT_RECONCILIATION_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_replay_reconciliation_009.sql"
FRESHNESS_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_freshness_gate_010.sql"
SNAPSHOT_REFRESH_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_snapshot_refresh_011.sql"
REFRESH_STABILITY_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_refresh_stability_012.sql"
SEMANTIC_AUTHORITY_MIGRATION = ROOT / "registry/db/migrations/20260703_governance_runtime_semantic_authority_013.sql"
GLOBAL_HEALTH_REPORT = ROOT / "outputs/audits/global_health_report.json"
GOVERNANCE_EVIDENCE_DIR = ROOT / "outputs/governance/evidence"
GOVERNANCE_CHANGE_LEDGER = ROOT / "registry/governance_change_ledger.json"
RESEARCH_DEBT_REGISTRY = ROOT / "registry/research_debt_registry.json"
PATCH_REGISTRY_DIR = ROOT / "registry/governance/patches"
SEMANTIC_AUTHORITY_REGISTRY = ROOT / "registry/theorem_registry.json"
CLAIM_REGISTRY = ROOT / "registry/claim_registry.json"
CLAIM_SUPPORT_MATRIX = ROOT / "registry/claim_support_matrix.json"
GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION = "governed_context_capsule_v1"
GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE = "1.0.0"
GOVERNED_CONTEXT_CAPSULE_CACHE_DIR = ROOT / "outputs/governance/context_capsules" / GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION

try:
    from scripts.orientation_retrieval import retrieve_artifacts
except ImportError:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from scripts.orientation_retrieval import retrieve_artifacts

try:
    from scripts.registry_runtime_trace import run_registry_runtime_trace
except ImportError:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from scripts.registry_runtime_trace import run_registry_runtime_trace

try:
    from scripts.claim_evidence_graph import build_claim_evidence_graph
except ImportError:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from scripts.claim_evidence_graph import build_claim_evidence_graph

try:
    from scripts.db.db_health_check import run_db_health_check
except ImportError:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from scripts.db.db_health_check import run_db_health_check

try:
    from tools.governance_inventory import build_q0_authority_scope_partition_bundle
except ImportError:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from tools.governance_inventory import build_q0_authority_scope_partition_bundle

try:
    from tools.runtime_authority import (
        ROLE_IDS as Q0_ROLE_IDS,
        classify_patch_record_closeout_work_package,
        classify_patch_record_deterministic_routing_component,
        classify_patch_record_executed_pass_boundary,
        classify_patch_record_explicit_none_authority_effect,
        classify_patch_record_historical_applied,
        classify_generated_view_component,
        classify_duplicate_identity_component,
        classify_patch_record_lifecycle,
        classify_target_role,
        get_authority_by_role,
        resolve_role_aware_authority,
    )
except ImportError:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from tools.runtime_authority import (
        ROLE_IDS as Q0_ROLE_IDS,
        classify_patch_record_closeout_work_package,
        classify_patch_record_deterministic_routing_component,
        classify_patch_record_executed_pass_boundary,
        classify_patch_record_explicit_none_authority_effect,
        classify_patch_record_historical_applied,
        classify_generated_view_component,
        classify_duplicate_identity_component,
        classify_patch_record_lifecycle,
        classify_target_role,
        get_authority_by_role,
        resolve_role_aware_authority,
    )

try:
    from tools.inference_governance.deterministic_router import load_operation_registry, route_parsed_request
    from tools.inference_governance.request_normalization import build_canonical_routed_request_v1, normalize_text
except ImportError:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    from tools.inference_governance.deterministic_router import load_operation_registry, route_parsed_request
    from tools.inference_governance.request_normalization import build_canonical_routed_request_v1, normalize_text


BOOTSTRAP_SQL = """\
CREATE TABLE IF NOT EXISTS governance_decision_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id TEXT UNIQUE NOT NULL,
    patch_id TEXT NOT NULL,
    campaign_id TEXT,
    requested_action TEXT,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    blocking_conditions TEXT,
    authority_resolution TEXT,
    dependency_resolution TEXT,
    provenance_resolution TEXT,
    validator_resolution TEXT,
    db_snapshot_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operator TEXT,
    evidence_json TEXT,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_governance_decision_log_patch_id
    ON governance_decision_log(patch_id);

CREATE INDEX IF NOT EXISTS idx_governance_decision_log_campaign_id
    ON governance_decision_log(campaign_id);

CREATE INDEX IF NOT EXISTS idx_governance_decision_log_created_at
    ON governance_decision_log(created_at);

CREATE VIEW IF NOT EXISTS governance_runtime_decision_view AS
SELECT
    decision_id,
    patch_id,
    campaign_id,
    requested_action,
    decision,
    reason,
    blocking_conditions,
    authority_resolution,
    dependency_resolution,
    provenance_resolution,
    validator_resolution,
    db_snapshot_at,
    created_at
FROM governance_decision_log;

CREATE VIEW IF NOT EXISTS patch_application_gate_view AS
SELECT
    decision_id,
    patch_id,
    campaign_id,
    requested_action AS action,
    decision,
    reason,
    blocking_conditions,
    created_at
FROM governance_decision_log;

CREATE VIEW IF NOT EXISTS authority_resolution_view AS
SELECT
    'registry' AS winning_authority,
    'registry_wins_over_db_on_conflicts' AS policy_id,
    'Registry remains authoritative; DB runtime is an operational gate only.' AS rule_text,
    'bootstrap' AS coverage_state;

CREATE VIEW IF NOT EXISTS patch_chain_view AS
SELECT
    NULL AS patch_id,
    'unknown' AS status,
    NULL AS dependencies,
    NULL AS missing_dependencies,
    'unknown' AS supersession_status,
    NULL AS superseded_by,
    'unknown' AS late_registration,
    NULL AS blockers,
    'defer' AS decision,
    'Patch-chain coverage is bootstrap only.' AS reason,
    NULL AS evidence_paths,
    'bootstrap' AS coverage_state;

CREATE VIEW IF NOT EXISTS debt_runtime_view AS
SELECT
    NULL AS debt_id,
    NULL AS title,
    NULL AS department,
    NULL AS status,
    NULL AS normalized_status,
    NULL AS severity,
    NULL AS normalized_severity,
    NULL AS domain,
    NULL AS blocking_scope,
    NULL AS owner_surface,
    NULL AS resolution_patch,
    NULL AS decision_effect,
    NULL AS evidence_paths,
    NULL AS warnings,
    'bootstrap' AS coverage_state
WHERE 0;

CREATE VIEW IF NOT EXISTS context_capsule_view AS
SELECT
    'unknown' AS global_runtime_status,
    'unknown' AS authority_boundary,
    'unknown' AS patch_status,
    'unknown' AS debt_status,
    NULL AS warnings,
    NULL AS minimal_evidence_paths,
    'bootstrap' AS coverage_state
WHERE 0;

CREATE VIEW IF NOT EXISTS current_state_view AS
SELECT
    (SELECT MAX(indexed_at) FROM artifacts) AS latest_artifact_indexed_at,
    (SELECT COUNT(*) FROM artifacts) AS artifact_count,
    (SELECT COUNT(*) FROM artifacts WHERE orientation_status = 'canonical_active') AS canonical_active_count,
    (SELECT COUNT(*) FROM artifacts WHERE orientation_status = 'active_runtime') AS active_runtime_count,
    (SELECT COUNT(*) FROM artifacts WHERE orientation_status IN (
        'historical_residue',
        'archived',
        'superseded',
        'invalidated',
        'unverified_residue'
    )) AS residue_count,
    'RT := [(ℰ≠0) ⇔R δα(ℰ>0)]' AS current_rt,
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM semantic_authority_map
            WHERE semantic_key IN ('RT_CORE', 'META_A_BINDING', 'META_B_BINDING')
              AND status = 'active'
        ) = 3 THEN 'semantic_projection_ready'
        ELSE 'semantic_projection_partial'
    END AS semantic_projection_state,
    CASE
        WHEN (SELECT COUNT(*) FROM artifacts WHERE orientation_status IN (
            'historical_residue',
            'archived',
            'superseded',
            'invalidated',
            'unverified_residue'
        )) > 0 THEN 'historical_residue_compressed'
        ELSE 'historical_residue_clear'
    END AS historical_residue_state,
    'registry' AS active_authority,
    NULL AS open_runtime_debt_count,
    NULL AS live_blocker_count,
    'partial_bootstrap' AS coverage_state;
"""


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def ensure_runtime_schema(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='governance_decision_log'"
    )
    had_decision_log = cursor.fetchone() is not None

    if DEFAULT_MIGRATION.exists():
        conn.executescript(DEFAULT_MIGRATION.read_text(encoding="utf-8"))
    else:
        conn.executescript(BOOTSTRAP_SQL)
    if CURRENT_STATE_MIGRATION.exists():
        conn.executescript(CURRENT_STATE_MIGRATION.read_text(encoding="utf-8"))
    if AUTHORITY_RESOLUTION_MIGRATION.exists():
        conn.executescript(AUTHORITY_RESOLUTION_MIGRATION.read_text(encoding="utf-8"))
    if PATCH_CHAIN_MIGRATION.exists():
        conn.executescript(PATCH_CHAIN_MIGRATION.read_text(encoding="utf-8"))
    if DEBT_RUNTIME_MIGRATION.exists():
        conn.executescript(DEBT_RUNTIME_MIGRATION.read_text(encoding="utf-8"))
    if CONTEXT_CAPSULE_MIGRATION.exists():
        conn.executescript(CONTEXT_CAPSULE_MIGRATION.read_text(encoding="utf-8"))
    if EVENT_BUS_MIGRATION.exists():
        conn.executescript(EVENT_BUS_MIGRATION.read_text(encoding="utf-8"))
    if EVENT_REPLAY_MIGRATION.exists():
        conn.executescript(EVENT_REPLAY_MIGRATION.read_text(encoding="utf-8"))
    if EVENT_RECONCILIATION_MIGRATION.exists():
        conn.executescript(EVENT_RECONCILIATION_MIGRATION.read_text(encoding="utf-8"))
    if FRESHNESS_MIGRATION.exists():
        conn.executescript(FRESHNESS_MIGRATION.read_text(encoding="utf-8"))
    if SNAPSHOT_REFRESH_MIGRATION.exists():
        conn.executescript(SNAPSHOT_REFRESH_MIGRATION.read_text(encoding="utf-8"))
    if SEMANTIC_AUTHORITY_MIGRATION.exists():
        conn.executescript(SEMANTIC_AUTHORITY_MIGRATION.read_text(encoding="utf-8"))
    ensure_snapshot_refresh_stability_columns(conn)
    conn.commit()
    return not had_decision_log


def ensure_snapshot_refresh_stability_columns(conn):
    cursor = conn.cursor()
    try:
        rows = cursor.execute("PRAGMA table_info(db_snapshot_refresh_metadata)").fetchall()
    except sqlite3.Error:
        return
    columns = {row[1] for row in rows}
    if not columns or "runtime_worktree_marker" in columns:
        return
    cursor.execute("ALTER TABLE db_snapshot_refresh_metadata ADD COLUMN runtime_worktree_marker TIMESTAMP")


def parse_timestamp(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def load_optional_json(path):
    if not path.exists():
        return None
    try:
        return load_json(path)
    except (OSError, json.JSONDecodeError):
        return None


def extract_global_validation_status(report):
    if not isinstance(report, dict):
        return "unknown"

    status = str(report.get("overall_status", "")).strip().lower()
    if status in {"pass", "success"}:
        return "pass"
    if status in {"warn", "warning", "pass_with_warnings", "degraded"}:
        return "warn"
    if status in {"fail", "failure", "error"}:
        return "fail"

    saw_warning = False
    for key in ("registry_validation", "db_validation", "implementation_validation", "campaign_validation"):
        section = report.get(key)
        if isinstance(section, dict):
            section_status = str(section.get("status", "")).strip().lower()
            if section_status in {"fail", "failure", "error"}:
                return "fail"
            if section_status in {"warn", "warning", "pass_with_warnings", "degraded"}:
                saw_warning = True
    if saw_warning:
        return "warn"
    return "unknown"


def extract_db_validation_status(report):
    if not isinstance(report, dict):
        return "unknown"

    db_section = report.get("db_validation")
    if isinstance(db_section, dict):
        section_status = str(db_section.get("status", "")).strip().lower()
        if section_status in {"pass", "success"}:
            return "pass"
        if section_status in {"warn", "warning", "pass_with_warnings", "degraded"}:
            return "warn"
        if section_status in {"fail", "failure", "error"}:
            return "fail"

        db_health = db_section.get("db_health")
        if isinstance(db_health, dict):
            health_status = str(db_health.get("status", "")).strip().lower()
            if health_status in {"pass", "success"}:
                return "pass"
            if health_status in {"warn", "warning", "pass_with_warnings", "degraded"}:
                return "warn"
            if health_status in {"fail", "failure", "error"}:
                return "fail"

    return "unknown"


def collect_governance_runtime_debt():
    registry = load_optional_json(RESEARCH_DEBT_REGISTRY)
    if not isinstance(registry, dict):
        return []

    items = []
    for item in registry.get("debt_items", []):
        if not isinstance(item, dict):
            continue
        if item.get("department") != "governance":
            continue
        if not str(item.get("introduced_by", "")).startswith("PATCH_DB_GOVERNANCE_RUNTIME"):
            continue
        if str(item.get("status", "")).lower() in {"resolved", "retired"}:
            continue
        items.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "status": item.get("status"),
                "severity": item.get("severity"),
                "resolution_priority": item.get("resolution_priority"),
                "blocks": item.get("blocks", []),
                "required_resolution": item.get("required_resolution", []),
                "depends_on": item.get("depends_on", []),
                "introduced_by": item.get("introduced_by"),
                "source_path": str(RESEARCH_DEBT_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            }
        )
    return items


def build_semantic_rt_projection(db_path, current_state=None, catalog_rows=None):
    semantic_targets = [
        {"semantic_key": "RT_CORE", "semantic_type": "theorem"},
        {"semantic_key": "META_A_BINDING", "semantic_type": "operator_binding"},
        {"semantic_key": "META_B_BINDING", "semantic_type": "operator_binding"},
        {"semantic_key": "REGISTRY_AUTHORITY_PRINCIPLE", "semantic_type": "runtime_rule"},
        {"semantic_key": "DB_RUNTIME_ROLE", "semantic_type": "runtime_rule"},
    ]
    if catalog_rows is None:
        summary = build_semantic_authority_summary(db_path, semantic_targets, current_state=current_state)
        target_decisions = summary.get("target_decisions", [])
        decision = summary.get("decision", "defer")
        reason = summary.get("reason", "Semantic RT projection is unavailable.")
        warnings = [warning for warning in dict.fromkeys(summary.get("warnings", [])) if warning]
        evidence_paths = [path for path in dict.fromkeys(path for path in summary.get("evidence_paths", []) if path)]
    else:
        target_decisions = [
            build_semantic_authority_record(
                target["semantic_key"],
                semantic_type=target["semantic_type"],
                current_state=current_state,
                catalog_rows=catalog_rows,
            )
            for target in semantic_targets
        ]
        warnings = []
        evidence_paths = []
        decision = "allow"
        reason = "Semantic authority checks passed."
        for record in target_decisions:
            warnings.extend(record.get("warnings", []))
            evidence_paths.extend(record.get("evidence_paths", []))
            record_decision = str(record.get("decision", "defer")).lower()
            if record_decision == "block":
                decision = "block"
                reason = f"Semantic authority blocked for {record.get('semantic_key')}"
            elif record_decision == "defer" and decision != "block":
                decision = "defer"
                reason = f"Semantic authority deferred for {record.get('semantic_key')}"
    indexed = {
        str(record.get("semantic_key") or "").strip(): record
        for record in target_decisions
        if isinstance(record, dict)
    }

    canonical_rt = "RT := [(ℰ≠0) ⇔R δα(ℰ>0)]"
    meta_a = "A_meta := δα(ℰ>0)"
    meta_b = "B_meta := (ℰ≠0)"
    authority_context = {
        "registry_principle": indexed.get("REGISTRY_AUTHORITY_PRINCIPLE", {}),
        "runtime_role": indexed.get("DB_RUNTIME_ROLE", {}),
    }
    return {
        "projection_state": "projected" if decision == "allow" else "deferred",
        "current_rt": canonical_rt,
        "meta_bindings": {
            "A_meta": meta_a,
            "B_meta": meta_b,
        },
        "domain_separation": {
            "meta_domain": "exclusive",
            "affect_effect_domain": "exclusive",
            "affect_effect_guard": "A|E remains outside RT_core",
        },
        "authority_context": authority_context,
        "target_decisions": target_decisions,
        "decision": decision,
        "reason": reason,
        "warnings": warnings,
        "evidence_paths": evidence_paths,
    }


def build_debt_blocker_projection(debt_records, current_state=None):
    records = [record for record in debt_records or [] if isinstance(record, dict)]
    blocker_records = []
    blocker_targets = []
    required_resolution = []
    dependency_edges = []
    status_counts = {}
    severity_counts = {}

    for record in records:
        status = normalize_debt_runtime_status(record.get("status"))
        severity = normalize_debt_runtime_severity(record.get("severity"))
        decision_effect = str(record.get("decision_effect") or "").strip().lower()
        if not decision_effect:
            decision_effect = "warn" if status in {"open", "partial"} else "defer" if status == "stale" else "allow"
        blocks = [str(entry).strip() for entry in parse_json_collection(record.get("blocks")) if str(entry).strip()]
        required = [str(entry).strip() for entry in parse_json_collection(record.get("required_resolution")) if str(entry).strip()]
        depends_on = [str(entry).strip() for entry in parse_json_collection(record.get("depends_on")) if str(entry).strip()]
        blocker_record = {
            "debt_id": record.get("debt_id") or record.get("id"),
            "title": record.get("title"),
            "status": status,
            "severity": severity,
            "decision_effect": decision_effect,
            "blocking_scope": record.get("blocking_scope", "none"),
            "blocks": blocks,
            "required_resolution": required,
            "depends_on": depends_on,
        }
        blocker_records.append(blocker_record)
        blocker_targets.extend(blocks)
        required_resolution.extend(required)
        if depends_on:
            dependency_edges.append(
                {
                    "debt_id": blocker_record["debt_id"],
                    "depends_on": depends_on,
                }
            )
        status_counts[status] = status_counts.get(status, 0) + 1
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    open_debt_count = sum(1 for record in blocker_records if record["status"] in {"open", "partial", "stale"})
    blocking_debt_count = sum(
        1
        for record in blocker_records
        if record["decision_effect"] == "block" or record["severity"] == "blocking"
    )
    return {
        "projection_state": "projected" if blocker_records else "empty",
        "debt_count": len(blocker_records),
        "open_debt_count": open_debt_count,
        "blocking_debt_count": blocking_debt_count,
        "status_counts": status_counts,
        "severity_counts": severity_counts,
        "blockers": [blocker for blocker in dict.fromkeys(blocker_targets) if blocker],
        "required_resolution": [item for item in dict.fromkeys(required_resolution) if item],
        "dependency_edges": dependency_edges,
        "debt_records": blocker_records,
        "coverage_state": current_state.get("coverage_state", "unknown") if current_state else "unknown",
    }


def build_historical_residue_projection(current_state=None, debt_records=None):
    state = current_state or {}
    runtime_state = state.get("runtime", {}) if isinstance(state.get("runtime"), dict) else {}
    records = [record for record in debt_records or [] if isinstance(record, dict)]
    residue_debt_count = sum(
        1
        for record in records
        if normalize_debt_runtime_status(record.get("status")) in {"open", "partial", "stale"}
    )
    residue_sources = []
    for record in records:
        if normalize_debt_runtime_status(record.get("status")) not in {"open", "partial", "stale"}:
            continue
        source = record.get("introduced_by") or record.get("source_path")
        if source:
            residue_sources.append(source)
    return {
        "projection_state": "compressed" if state.get("residue_count") or residue_debt_count else "clear",
        "artifact_count": state.get("artifact_count", runtime_state.get("artifact_count", 0)),
        "residue_count": state.get("residue_count", runtime_state.get("residue_count", 0)),
        "invalidated_count": state.get("invalidated_count", runtime_state.get("invalidated_count", 0)),
        "decision_count": state.get("decision_count", runtime_state.get("decision_count", 0)),
        "latest_decision_id": state.get("latest_decision_id") or runtime_state.get("latest_decision_id"),
        "snapshot_freshness": state.get("snapshot_freshness", runtime_state.get("snapshot_freshness", "unknown")),
        "coverage_state": state.get("coverage_state", runtime_state.get("coverage_state", "unknown")),
        "residual_debt_count": residue_debt_count,
        "residue_sources": [source for source in dict.fromkeys(residue_sources) if source],
        "compressed_statuses": [
            "historical_residue",
            "archived",
            "superseded",
            "invalidated",
            "unverified_residue",
        ],
    }


def build_replay_reconciliation_projection(conn):
    projection = {
        "projection_state": "unavailable",
        "boundary_state": "unavailable",
        "coverage_state": "unknown",
        "subject_count": 0,
        "event_count": 0,
        "latest_subject_id": None,
        "latest_subject_type": None,
        "latest_event_id": None,
        "latest_event_type": None,
        "latest_source_patch_id": None,
        "latest_source_path": None,
        "latest_created_at": None,
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_BUS_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_REPLAY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_RECONCILIATION_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
        "warnings": [],
    }

    try:
        rows = conn.execute(
            """
            SELECT
                subject_id,
                subject_type,
                latest_event_id,
                latest_event_type,
                latest_source_patch_id,
                latest_source_path,
                event_count,
                latest_created_at
            FROM governance_replay_reconciliation_view
            ORDER BY latest_created_at DESC, subject_id DESC
            """
        ).fetchall()
    except sqlite3.Error:
        projection["warnings"].append("Replay reconciliation view is unavailable.")
        return projection

    records = [dict(row) for row in rows]
    if not records:
        projection["projection_state"] = "empty"
        projection["boundary_state"] = "unavailable"
        projection["coverage_state"] = "empty"
        return projection

    latest = records[0]
    projection["projection_state"] = "projected"
    projection["boundary_state"] = "diagnostic_only"
    projection["coverage_state"] = "stateful_projection"
    projection["subject_count"] = len(records)
    projection["event_count"] = sum(int(record.get("event_count") or 0) for record in records)
    projection["latest_subject_id"] = latest.get("subject_id")
    projection["latest_subject_type"] = latest.get("subject_type")
    projection["latest_event_id"] = latest.get("latest_event_id")
    projection["latest_event_type"] = latest.get("latest_event_type")
    projection["latest_source_patch_id"] = latest.get("latest_source_patch_id")
    projection["latest_source_path"] = latest.get("latest_source_path")
    projection["latest_created_at"] = latest.get("latest_created_at")
    return projection


def collect_recent_governance_decisions(conn, limit=5):
    rows = conn.execute(
        """
        SELECT
            decision_id,
            patch_id,
            campaign_id,
            requested_action,
            decision,
            reason,
            created_at
        FROM governance_decision_log
        ORDER BY COALESCE(created_at, db_snapshot_at) DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def _canonical_json_text(value):
    encoder = json.JSONEncoder(ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "".join(encoder.iterencode(value))


def _hash_json_value(value):
    digest = hashlib.sha256()
    digest.update(_canonical_json_text(value).encode("utf-8"))
    return digest.hexdigest()


def _hash_file(path):
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return None

    digest = hashlib.sha256()
    try:
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                if not chunk:
                    break
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def _sanitize_path_component(value, fallback="unknown"):
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip())
    text = text.strip("._-")
    return text or fallback


def _governance_timestamp_slug(moment=None):
    moment = moment or datetime.now(timezone.utc)
    return moment.strftime("%Y%m%dT%H%M%S.%fZ")


def _collect_compact_governance_artifact_paths(full_evidence):
    if not isinstance(full_evidence, dict):
        return []

    candidate_paths = []
    basis = full_evidence.get("basis")
    if isinstance(basis, dict):
        candidate_paths.extend(parse_json_collection(basis.get("source_surfaces")))

    candidate_paths.extend(parse_json_collection(full_evidence.get("authority_targets")))

    for key in ("patch_chain", "semantic_resolution", "debt_resolution", "freshness_resolution"):
        section = full_evidence.get(key)
        if isinstance(section, dict):
            candidate_paths.extend(parse_json_collection(section.get("evidence_paths")))

    for change in parse_json_collection(full_evidence.get("required_repo_changes")):
        path = None
        if isinstance(change, dict):
            path = change.get("path") or change.get("source_path") or change.get("file")
        elif isinstance(change, str):
            path = change
        normalized = normalize_repo_path(path)
        if normalized:
            candidate_paths.append(normalized)

    return [path for path in dict.fromkeys(path for path in candidate_paths if path)]


def _build_governance_failure_codes(record, patch_chain):
    failure_codes = []
    for label in ("blocking_conditions", "defer_conditions"):
        for condition in parse_json_collection(record.get(label)):
            text = str(condition).strip()
            if text:
                failure_codes.append(f"{label}:{text}")

    for blocker in parse_json_collection(patch_chain.get("blockers")):
        text = str(blocker).strip()
        if text:
            failure_codes.append(f"patch_chain_blocker:{text}")

    for missing_dep in parse_json_collection(patch_chain.get("missing_dependencies")):
        text = str(missing_dep).strip()
        if text:
            failure_codes.append(f"missing_dependency:{text}")

    return [code for code in dict.fromkeys(code for code in failure_codes if code)]


def _build_governance_summary_counts(record, full_evidence, artifact_paths, artifact_hashes, dependency_patch_ids, patch_chain):
    return {
        "blocking_conditions": len(parse_json_collection(record.get("blocking_conditions"))),
        "defer_conditions": len(parse_json_collection(record.get("defer_conditions"))),
        "warnings": len(parse_json_collection(record.get("warnings"))),
        "dependency_patch_ids": len(dependency_patch_ids),
        "artifact_paths": len(artifact_paths),
        "artifact_hashes": len(artifact_hashes),
        "patch_chain_blockers": len(parse_json_collection(patch_chain.get("blockers"))),
        "patch_chain_missing_dependencies": len(parse_json_collection(patch_chain.get("missing_dependencies"))),
        "patch_chain_evidence_paths": len(parse_json_collection(patch_chain.get("evidence_paths"))),
        "authority_targets": len(parse_json_collection(full_evidence.get("authority_targets"))),
        "semantic_targets": len(parse_json_collection(full_evidence.get("semantic_targets"))),
        "required_repo_changes": len(parse_json_collection(full_evidence.get("required_repo_changes"))),
        "full_evidence_keys": len(full_evidence) if isinstance(full_evidence, dict) else 0,
    }


def _externalize_governance_decision_evidence(record, full_evidence, decision_timestamp_slug, compact_metadata=None):
    patch_id = _sanitize_path_component(record.get("patch_id"), "unknown_patch")
    evidence_dir = GOVERNANCE_EVIDENCE_DIR / patch_id
    evidence_dir.mkdir(parents=True, exist_ok=True)

    external_path = evidence_dir / f"{decision_timestamp_slug}_evidence.json"
    patch_chain = full_evidence.get("patch_chain", {})
    if not isinstance(patch_chain, dict):
        patch_chain = {}
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision_record": {
            "decision_id": record.get("decision_id"),
            "patch_id": record.get("patch_id"),
            "campaign_id": record.get("campaign_id"),
            "requested_action": record.get("requested_action"),
            "decision": record.get("decision"),
            "reason": record.get("reason"),
            "blocking_conditions": parse_json_collection(record.get("blocking_conditions")),
            "defer_conditions": parse_json_collection(record.get("defer_conditions")),
            "warnings": parse_json_collection(record.get("warnings")),
            "authority_resolution": record.get("authority_resolution", {}),
            "dependency_resolution": record.get("dependency_resolution", {}),
            "provenance_resolution": record.get("provenance_resolution", {}),
            "validator_resolution": record.get("validator_resolution", {}),
            "db_snapshot_at": record.get("db_snapshot_at"),
            "operator": record.get("operator"),
            "metadata_json": record.get("metadata_json", {}),
        },
        "evidence_summary": {
            "patch_chain_status": patch_chain.get("status"),
            "patch_chain_decision": patch_chain.get("decision"),
            "patch_gate_decision": record.get("decision"),
            "dependency_patch_ids": [
                str(dep).strip()
                for dep in parse_json_collection(patch_chain.get("dependencies"))
                if str(dep).strip()
            ],
            "failure_codes": _build_governance_failure_codes(record, patch_chain),
            "summary_counts": _build_governance_summary_counts(
                record,
                full_evidence,
                _collect_compact_governance_artifact_paths(full_evidence),
                {
                    path: file_hash
                    for path in _collect_compact_governance_artifact_paths(full_evidence)
                    if (file_hash := _hash_file(ROOT / path))
                },
                [
                    str(dep).strip()
                    for dep in parse_json_collection(patch_chain.get("dependencies"))
                    if str(dep).strip()
                ],
                patch_chain,
            ),
        },
    }
    if compact_metadata:
        payload["compact_metadata"] = compact_metadata

    temp_path = external_path.with_suffix(".json.tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    temp_path.replace(external_path)

    relative_path = str(external_path.relative_to(ROOT)).replace("\\", "/")
    return relative_path, _hash_file(external_path)


def _build_compact_governance_decision_evidence(record, *, external_evidence_path=None, external_evidence_hash=None, decision_timestamp=None):
    full_evidence = record.get("evidence_json", {})
    if not isinstance(full_evidence, dict):
        full_evidence = {}

    patch_chain = full_evidence.get("patch_chain", {})
    if not isinstance(patch_chain, dict):
        patch_chain = {}

    dependency_patch_ids = [
        str(dep).strip()
        for dep in parse_json_collection(patch_chain.get("dependencies"))
        if str(dep).strip()
    ]
    artifact_paths = _collect_compact_governance_artifact_paths(full_evidence)
    artifact_hashes = {
        path: file_hash
        for path in artifact_paths
        if (file_hash := _hash_file(ROOT / path))
    }
    summary_counts = _build_governance_summary_counts(record, full_evidence, artifact_paths, artifact_hashes, dependency_patch_ids, patch_chain)
    failure_codes = _build_governance_failure_codes(record, patch_chain)

    evidence_summary = {
        "patch_chain_status": patch_chain.get("status"),
        "patch_chain_decision": patch_chain.get("decision"),
        "patch_gate_decision": record.get("decision"),
        "patch_chain_reason": patch_chain.get("reason"),
        "patch_gate_reason": record.get("reason"),
        "dependency_count": len(dependency_patch_ids),
        "missing_dependency_count": len(parse_json_collection(patch_chain.get("missing_dependencies"))),
        "blocker_count": len(parse_json_collection(patch_chain.get("blockers"))),
        "warning_count": len(parse_json_collection(patch_chain.get("warnings"))),
        "authority_target_count": len(parse_json_collection(full_evidence.get("authority_targets"))),
        "semantic_target_count": len(parse_json_collection(full_evidence.get("semantic_targets"))),
        "artifact_path_count": len(artifact_paths),
        "patch_chain_evidence_path_count": len(parse_json_collection(patch_chain.get("evidence_paths"))),
        "provenance_has_basis": bool(full_evidence.get("basis")),
        "provenance_has_core_rule": bool(full_evidence.get("core_rule")),
    }

    if decision_timestamp is None:
        decision_timestamp = datetime.now(timezone.utc).isoformat()

    return {
        "decision": record.get("decision"),
        "patch_id": record.get("patch_id"),
        "timestamp": decision_timestamp,
        "status": patch_chain.get("status"),
        "patch_chain_decision": patch_chain.get("decision"),
        "patch_gate_decision": record.get("decision"),
        "patch_chain_status": patch_chain.get("status"),
        "artifact_paths": artifact_paths,
        "artifact_hashes": artifact_hashes,
        "dependency_patch_ids": dependency_patch_ids,
        "failure_codes": failure_codes,
        "summary_counts": summary_counts,
        "evidence_summary": evidence_summary,
        "full_evidence_hash": external_evidence_hash or _hash_json_value(full_evidence),
        "full_evidence_path": external_evidence_path,
    }


def normalize_repo_path(value):
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    path = Path(text)
    if path.is_absolute():
        try:
            path = path.relative_to(ROOT)
        except ValueError:
            return text.replace("\\", "/")

    return str(path).replace("\\", "/")


RUNTIME_ONLY_FRESHNESS_PATH_PREFIXES = (
    "registry/db/acellorator_index.sqlite",
    "outputs/",
    "validation/results/",
    "docs/reports/",
)


def is_runtime_only_freshness_path(path):
    normalized = normalize_repo_path(path)
    if not normalized:
        return False
    return any(normalized.startswith(prefix) for prefix in RUNTIME_ONLY_FRESHNESS_PATH_PREFIXES)


def parse_json_collection(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        if isinstance(parsed, (list, tuple)):
            return list(parsed)
        if parsed is None:
            return []
        return [parsed]
    return [value]


def load_governance_runtime_debt_items():
    registry = load_optional_json(RESEARCH_DEBT_REGISTRY)
    if not isinstance(registry, dict):
        return []

    items = []
    for item in registry.get("debt_items", []):
        if not isinstance(item, dict):
            continue
        if item.get("department") != "governance":
            continue
        if not str(item.get("introduced_by", "")).startswith("PATCH_DB_GOVERNANCE_RUNTIME"):
            continue
        items.append(item)
    return items


def normalize_debt_runtime_status(raw_status):
    status = str(raw_status or "").strip().lower()
    if status in {"resolved", "retired", "closed"}:
        return "resolved"
    if status in {"partially_resolved", "partial", "partially resolved"}:
        return "partial"
    if status in {"open", "acknowledged", "scheduled", "active", "under_review"}:
        return "open"
    if status in {"stale", "stale_snapshot"}:
        return "stale"
    return "unknown"


def normalize_debt_runtime_severity(raw_severity):
    severity = str(raw_severity or "").strip().lower()
    if severity in {"critical", "blocking"}:
        return "blocking"
    if severity == "high":
        return "high"
    if severity in {"moderate", "medium"}:
        return "medium"
    if severity in {"low", "informational", "info"}:
        return "low"
    return "unknown"


def normalize_debt_runtime_domain(item):
    title = str(item.get("title", "")).strip().lower()
    affects = [str(entry).strip().lower() for entry in parse_json_collection(item.get("affects")) if str(entry).strip()]
    if "provenance" in title:
        return "provenance"
    if "validation" in title:
        return "validation"
    if any(token in title for token in ("db", "runtime", "patch-chain", "current-state", "authority", "debt")):
        return "db_runtime"
    if "semantic" in title:
        return "semantic"
    if "documentation" in title or any("docs/" in entry or entry.endswith("readme.md") for entry in affects):
        return "docs"
    return "governance"


def debt_runtime_matches_target(record, target):
    normalized_target = normalize_repo_path(target)
    if not normalized_target:
        return False

    candidates = [
        record.get("owner_surface"),
        record.get("source_path"),
        record.get("resolution_patch"),
        record.get("introduced_by"),
    ]
    candidates.extend(parse_json_collection(record.get("affects")))
    candidates.extend(parse_json_collection(record.get("blocks")))
    for candidate in candidates:
        normalized_candidate = normalize_repo_path(candidate)
        if not normalized_candidate:
            continue
        if normalized_candidate == normalized_target or fnmatch(normalized_target, normalized_candidate) or fnmatch(normalized_candidate, normalized_target):
            return True
    return False


def normalize_debt_runtime_record(item, target=None):
    raw_status = item.get("status")
    raw_severity = item.get("severity")
    status = normalize_debt_runtime_status(raw_status)
    severity = normalize_debt_runtime_severity(raw_severity)
    domain = normalize_debt_runtime_domain(item)
    owner_surface = normalize_repo_path(item.get("owner_surface")) or str(RESEARCH_DEBT_REGISTRY.relative_to(ROOT)).replace("\\", "/")
    affects = [normalize_repo_path(entry) for entry in parse_json_collection(item.get("affects")) if normalize_repo_path(entry)]
    blocks = [str(entry).strip() for entry in parse_json_collection(item.get("blocks")) if str(entry).strip()]
    required_resolution = [str(entry).strip() for entry in parse_json_collection(item.get("required_resolution")) if str(entry).strip()]
    depends_on = [str(entry).strip() for entry in parse_json_collection(item.get("depends_on")) if str(entry).strip()]
    evidence_paths = [owner_surface, str(RESEARCH_DEBT_REGISTRY.relative_to(ROOT)).replace("\\", "/")]
    evidence_paths.extend(affects)
    resolution_patch = normalize_repo_path(item.get("resolution_patch"))
    if not resolution_patch:
        resolution_patch = normalize_repo_path(item.get("introduced_by")) if status == "resolved" else None

    if severity == "blocking":
        decision_effect = "block"
    elif status == "stale":
        decision_effect = "defer"
    elif status in {"open", "partial"}:
        decision_effect = "warn"
    elif status == "resolved":
        decision_effect = "allow"
    else:
        decision_effect = "warn"

    blocking_scope = "global" if severity == "blocking" else "target" if target and debt_runtime_matches_target(item, target) else "none"
    blocker_projection = {
        "debt_id": item.get("id"),
        "title": item.get("title"),
        "status": status,
        "severity": severity,
        "decision_effect": decision_effect,
        "blocking_scope": blocking_scope,
        "blocks": blocks,
        "required_resolution": required_resolution,
        "depends_on": depends_on,
    }
    residue_projection = {
        "debt_id": item.get("id"),
        "status": status,
        "severity": severity,
        "resolution_priority": item.get("resolution_priority"),
        "introduced_by": item.get("introduced_by"),
        "residue_class": "historical_residue" if status in {"open", "partial", "stale"} else "resolved",
        "provenance_state": "retained",
    }
    warnings = []
    if raw_status and status == "unknown":
        warnings.append(f"Debt status '{raw_status}' is not normalized.")
    if raw_severity and severity == "unknown":
        warnings.append(f"Debt severity '{raw_severity}' is not normalized.")
    if item.get("notes"):
        warnings.append(str(item.get("notes")))

    normalized = {
        "debt_id": item.get("id"),
        "title": item.get("title"),
        "status": status,
        "severity": severity,
        "domain": domain,
        "blocking_scope": blocking_scope,
        "owner_surface": owner_surface,
        "decision_effect": decision_effect,
        "resolution_patch": resolution_patch,
        "evidence_paths": [path for path in dict.fromkeys(path for path in evidence_paths if path)],
        "warnings": [warning for warning in dict.fromkeys(warnings) if warning],
        "source_path": str(RESEARCH_DEBT_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
        "introduced_by": item.get("introduced_by"),
        "affects": affects,
        "blocks": blocks,
        "depends_on": depends_on,
        "required_resolution": required_resolution,
        "blocker_projection": blocker_projection,
        "residue_projection": residue_projection,
        "raw_status": raw_status,
        "raw_severity": raw_severity,
    }
    if target:
        normalized["target_match"] = debt_runtime_matches_target(item, target)
    return normalized


def refresh_debt_runtime_projection(conn, target=None):
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS debt_runtime_projection (
                debt_id TEXT PRIMARY KEY,
                title TEXT,
                department TEXT,
                status TEXT,
                severity TEXT,
                domain TEXT,
                blocking_scope TEXT,
                owner_surface TEXT,
                resolution_patch TEXT,
                decision_effect TEXT,
                evidence_paths TEXT,
                warnings TEXT,
                source_path TEXT,
                introduced_by TEXT,
                affects TEXT,
                blocks TEXT,
                depends_on TEXT,
                required_resolution TEXT,
                blocker_projection TEXT,
                residue_projection TEXT,
                raw_status TEXT,
                raw_severity TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute("DELETE FROM debt_runtime_projection")
        for item in load_governance_runtime_debt_items():
            normalized = normalize_debt_runtime_record(item, target=target)
            conn.execute(
                """
                INSERT INTO debt_runtime_projection (
                    debt_id,
                    title,
                    department,
                    status,
                    severity,
                    domain,
                    blocking_scope,
                    owner_surface,
                    resolution_patch,
                    decision_effect,
                    evidence_paths,
                    warnings,
                    source_path,
                    introduced_by,
                    affects,
                    blocks,
                    depends_on,
                    required_resolution,
                    blocker_projection,
                    residue_projection,
                    raw_status,
                    raw_severity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized.get("debt_id"),
                    normalized.get("title"),
                    "governance",
                    normalized.get("status"),
                    normalized.get("severity"),
                    normalized.get("domain"),
                    normalized.get("blocking_scope"),
                    normalized.get("owner_surface"),
                    normalized.get("resolution_patch"),
                    normalized.get("decision_effect"),
                    json.dumps(normalized.get("evidence_paths", []), ensure_ascii=False),
                    json.dumps(normalized.get("warnings", []), ensure_ascii=False),
                    normalized.get("source_path"),
                    normalized.get("introduced_by"),
                    json.dumps(normalized.get("affects", []), ensure_ascii=False),
                    json.dumps(normalized.get("blocks", []), ensure_ascii=False),
                    json.dumps(normalized.get("depends_on", []), ensure_ascii=False),
                    json.dumps(normalized.get("required_resolution", []), ensure_ascii=False),
                    json.dumps(normalized.get("blocker_projection", {}), ensure_ascii=False),
                    json.dumps(normalized.get("residue_projection", {}), ensure_ascii=False),
                    normalized.get("raw_status"),
                    normalized.get("raw_severity"),
                ),
            )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()


def load_debt_runtime_catalog(conn):
    try:
        rows = conn.execute(
            """
            SELECT
                debt_id,
                title,
                department,
                status,
                severity,
                domain,
                blocking_scope,
                owner_surface,
                resolution_patch,
                decision_effect,
                evidence_paths,
                warnings,
                source_path,
                introduced_by,
                affects,
                blocks,
                depends_on,
                required_resolution,
                blocker_projection,
                residue_projection,
                raw_status,
                raw_severity,
                updated_at,
                coverage_state
            FROM debt_runtime_view
            ORDER BY CASE status
                WHEN 'blocking' THEN 0
                WHEN 'open' THEN 1
                WHEN 'partial' THEN 2
                WHEN 'stale' THEN 3
                WHEN 'resolved' THEN 4
                ELSE 5
            END,
            debt_id
            """
        ).fetchall()
    except sqlite3.Error:
        rows = []

    if rows:
        normalized_rows = []
        for row in rows:
            record = dict(row)
            for field in ("evidence_paths", "warnings", "affects", "blocks", "depends_on", "required_resolution"):
                record[field] = parse_json_collection(record.get(field))
            for field in ("blocker_projection", "residue_projection"):
                raw_value = record.get(field)
                if isinstance(raw_value, dict):
                    continue
                if isinstance(raw_value, str) and raw_value.strip():
                    try:
                        record[field] = json.loads(raw_value)
                    except json.JSONDecodeError:
                        record[field] = {}
                else:
                    record[field] = {}
            normalized_rows.append(record)
        return normalized_rows

    return [
        normalize_debt_runtime_record(item)
        for item in load_governance_runtime_debt_items()
    ]


def filter_debt_runtime_records(records, status_filter="all", target=None):
    normalized_filter = str(status_filter or "all").strip().lower()
    normalized_target = normalize_repo_path(target) if target else None

    filtered = []
    for record in records:
        if normalized_target and not debt_runtime_matches_target(record, normalized_target):
            continue
        if normalized_filter == "all":
            filtered.append(record)
            continue
        if normalized_filter == "blocking" and record.get("decision_effect") == "block":
            filtered.append(record)
            continue
        if normalized_filter in {"open", "partial", "resolved"} and record.get("status") == normalized_filter:
            filtered.append(record)
            continue
    return filtered


def build_debt_runtime_result(db_path, target=None, status_filter="all", current_state=None):
    db_file = Path(db_path)
    result = {
        "mode": "debt_runtime",
        "db_path": str(db_file),
        "target": normalize_repo_path(target),
        "status_filter": str(status_filter or "all").strip().lower() or "all",
        "debts": [],
        "summary": {
            "open": 0,
            "partial": 0,
            "resolved": 0,
            "blocking": 0,
            "warnings": 0,
        },
        "decision": "defer",
        "reason": "Debt runtime is unavailable.",
        "warnings": [],
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(RESEARCH_DEBT_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            str(DEBT_RUNTIME_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
    }

    if not db_file.exists():
        result["reason"] = "Governance DB file is missing."
        result["warnings"].append("The governance runtime database is unavailable.")
        return result

    if current_state and current_state.get("warnings"):
        result["warnings"].extend(current_state["warnings"])

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        ensure_runtime_schema(conn)
        refresh_debt_runtime_projection(conn, target=target)
        catalog = load_debt_runtime_catalog(conn)
    finally:
        conn.close()

    filtered = filter_debt_runtime_records(catalog, status_filter=status_filter, target=target)
    if current_state and current_state.get("status") == "warn":
        result["warnings"].append("Current-state capsule reports warnings.")

    for record in filtered:
        status = record.get("status", "unknown")
        if status == "open":
            result["summary"]["open"] += 1
        elif status == "partial":
            result["summary"]["partial"] += 1
        elif status == "resolved":
            result["summary"]["resolved"] += 1
        if record.get("decision_effect") == "block":
            result["summary"]["blocking"] += 1
        result["warnings"].extend(record.get("warnings", []))

    result["debts"] = filtered
    debt_projection = build_debt_blocker_projection(filtered, current_state=current_state)
    residue_projection = build_historical_residue_projection(current_state=current_state, debt_records=filtered)
    result["blocker_projection"] = debt_projection
    result["historical_residue_projection"] = residue_projection
    result["projection"] = {
        "blocker_projection": debt_projection,
        "historical_residue_projection": residue_projection,
    }
    result["summary"]["projected_blockers"] = debt_projection.get("blocking_debt_count", 0)
    result["summary"]["projected_open_debts"] = debt_projection.get("open_debt_count", 0)
    result["summary"]["warnings"] = len([warning for warning in dict.fromkeys(result["warnings"]) if warning])

    if any(record.get("decision_effect") == "block" for record in filtered):
        result["decision"] = "block"
        result["reason"] = "Blocking debt item(s) remain open."
    elif any(record.get("decision_effect") == "defer" for record in filtered):
        result["decision"] = "defer"
        result["reason"] = "Debt runtime advises deferral pending resolution."
    elif filtered:
        result["decision"] = "allow"
        result["reason"] = "Debt runtime records are advisory only."
    else:
        result["decision"] = "allow"
        result["reason"] = "No debt items match the requested filter."

    evidence_paths = list(result["evidence_paths"])
    for record in filtered:
        evidence_paths.extend(record.get("evidence_paths", []))
    result["evidence_paths"] = [path for path in dict.fromkeys(path for path in evidence_paths if path)]
    result["warnings"] = [warning for warning in dict.fromkeys(result["warnings"]) if warning]
    return result


def _parse_governance_event_payload(raw_payload):
    if raw_payload is None:
        return {}, True
    if isinstance(raw_payload, (dict, list, tuple, int, float, bool)):
        return raw_payload, True

    text = str(raw_payload).strip()
    if not text:
        return {}, True

    candidates = []

    def add_candidate(candidate):
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    add_candidate(text)

    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        add_candidate(text[1:-1].strip())

    for seed in list(candidates):
        add_candidate(seed.replace('\\"', '"').replace('`"', '"'))
        add_candidate(seed.replace("\\'", "'"))
        add_candidate(seed.replace("\\\\", "\\"))

    for seed in list(candidates):
        if len(seed) >= 2 and seed[0] == seed[-1] and seed[0] in {"'", '"'}:
            add_candidate(seed[1:-1].strip())

    for candidate in candidates:
        try:
            return json.loads(candidate), True
        except json.JSONDecodeError:
            continue

    # Coerce very simple shell-stripped object literals like `{status:registered}`
    # into valid JSON so PowerShell-escaped acceptance commands remain usable.
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        if not inner:
            return {}, True

        pairs = []
        simple_pairs = [segment.strip() for segment in inner.split(",") if segment.strip()]
        if simple_pairs and all(":" in segment for segment in simple_pairs):
            for segment in simple_pairs:
                key_text, value_text = segment.split(":", 1)
                key_text = key_text.strip().strip("'\"")
                value_text = value_text.strip()
                if not key_text:
                    continue
                if value_text.startswith("{") or value_text.startswith("["):
                    coerced_value = value_text
                elif value_text.lower() in {"true", "false", "null"}:
                    coerced_value = value_text.lower()
                elif re.fullmatch(r"-?\d+(?:\.\d+)?", value_text):
                    coerced_value = value_text
                else:
                    coerced_value = json.dumps(value_text.strip("'\""))
                pairs.append(f"{json.dumps(key_text)}:{coerced_value}")

            if pairs:
                candidate = "{" + ",".join(pairs) + "}"
                try:
                    return json.loads(candidate), True
                except json.JSONDecodeError:
                    pass

    return None, False


def _normalize_governance_event_payload(payload):
    parsed, _ = _parse_governance_event_payload(payload)
    if parsed is None:
        return {"value": payload}
    return parsed


def _normalize_governance_event_evidence_paths(paths):
    normalized = []
    for path in parse_json_collection(paths):
        normalized_path = normalize_repo_path(path)
        if normalized_path:
            normalized.append(normalized_path)
    return [path for path in dict.fromkeys(normalized) if path]


def append_governance_event(conn, record):
    event_id = str(record.get("event_id") or f"EVT-{uuid.uuid4().hex[:12].upper()}").strip()
    event_type = str(record.get("event_type") or "unknown").strip() or "unknown"
    subject_id = str(record.get("subject_id") or "unknown").strip() or "unknown"
    subject_type = str(record.get("subject_type") or "unknown").strip() or "unknown"
    source_patch_id = str(record.get("source_patch_id") or "").strip() or None
    source_path = normalize_repo_path(record.get("source_path"))
    payload = _normalize_governance_event_payload(record.get("payload"))
    evidence_paths = _normalize_governance_event_evidence_paths(record.get("evidence_paths"))

    conn.execute(
        """
        INSERT INTO governance_events (
            event_id,
            event_type,
            subject_id,
            subject_type,
            source_patch_id,
            source_path,
            payload_json,
            evidence_paths_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            event_type,
            subject_id,
            subject_type,
            source_patch_id,
            source_path,
            json.dumps(payload, ensure_ascii=False),
            json.dumps(evidence_paths, ensure_ascii=False),
        ),
    )

    row = conn.execute(
        """
        SELECT
            event_id,
            event_type,
            subject_id,
            subject_type,
            source_patch_id,
            source_path,
            payload_json,
            evidence_paths_json,
            created_at
        FROM governance_events
        WHERE event_id = ?
        """,
        (event_id,),
    ).fetchone()
    if row is None:
        return None

    payload_value = {}
    evidence_value = []
    try:
        payload_value = json.loads(row["payload_json"]) if row["payload_json"] else {}
    except json.JSONDecodeError:
        payload_value = {"raw_payload": row["payload_json"]}
    if not isinstance(payload_value, dict):
        payload_value = {"value": payload_value}
    try:
        evidence_value = json.loads(row["evidence_paths_json"]) if row["evidence_paths_json"] else []
    except json.JSONDecodeError:
        evidence_value = [row["evidence_paths_json"]]

    return {
        "event_id": row["event_id"],
        "event_type": row["event_type"],
        "subject_id": row["subject_id"],
        "subject_type": row["subject_type"],
        "source_patch_id": row["source_patch_id"],
        "source_path": row["source_path"],
        "payload": payload_value,
        "created_at": row["created_at"],
        "evidence_paths": [path for path in dict.fromkeys(path for path in evidence_value if path)],
    }


def load_governance_event_records(db_path, event_type=None, subject_id=None, source_patch_id=None, limit=20):
    db_file = Path(db_path)
    result = {
        "mode": "governance_events",
        "db_path": str(db_file),
        "filters": {
            "event_type": event_type,
            "subject_id": subject_id,
            "source_patch_id": source_patch_id,
            "limit": limit,
        },
        "events": [],
        "summary": {
            "total": 0,
            "by_event_type": {},
        },
        "status": "success",
        "warnings": [],
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_BUS_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
    }

    if not db_file.exists():
        result["status"] = "unavailable"
        result["warnings"].append("The governance runtime database is unavailable.")
        return result

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        ensure_runtime_schema(conn)
        query = """
            SELECT
                event_id,
                event_type,
                subject_id,
                subject_type,
                source_patch_id,
                source_path,
                payload_json,
                evidence_paths_json,
                created_at
            FROM governance_events
            WHERE 1=1
        """
        params = []
        if event_type:
            query += " AND event_type = ?"
            params.append(str(event_type).strip())
        if subject_id:
            query += " AND subject_id = ?"
            params.append(str(subject_id).strip())
        if source_patch_id:
            query += " AND source_patch_id = ?"
            params.append(str(source_patch_id).strip())
        query += " ORDER BY COALESCE(created_at, '') DESC, event_id DESC LIMIT ?"
        params.append(max(1, int(limit or 20)))
        rows = conn.execute(query, params).fetchall()
    except sqlite3.Error as exc:
        result["status"] = "unavailable"
        result["warnings"].append(str(exc))
        return result
    finally:
        conn.close()

    events = []
    by_event_type = {}
    for row in rows:
        try:
            payload = json.loads(row["payload_json"]) if row["payload_json"] else {}
        except json.JSONDecodeError:
            payload = {"raw_payload": row["payload_json"]}
        if not isinstance(payload, dict):
            payload = {"value": payload}
        try:
            evidence_paths = json.loads(row["evidence_paths_json"]) if row["evidence_paths_json"] else []
        except json.JSONDecodeError:
            evidence_paths = [row["evidence_paths_json"]]
        event = {
            "event_id": row["event_id"],
            "event_type": row["event_type"],
            "subject_id": row["subject_id"],
            "subject_type": row["subject_type"],
            "source_patch_id": row["source_patch_id"],
            "source_path": row["source_path"],
            "payload": payload,
            "created_at": row["created_at"],
            "evidence_paths": [path for path in dict.fromkeys(path for path in evidence_paths if path)],
        }
        events.append(event)
        by_event_type[event["event_type"]] = by_event_type.get(event["event_type"], 0) + 1

    result["events"] = events
    result["summary"]["total"] = len(events)
    result["summary"]["by_event_type"] = by_event_type
    if events:
        result["evidence_paths"] = [path for path in dict.fromkeys(
            result["evidence_paths"] + [path for event in events for path in event.get("evidence_paths", [])]
        ) if path]
    return result


def load_recent_governance_events(db_path, limit=3):
    records = load_governance_event_records(db_path, limit=limit)
    if not isinstance(records, dict):
        return []
    events = []
    for event in records.get("events", []):
        events.append(
            {
                "event_id": event.get("event_id"),
                "event_type": event.get("event_type"),
                "subject_id": event.get("subject_id"),
                "source_patch_id": event.get("source_patch_id"),
            }
        )
    return events


SAFE_REPLAY_EVENT_TYPES = {
    "patch_registered",
    "patch_applied",
    "patch_blocked",
    "patch_deferred",
    "governance_decision",
    "validator_completed",
    "debt_created",
    "debt_updated",
    "debt_resolved",
    "db_snapshot_stale",
    "db_snapshot_refreshed",
}


def _governance_event_replay_sort_key(event):
    created_at = parse_timestamp(event.get("created_at"))
    if created_at is None:
        created_at = datetime.min.replace(tzinfo=timezone.utc)
    return (created_at, str(event.get("event_id") or ""))


def _initial_governance_replay_state(subject_id=None, event_type=None):
    return {
        "scope": {
            "subject_id": subject_id,
            "event_type": event_type,
        },
        "status": "empty",
        "current_status": "unknown",
        "latest_event": None,
        "latest_subject_type": None,
        "patches": {},
        "debts": {},
        "authority": {},
        "decisions": [],
        "validators": [],
        "snapshot": {
            "status": "unknown",
            "event_id": None,
            "event_type": None,
        },
        "event_counts": {
            "applied": 0,
            "ignored": 0,
            "by_event_type": {},
            "by_subject_type": {},
        },
        "warnings": [],
    }


def _apply_governance_replay_event(state, event):
    event_type = str(event.get("event_type") or "unknown").strip() or "unknown"
    subject_id = str(event.get("subject_id") or "unknown").strip() or "unknown"
    subject_type = str(event.get("subject_type") or "unknown").strip() or "unknown"
    payload = event.get("payload") or {}
    evidence_paths = [path for path in event.get("evidence_paths", []) if path]

    state["event_counts"]["applied"] += 1
    state["event_counts"]["by_event_type"][event_type] = state["event_counts"]["by_event_type"].get(event_type, 0) + 1
    state["event_counts"]["by_subject_type"][subject_type] = state["event_counts"]["by_subject_type"].get(subject_type, 0) + 1
    state["latest_event"] = {
        "event_id": event.get("event_id"),
        "event_type": event_type,
        "subject_id": subject_id,
        "subject_type": subject_type,
        "source_patch_id": event.get("source_patch_id"),
        "source_path": event.get("source_path"),
        "created_at": event.get("created_at"),
        "payload": payload,
        "evidence_paths": evidence_paths,
    }
    state["latest_subject_type"] = subject_type

    if event_type == "patch_registered":
        patch_state = state["patches"].setdefault(
            subject_id,
            {
                "patch_id": subject_id,
                "status": "registered",
                "source_patch_id": event.get("source_patch_id"),
                "source_path": event.get("source_path"),
                "last_event_id": None,
                "last_event_type": None,
            },
        )
        patch_state["status"] = str(payload.get("status") or "registered").strip() or "registered"
        patch_state["source_patch_id"] = event.get("source_patch_id")
        patch_state["source_path"] = event.get("source_path")
        patch_state["last_event_id"] = event.get("event_id")
        patch_state["last_event_type"] = event_type
        patch_state["evidence_paths"] = evidence_paths
        state["current_status"] = patch_state["status"]
        state["status"] = patch_state["status"]
        return

    if event_type in {"patch_applied", "patch_blocked", "patch_deferred"}:
        patch_state = state["patches"].setdefault(
            subject_id,
            {
                "patch_id": subject_id,
                "status": "unknown",
                "source_patch_id": event.get("source_patch_id"),
                "source_path": event.get("source_path"),
                "last_event_id": None,
                "last_event_type": None,
            },
        )
        derived_status = {
            "patch_applied": "applied",
            "patch_blocked": "blocked",
            "patch_deferred": "deferred",
        }[event_type]
        patch_state["status"] = str(payload.get("status") or derived_status).strip() or derived_status
        patch_state["source_patch_id"] = event.get("source_patch_id")
        patch_state["source_path"] = event.get("source_path")
        patch_state["last_event_id"] = event.get("event_id")
        patch_state["last_event_type"] = event_type
        patch_state["evidence_paths"] = evidence_paths
        state["current_status"] = patch_state["status"]
        state["status"] = patch_state["status"]
        return

    if event_type == "governance_decision":
        decision_record = {
            "event_id": event.get("event_id"),
            "subject_id": subject_id,
            "source_patch_id": event.get("source_patch_id"),
            "decision": payload.get("decision"),
            "reason": payload.get("reason"),
            "created_at": event.get("created_at"),
            "evidence_paths": evidence_paths,
        }
        state["decisions"].append(decision_record)
        if payload.get("decision"):
            state["current_status"] = str(payload.get("decision")).strip() or state["current_status"]
            state["status"] = str(payload.get("decision")).strip() or state["status"]
        return

    if event_type == "validator_completed":
        validator_record = {
            "event_id": event.get("event_id"),
            "subject_id": subject_id,
            "validator": payload.get("validator") or payload.get("validator_id"),
            "result": payload.get("result") or payload.get("status"),
            "created_at": event.get("created_at"),
            "evidence_paths": evidence_paths,
        }
        state["validators"].append(validator_record)
        if payload.get("result") or payload.get("status"):
            state["current_status"] = str(payload.get("result") or payload.get("status")).strip() or state["current_status"]
        return

    if event_type in {"debt_created", "debt_updated", "debt_resolved"}:
        debt_state = state["debts"].setdefault(
            subject_id,
            {
                "debt_id": subject_id,
                "status": "open",
                "severity": payload.get("severity"),
                "domain": payload.get("domain"),
                "blocking_scope": payload.get("blocking_scope"),
                "owner_surface": payload.get("owner_surface"),
                "decision_effect": payload.get("decision_effect"),
                "source_patch_id": event.get("source_patch_id"),
                "source_path": event.get("source_path"),
                "last_event_id": None,
                "last_event_type": None,
            },
        )
        if event_type == "debt_resolved":
            debt_state["status"] = "resolved"
            debt_state["decision_effect"] = payload.get("decision_effect") or "allow"
        else:
            debt_state["status"] = str(payload.get("status") or debt_state.get("status") or "open").strip() or "open"
            if payload.get("decision_effect"):
                debt_state["decision_effect"] = payload.get("decision_effect")
        for field in ("severity", "domain", "blocking_scope", "owner_surface", "resolution_patch", "decision_effect"):
            if payload.get(field) is not None:
                debt_state[field] = payload.get(field)
        debt_state["source_patch_id"] = event.get("source_patch_id")
        debt_state["source_path"] = event.get("source_path")
        debt_state["last_event_id"] = event.get("event_id")
        debt_state["last_event_type"] = event_type
        debt_state["evidence_paths"] = evidence_paths
        state["current_status"] = debt_state["status"]
        state["status"] = debt_state["status"]
        return

    if event_type in {"db_snapshot_stale", "db_snapshot_refreshed"}:
        snapshot_status = "stale" if event_type == "db_snapshot_stale" else "current"
        state["snapshot"] = {
            "status": snapshot_status,
            "event_id": event.get("event_id"),
            "event_type": event_type,
            "source_patch_id": event.get("source_patch_id"),
            "source_path": event.get("source_path"),
        }
        state["current_status"] = snapshot_status
        state["status"] = snapshot_status
        return

    state["current_status"] = event_type
    state["status"] = event_type


def replay_governance_events(records):
    result = {
        "subject_id": None,
        "reconstructed_state": _initial_governance_replay_state(),
        "applied_events": [],
        "ignored_events": [],
        "warnings": [],
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_BUS_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_REPLAY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
        "authority_note": "Registry remains authority; replay is diagnostic unless reconciled.",
    }

    if not isinstance(records, dict):
        result["warnings"].append("Replay records are unavailable.")
        return result

    if records.get("status") != "success":
        result["warnings"].extend(records.get("warnings", []))
        result["reconstructed_state"]["status"] = "unavailable"
        result["reconstructed_state"]["warnings"].extend(records.get("warnings", []))
        return result

    subject_id = records.get("filters", {}).get("subject_id")
    requested_event_type = records.get("filters", {}).get("event_type")
    result["subject_id"] = subject_id
    result["reconstructed_state"] = _initial_governance_replay_state(subject_id=subject_id, event_type=requested_event_type)

    requested_event_type_text = str(requested_event_type or "").strip()
    if requested_event_type_text and requested_event_type_text not in SAFE_REPLAY_EVENT_TYPES:
        warning = f"Event type '{requested_event_type_text}' is not in the safe replay set."
        result["warnings"].append(warning)
        result["reconstructed_state"]["warnings"].append(warning)

    events = list(records.get("events", []))
    events.sort(key=_governance_event_replay_sort_key)

    for event in events:
        event_type = str(event.get("event_type") or "unknown").strip() or "unknown"
        event_summary = {
            "event_id": event.get("event_id"),
            "event_type": event_type,
            "subject_id": event.get("subject_id"),
            "subject_type": event.get("subject_type"),
            "source_patch_id": event.get("source_patch_id"),
            "source_path": event.get("source_path"),
            "created_at": event.get("created_at"),
            "payload": event.get("payload") or {},
            "evidence_paths": event.get("evidence_paths", []),
        }
        if event_type not in SAFE_REPLAY_EVENT_TYPES:
            result["ignored_events"].append(
                {
                    "event_id": event.get("event_id"),
                    "event_type": event_type,
                    "subject_id": event.get("subject_id"),
                    "reason": "Event type is not in the safe replay set.",
                }
            )
            result["reconstructed_state"]["event_counts"]["ignored"] += 1
            continue

        result["applied_events"].append(event_summary)
        _apply_governance_replay_event(result["reconstructed_state"], event)

    if result["applied_events"]:
        latest_event = result["applied_events"][-1]
        result["reconstructed_state"]["latest_event"] = latest_event
        if result["reconstructed_state"].get("status") == "empty":
            result["reconstructed_state"]["status"] = "replayed"
    else:
        result["reconstructed_state"]["status"] = "empty"

    result["reconstructed_state"]["scope"] = {
        "subject_id": subject_id,
        "event_type": requested_event_type,
        "limit": records.get("filters", {}).get("limit"),
    }
    result["reconstructed_state"]["replay_summary"] = {
        "applied": len(result["applied_events"]),
        "ignored": len(result["ignored_events"]),
        "event_types": result["reconstructed_state"]["event_counts"]["by_event_type"],
    }

    evidence_paths = list(result["evidence_paths"])
    for event in result["applied_events"]:
        evidence_paths.extend(event.get("evidence_paths", []))
    result["evidence_paths"] = [path for path in dict.fromkeys(path for path in evidence_paths if path)]
    return result


def find_patch_candidates_for_target(target):
    normalized_target = normalize_repo_path(target)
    if not normalized_target or not PATCH_REGISTRY_DIR.exists():
        return []

    if normalized_target.startswith("registry/governance/patches/") and normalized_target.endswith(".json"):
        patch, patch_path = load_patch_record_by_path(ROOT / normalized_target)
        if isinstance(patch, dict):
            return [(patch, patch_path)]

    candidates = []
    for patch_path in sorted(PATCH_REGISTRY_DIR.glob("*.json")):
        patch, loaded_path = load_patch_record_by_path(patch_path)
        if not isinstance(patch, dict):
            continue
        patch_paths = collect_patch_target_paths(patch)
        if any(
            normalized_target == path
            or fnmatch(normalized_target, path)
            or fnmatch(path, normalized_target)
            for path in patch_paths
            if path
        ):
            candidates.append((patch, loaded_path))

    candidates.sort(
        key=lambda item: (
            str(item[0].get("applied_on") or ""),
            str(item[0].get("patch_id") or ""),
        ),
        reverse=True,
    )
    return candidates


def find_latest_applied_patch_candidate():
    if not PATCH_REGISTRY_DIR.exists():
        return None, None

    candidates = []
    for patch_path in sorted(PATCH_REGISTRY_DIR.glob("*.json")):
        patch, loaded_path = load_patch_record_by_path(patch_path)
        if not isinstance(patch, dict):
            continue
        status = str(patch.get("status", "")).strip().upper()
        if status != "APPLIED":
            continue
        patch_id = str(patch.get("patch_id", "")).strip()
        if not patch_id.startswith("PATCH_DB_GOVERNANCE_RUNTIME_"):
            continue
        candidates.append((patch, loaded_path))

    candidates.sort(
        key=lambda item: (
            str(item[0].get("applied_on") or ""),
            str(item[0].get("patch_id") or ""),
        ),
        reverse=True,
    )
    return candidates[0] if candidates else (None, None)


def _dedupe_trim(items, limit=None):
    values = [item for item in items if item not in (None, "", [], {}, ())]
    values = [item for item in dict.fromkeys(values)]
    if limit is not None:
        return values[:limit]
    return values


def _normalize_light_summary_verdict(verdict):
    normalized = str(verdict or "").strip().lower()
    if normalized in {"apply", "allow", "defer", "block"}:
        return normalized
    if normalized == "applied":
        return "apply"
    if normalized == "allowed":
        return "allow"
    if normalized == "deferred":
        return "defer"
    if normalized == "blocked":
        return "block"
    return "unknown"


def _normalize_light_summary_status(raw_status, verdict=None):
    normalized = str(raw_status or "").strip().lower()
    if normalized == "applied":
        return "applied"
    if normalized == "active":
        return "active"
    if normalized in {"blocked", "late_registered", "superseded", "missing"}:
        return "blocked"
    if normalized == "error":
        return "error"

    verdict_normalized = _normalize_light_summary_verdict(verdict)
    if verdict_normalized in {"apply", "allow"}:
        return "active"
    if verdict_normalized == "block":
        return "blocked"
    return "unknown"


def build_patch_chain_light_summary(chain_result, serialization_warning=None):
    if not isinstance(chain_result, dict):
        chain_result = {}

    result = {
        "patch_id": chain_result.get("patch_id"),
        "query": "patch_chain",
        "status": _normalize_light_summary_status(chain_result.get("status"), chain_result.get("decision")),
        "verdict": _normalize_light_summary_verdict(chain_result.get("decision")),
        "reason": chain_result.get("reason") or "Patch chain resolution is unavailable.",
        "blockers": _dedupe_trim(chain_result.get("blockers", []), limit=3),
        "runtime_path": "light_summary",
        "full_report_available": True,
    }
    if serialization_warning:
        result["serialization_warning"] = serialization_warning
    return result


def build_patch_gate_light_summary(gate_result, serialization_warning=None):
    if not isinstance(gate_result, dict):
        gate_result = {}

    patch_chain = gate_result.get("patch_chain", {})
    if not isinstance(patch_chain, dict):
        patch_chain = {}

    result = {
        "patch_id": gate_result.get("patch_id"),
        "query": "patch_gate",
        "status": _normalize_light_summary_status(patch_chain.get("status"), gate_result.get("decision")),
        "verdict": _normalize_light_summary_verdict(gate_result.get("decision")),
        "reason": gate_result.get("reason") or patch_chain.get("reason") or "Patch gate resolution is unavailable.",
        "blockers": _dedupe_trim(
            list(gate_result.get("blocking_conditions", [])) + list(patch_chain.get("blockers", [])),
            limit=3,
        ),
        "runtime_path": "light_summary",
        "full_report_available": True,
    }
    if serialization_warning:
        result["serialization_warning"] = serialization_warning
    return result


EVIDENCE_LEVEL_NAMES = {
    0: "summary",
    1: "diagnostic",
    2: "governance",
    3: "forensic",
}

EVIDENCE_LEVEL_ALIASES = {
    "summary": 0,
    "level_0": 0,
    "0": 0,
    "diagnostic": 1,
    "level_1": 1,
    "1": 1,
    "governance": 2,
    "level_2": 2,
    "2": 2,
    "forensic": 3,
    "level_3": 3,
    "3": 3,
}


def _normalize_evidence_level(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value if value in EVIDENCE_LEVEL_NAMES else None

    text = str(value).strip().lower()
    if not text:
        return None
    if text.isdigit():
        numeric = int(text)
        return numeric if numeric in EVIDENCE_LEVEL_NAMES else None
    return EVIDENCE_LEVEL_ALIASES.get(text)


def _evidence_level_name(level):
    return EVIDENCE_LEVEL_NAMES.get(level, "unknown")


def _resolve_requested_evidence_level(args):
    explicit_level = _normalize_evidence_level(getattr(args, "level", None))
    if explicit_level is not None:
        return explicit_level
    if getattr(args, "summary", False):
        return 0
    return None


def _attach_evidence_level_metadata(payload, requested_level, emitted_level, fallback_from=None, serialization_warning=None):
    if not isinstance(payload, dict):
        return payload

    result = dict(payload)
    if requested_level is not None:
        result["requested_evidence_level"] = _evidence_level_name(requested_level)
    if emitted_level is not None:
        result["evidence_level"] = _evidence_level_name(emitted_level)
    if fallback_from is not None and fallback_from != emitted_level:
        result["evidence_level_fallback_from"] = _evidence_level_name(fallback_from)
    if serialization_warning:
        result["serialization_warning"] = serialization_warning
    return result


def _trim_nested_lists(payload, limit=5):
    if not isinstance(payload, dict):
        return payload

    result = dict(payload)
    for key, value in list(result.items()):
        if isinstance(value, list):
            result[key] = value[:limit]
            continue
        if isinstance(value, dict):
            nested = dict(value)
            for nested_key, nested_value in list(nested.items()):
                if isinstance(nested_value, list):
                    nested[nested_key] = nested_value[:limit]
            result[key] = nested
    return result


def _summarize_target_decisions(target_decisions, limit=3):
    summary = []
    for record in parse_json_collection(target_decisions)[:limit]:
        if not isinstance(record, dict):
            continue
        summary.append(
            {
                "target": record.get("target") or record.get("semantic_key"),
                "decision": record.get("decision"),
                "reason": record.get("reason"),
                "status": record.get("status"),
                "conflict_state": record.get("conflict_state"),
            }
        )
    return summary


def _summarize_dependency_results(dependency_results, limit=5):
    summary = []
    for record in parse_json_collection(dependency_results)[:limit]:
        if not isinstance(record, dict):
            continue
        summary.append(
            {
                "patch_id": record.get("patch_id"),
                "status": record.get("status"),
                "decision": record.get("decision"),
                "reason": record.get("reason"),
            }
        )
    return summary


def _summarize_current_state_capsule(capsule):
    if not isinstance(capsule, dict):
        return capsule
    runtime = capsule.get("runtime", {}) if isinstance(capsule.get("runtime"), dict) else {}
    health = capsule.get("health", {}) if isinstance(capsule.get("health"), dict) else {}
    return {
        "status": capsule.get("status"),
        "health": {
            "global_validation": health.get("global_validation"),
        },
        "runtime": {
            "db_first_gate": runtime.get("db_first_gate"),
            "authority_boundary": runtime.get("authority_boundary"),
        },
        "blocker_count": len(parse_json_collection(capsule.get("blockers", []))),
        "open_debt_count": len(parse_json_collection(capsule.get("open_debt", []))),
        "latest_decision_count": len(parse_json_collection(capsule.get("latest_decisions", []))),
        "warning_count": len(parse_json_collection(capsule.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(capsule.get("warnings", [])), limit=3),
        "evidence_paths": _dedupe_trim(parse_json_collection(capsule.get("evidence_paths", [])), limit=5),
    }


def _summarize_authority_result(result):
    if not isinstance(result, dict):
        return result
    summary = {
        "target": result.get("target"),
        "authority_owner": result.get("authority_owner"),
        "decision": result.get("decision"),
        "reason": result.get("reason"),
        "conflict_state": result.get("conflict_state"),
        "warning_count": len(parse_json_collection(result.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(result.get("warnings", [])), limit=3),
        "evidence_paths": _dedupe_trim(parse_json_collection(result.get("evidence_paths", [])), limit=5),
    }
    if "semantic_key" in result or result.get("mode") == "semantic_authority_resolution":
        summary.update(
            {
                "semantic_key": result.get("semantic_key"),
                "semantic_type": result.get("semantic_type"),
                "authority_rank": result.get("authority_rank"),
                "supersession": result.get("supersession", {}),
            }
        )
        if result.get("target_authority"):
            summary["target_authority"] = _summarize_authority_result(result.get("target_authority"))
    else:
        summary.update(
            {
                "authority_source": result.get("authority_source"),
                "supersession": result.get("supersession", {}),
            }
        )
    return summary


def _summarize_freshness_result(result):
    if not isinstance(result, dict):
        return result
    return {
        "db_snapshot_status": result.get("db_snapshot_status"),
        "decision": result.get("decision"),
        "reason": result.get("reason"),
        "change_basis": result.get("change_basis"),
        "staleness_cause": result.get("staleness_cause"),
        "source_change_count": result.get("source_change_count", 0),
        "runtime_only_change_count": result.get("runtime_only_change_count", 0),
        "latest_known_worktree_change": result.get("latest_known_worktree_change"),
        "latest_runtime_only_worktree_change": result.get("latest_runtime_only_worktree_change"),
        "warning_count": len(parse_json_collection(result.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(result.get("warnings", [])), limit=3),
    }


def _summarize_debt_result(result):
    if not isinstance(result, dict):
        return result
    debts = []
    for record in parse_json_collection(result.get("debts", []))[:5]:
        if not isinstance(record, dict):
            continue
        debts.append(
            {
                "debt_id": record.get("debt_id"),
                "status": record.get("status"),
                "severity": record.get("severity"),
                "decision_effect": record.get("decision_effect"),
            }
        )
    return {
        "mode": result.get("mode"),
        "target": result.get("target"),
        "status_filter": result.get("status_filter"),
        "decision": result.get("decision"),
        "reason": result.get("reason"),
        "summary": result.get("summary", {}),
        "debts": debts,
        "warning_count": len(parse_json_collection(result.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(result.get("warnings", [])), limit=3),
        "evidence_paths": _dedupe_trim(parse_json_collection(result.get("evidence_paths", [])), limit=5),
    }


def _summarize_events_result(result):
    if not isinstance(result, dict):
        return result
    events = []
    for event in parse_json_collection(result.get("events", []))[:5]:
        if not isinstance(event, dict):
            continue
        events.append(
            {
                "event_id": event.get("event_id"),
                "event_type": event.get("event_type"),
                "subject_id": event.get("subject_id"),
                "source_patch_id": event.get("source_patch_id"),
            }
        )
    return {
        "mode": result.get("mode"),
        "status": result.get("status"),
        "filters": result.get("filters", {}),
        "summary": result.get("summary", {}),
        "events": events,
        "warning_count": len(parse_json_collection(result.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(result.get("warnings", [])), limit=3),
        "evidence_paths": _dedupe_trim(parse_json_collection(result.get("evidence_paths", [])), limit=5),
    }


def _summarize_replay_result(result):
    if not isinstance(result, dict):
        return result
    reconstructed_state = result.get("reconstructed_state", {})
    latest_event = reconstructed_state.get("latest_event") if isinstance(reconstructed_state, dict) else None
    latest_summary = None
    if isinstance(latest_event, dict):
        latest_summary = {
            "event_id": latest_event.get("event_id"),
            "event_type": latest_event.get("event_type"),
            "subject_id": latest_event.get("subject_id"),
            "source_patch_id": latest_event.get("source_patch_id"),
        }
    return {
        "mode": result.get("mode"),
        "subject_id": result.get("subject_id"),
        "status": result.get("status"),
        "reconstructed_status": reconstructed_state.get("status") if isinstance(reconstructed_state, dict) else None,
        "applied_events_count": len(parse_json_collection(result.get("applied_events", []))),
        "ignored_events_count": len(parse_json_collection(result.get("ignored_events", []))),
        "latest_event": latest_summary,
        "warning_count": len(parse_json_collection(result.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(result.get("warnings", [])), limit=3),
        "evidence_paths": _dedupe_trim(parse_json_collection(result.get("evidence_paths", [])), limit=5),
    }


def _summarize_reconcile_result(result):
    if not isinstance(result, dict):
        return result
    return {
        "mode": result.get("mode"),
        "subject_id": result.get("subject_id"),
        "reconciliation": result.get("reconciliation"),
        "difference_count": len(parse_json_collection(result.get("differences", []))),
        "warning_count": len(parse_json_collection(result.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(result.get("warnings", [])), limit=3),
        "evidence_paths": _dedupe_trim(parse_json_collection(result.get("evidence_paths", [])), limit=5),
        "authority_note": result.get("authority_note"),
    }


def _summarize_context_capsule_result(result):
    if not isinstance(result, dict):
        return result
    return {
        "schema_id": result.get("schema_id"),
        "schema_version": result.get("schema_version"),
        "target": result.get("target"),
        "task": result.get("task"),
        "capsule_schema_version": result.get("capsule_schema_version"),
        "capsule_id": result.get("capsule_id"),
        "capsule_hash": result.get("capsule_hash"),
        "cache_status": result.get("cache_status"),
        "metrics": result.get("metrics", {}),
        "global_runtime_status": {
            "status": result.get("global_runtime_status", {}).get("status") if isinstance(result.get("global_runtime_status"), dict) else None,
            "health": result.get("global_runtime_status", {}).get("health") if isinstance(result.get("global_runtime_status"), dict) else None,
            "authority_boundary": result.get("global_runtime_status", {}).get("authority_boundary") if isinstance(result.get("global_runtime_status"), dict) else None,
            "snapshot": result.get("global_runtime_status", {}).get("snapshot") if isinstance(result.get("global_runtime_status"), dict) else None,
        },
        "freshness_summary": _summarize_freshness_result(result.get("freshness_summary", {})),
        "authority_summary": _summarize_authority_result(result.get("authority_summary", {})),
        "patch_summary": result.get("patch_summary", {}),
        "blocking_summary": result.get("blocking_summary", {}),
        "debt_summary": result.get("debt_summary", {}),
        "warning_count": len(parse_json_collection(result.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(result.get("warnings", [])), limit=3),
        "evidence_paths": _dedupe_trim(parse_json_collection(result.get("evidence_paths", [])), limit=5),
    }


def _stable_unique_strings(items):
    values = []
    for item in items or []:
        text = str(item).strip()
        if text and text not in values:
            values.append(text)
    return values


def _stable_sorted_unique_strings(items):
    return sorted(_stable_unique_strings(items))


def _sorted_json_records(records, limit=None):
    cleaned = [record for record in records or [] if record not in (None, "", [], {}, ())]
    cleaned.sort(key=_canonical_json_text)
    if limit is not None:
        return cleaned[:limit]
    return cleaned


def _build_governed_context_request_identity(db_path, normalized_target, task_text, query_text, limit):
    surface_request = {
        "surface_name": "governed_context_capsule_v1",
        "request_type": "governed_context_capsule",
        "command": "context-capsule",
        "db_path": str(Path(db_path)),
        "target": normalized_target,
        "task": task_text,
        "query": query_text,
        "limit": int(limit) if limit is not None else None,
    }
    route_result = route_parsed_request(surface_request, load_operation_registry(), None, "scripts.query_governance")
    canonical_focus = query_text or normalized_target or task_text
    canonical_request = build_canonical_routed_request_v1(
        operation_code=route_result.get("operation_code") or "governed_context_capsule",
        target_scope={
            "db_path": str(Path(db_path)),
            "target": normalized_target,
            "focus_query": canonical_focus,
            "limit": int(limit) if limit is not None else None,
        },
        target_identifiers=[canonical_focus] if canonical_focus else [],
        constraints={
            "db_path": str(Path(db_path)),
            "limit": int(limit) if limit is not None else None,
        },
        authority_requirements={
            "surface": "governed_context_capsule",
            "target": normalized_target,
        },
        freshness_requirements={
            "surface": "governed_context_capsule",
            "limit": int(limit) if limit is not None else None,
        },
        output_contract={
            "schema_id": GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION,
            "schema_version": GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE,
        },
        presentation_preferences={
            "task": task_text,
            "query": query_text,
        },
        candidate_policy_id=route_result.get("candidate_policy_id") or "governed_context_artifact_candidates_v1",
        source_request_digest=_hash_json_value(surface_request),
        normalization_record={
            "route_status": route_result.get("route_status"),
            "matched_rule_id": route_result.get("matched_rule_id"),
            "ambiguity_record": route_result.get("ambiguity_record", {}),
            "surface_request": surface_request,
            "normalized_target": normalized_target,
            "canonical_focus": canonical_focus,
        },
    )
    request_scope = {
        "db_path": str(Path(db_path)),
        "target": normalized_target,
        "task": canonical_focus,
        "query": canonical_focus,
        "focus_query": canonical_focus,
        "limit": int(limit) if limit is not None else None,
        "operation_code": canonical_request.get("operation_code"),
        "candidate_policy_id": canonical_request.get("candidate_policy_id"),
    }
    request_id = f"{GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION}:{_hash_json_value(canonical_request)[:16]}"
    request_identity = {
        "request_id": request_id,
        "request_type": "governed_context_capsule",
        "request_scope": request_scope,
        "schema_id": GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION,
        "schema_version": GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE,
        "command": "governed-context-capsule",
        "operation_code": canonical_request.get("operation_code"),
        "candidate_policy_id": canonical_request.get("candidate_policy_id"),
        "candidate_policy_version": route_result.get("candidate_policy_version"),
        "canonical_routed_request": canonical_request,
        "source_request_digest": _hash_json_value(surface_request),
        "normalization_record": canonical_request.get("normalization_record", {}),
        "surface_request": surface_request,
    }
    request_identity.update(request_scope)
    return request_identity


def _build_governed_context_source_records(source_inventory, freshness, authority):
    freshness_snapshot = freshness.get("db_snapshot_status", "unknown") if isinstance(freshness, dict) else "unknown"
    authority_status = authority.get("authority_status") if isinstance(authority, dict) else None
    if not authority_status and isinstance(authority, dict):
        authority_status = authority.get("decision", "unknown")
    authority_status = authority_status or "unknown"
    authority_owner = authority.get("authority_owner", "unknown") if isinstance(authority, dict) else "unknown"
    authority_source = authority.get("authority_source") if isinstance(authority, dict) else None
    authority_decision = authority.get("decision", "defer") if isinstance(authority, dict) else "defer"
    freshness_decision = freshness.get("decision", "unknown") if isinstance(freshness, dict) else "unknown"
    freshness_indexed_at = freshness.get("indexed_at") if isinstance(freshness, dict) else None
    records = []
    for entry in source_inventory or []:
        if not isinstance(entry, dict):
            continue
        path = normalize_repo_path(entry.get("path"))
        if not path:
            continue
        records.append(
            {
                "source_id": path,
                "path": path,
                "content_hash": entry.get("source_hash"),
                "authority": {
                    "status": authority_status,
                    "decision": authority_decision,
                    "owner": authority_owner,
                    "source": authority_source,
                },
                "freshness": {
                    "status": freshness_snapshot,
                    "decision": freshness_decision,
                    "indexed_at": freshness_indexed_at,
                },
                "roles": _stable_sorted_unique_strings(entry.get("roles", [])),
                "sections": _stable_sorted_unique_strings(entry.get("sections", [])),
                "exists": bool(entry.get("exists")),
            }
        )
    records.sort(key=lambda record: str(record.get("source_id") or record.get("path") or ""))
    return records


def _normalize_governed_context_freshness(freshness, source_change_paths=None, runtime_only_change_paths=None):
    freshness = dict(freshness or {})
    checked_sources = parse_json_collection(freshness.get("checked_sources", []))
    if not checked_sources:
        checked_sources = []
        checked_sources.extend(parse_json_collection(freshness.get("evidence_paths", [])))
        checked_sources.extend(parse_json_collection(source_change_paths or []))
        checked_sources.extend(parse_json_collection(runtime_only_change_paths or []))
    stale_sources = parse_json_collection(freshness.get("stale_sources", []))
    if not stale_sources and str(freshness.get("db_snapshot_status") or "").strip().lower() == "stale":
        stale_sources.extend(parse_json_collection(source_change_paths or []))
        if not stale_sources:
            stale_sources.extend(parse_json_collection(runtime_only_change_paths or []))
    freshness["status"] = freshness.get("db_snapshot_status", "unknown")
    freshness["checked_sources"] = _stable_sorted_unique_strings(checked_sources)
    freshness["stale_sources"] = _stable_sorted_unique_strings(stale_sources)
    return freshness


def _normalize_governed_context_authority(authority, normalized_target=None):
    authority = dict(authority or {})
    decision = str(authority.get("decision") or "defer").strip().lower() or "defer"
    authority_status = authority.get("authority_status") or decision
    if decision in {"allow", "allow_with_note"}:
        allowed_actions = ["read_context", "project_context", "reuse_capsule"]
        forbidden_actions = ["mutate_governed_state", "bypass_authority", "ignore_freshness"]
    elif decision == "warn":
        allowed_actions = ["read_context", "project_context"]
        forbidden_actions = ["mutate_governed_state", "apply_patch", "bypass_authority"]
    else:
        allowed_actions = ["read_context"]
        forbidden_actions = ["mutate_governed_state", "apply_patch", "bypass_authority", "ignore_freshness"]
    if normalized_target:
        allowed_actions.append(f"project_target:{normalized_target}")
    authority["authority_status"] = authority_status
    authority["allowed_actions"] = _stable_sorted_unique_strings(allowed_actions)
    authority["forbidden_actions"] = _stable_sorted_unique_strings(forbidden_actions)
    return authority


def _normalize_governed_context_patch_chain(patch_chain):
    patch_chain = dict(patch_chain or {})
    supersession = patch_chain.get("supersession", {}) if isinstance(patch_chain.get("supersession"), dict) else {}
    patch_chain["active_patch"] = patch_chain.get("patch_id")
    patch_chain["predecessors"] = _stable_sorted_unique_strings(parse_json_collection(patch_chain.get("dependencies", [])))
    patch_chain["successors"] = _stable_sorted_unique_strings(parse_json_collection(supersession.get("superseded_by", [])))
    patch_chain["chain_status"] = patch_chain.get("status", "unknown")
    return patch_chain


def _normalize_governed_context_relevant_artifacts(artifacts, freshness, authority, focus_query):
    normalized = []
    freshness_snapshot = freshness.get("db_snapshot_status", "unknown") if isinstance(freshness, dict) else "unknown"
    freshness_decision = freshness.get("decision", "unknown") if isinstance(freshness, dict) else "unknown"
    freshness_indexed_at = freshness.get("indexed_at") if isinstance(freshness, dict) else None
    authority_status = authority.get("authority_status") if isinstance(authority, dict) else None
    if not authority_status and isinstance(authority, dict):
        authority_status = authority.get("decision", "unknown")
    authority_status = authority_status or "unknown"
    authority_owner = authority.get("authority_owner", "unknown") if isinstance(authority, dict) else "unknown"
    authority_source = authority.get("authority_source") if isinstance(authority, dict) else None
    authority_decision = authority.get("decision", "defer") if isinstance(authority, dict) else "defer"
    for artifact in artifacts or []:
        if not isinstance(artifact, dict):
            continue
        entry = dict(artifact)
        path = normalize_repo_path(entry.get("path"))
        entry["path"] = path
        content_hash = entry.get("content_hash") or entry.get("source_hash") or _source_path_hash(path)
        relevance_reason = (
            entry.get("relevance_reason")
            or entry.get("reason")
            or entry.get("match_reason")
            or entry.get("orientation_status")
            or f"retrieved_for:{focus_query or 'context'}"
        )
        entry["artifact_id"] = str(entry.get("artifact_id") or path or content_hash or relevance_reason)
        entry["content_hash"] = content_hash
        entry["authority"] = {
            "status": authority_status,
            "decision": authority_decision,
            "owner": authority_owner,
            "source": authority_source,
        }
        entry["freshness"] = {
            "status": freshness_snapshot,
            "decision": freshness_decision,
            "indexed_at": freshness_indexed_at,
        }
        entry["relevance_reason"] = relevance_reason
        normalized.append(entry)

    def _artifact_sort_key(item):
        try:
            score = float(item.get("score", 0.0) or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        return (-score, str(item.get("path") or ""), str(item.get("orientation_status") or ""))

    normalized.sort(key=_artifact_sort_key)
    return normalized


def _normalize_governed_context_open_debt(debt_result):
    debt_result = dict(debt_result or {})
    debts = []
    for record in parse_json_collection(debt_result.get("debts", [])):
        if isinstance(record, dict):
            debts.append(dict(record))
    debts.sort(key=lambda record: str(record.get("debt_id") or ""))
    return debts, debt_result


def _build_governed_context_metrics(cache_status, build_time_ms, serialized_bytes, estimated_tokens, artifact_count, source_count, excluded_source_count):
    return {
        "build_time_ms": build_time_ms,
        "serialized_bytes": serialized_bytes,
        "estimated_tokens": estimated_tokens,
        "artifact_count": artifact_count,
        "source_count": source_count,
        "excluded_source_count": excluded_source_count,
        "cache_status": cache_status,
    }


def validate_governed_context_capsule_payload(capsule, expected_hash=None, expected_id=None):
    errors = []
    if not isinstance(capsule, dict):
        return ["capsule is not an object"]

    required_top_level = [
        "schema_id",
        "schema_version",
        "capsule_id",
        "capsule_hash",
        "request_identity",
        "current_state",
        "freshness",
        "authority",
        "patch_chain",
        "open_debt",
        "relevant_artifacts",
        "runtime_trace",
        "candidate_actions",
        "exclusions",
        "provenance",
        "metrics",
    ]
    for field in required_top_level:
        if field not in capsule:
            errors.append(f"missing_top_level_field:{field}")

    if capsule.get("schema_id") != GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION:
        errors.append("schema_id_mismatch")
    if capsule.get("schema_version") != GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE:
        errors.append("schema_version_mismatch")
    if expected_hash is not None and capsule.get("capsule_hash") != expected_hash:
        errors.append("capsule_hash_mismatch")
    if expected_id is not None and capsule.get("capsule_id") != expected_id:
        errors.append("capsule_id_mismatch")

    request_identity = capsule.get("request_identity", {})
    if not isinstance(request_identity, dict):
        errors.append("request_identity_not_object")
        request_identity = {}
    for field in ("request_id", "request_type", "request_scope"):
        if field not in request_identity:
            errors.append(f"missing_request_identity_field:{field}")
    request_scope = request_identity.get("request_scope", {})
    if not isinstance(request_scope, dict):
        errors.append("request_scope_not_object")

    freshness = capsule.get("freshness", {})
    if not isinstance(freshness, dict):
        errors.append("freshness_not_object")
        freshness = {}
    for field in ("status", "checked_sources", "stale_sources"):
        if field not in freshness:
            errors.append(f"missing_freshness_field:{field}")

    authority = capsule.get("authority", {})
    if not isinstance(authority, dict):
        errors.append("authority_not_object")
        authority = {}
    for field in ("authority_status", "allowed_actions", "forbidden_actions"):
        if field not in authority:
            errors.append(f"missing_authority_field:{field}")

    patch_chain = capsule.get("patch_chain", {})
    if not isinstance(patch_chain, dict):
        errors.append("patch_chain_not_object")
        patch_chain = {}
    for field in ("active_patch", "predecessors", "successors", "chain_status"):
        if field not in patch_chain:
            errors.append(f"missing_patch_chain_field:{field}")

    if not isinstance(capsule.get("open_debt"), list):
        errors.append("open_debt_not_array")

    relevant_artifacts = capsule.get("relevant_artifacts", [])
    if not isinstance(relevant_artifacts, list):
        errors.append("relevant_artifacts_not_array")
        relevant_artifacts = []
    for index, artifact in enumerate(relevant_artifacts):
        if not isinstance(artifact, dict):
            errors.append(f"artifact_not_object:{index}")
            continue
        for field in ("artifact_id", "path", "content_hash", "authority", "freshness", "relevance_reason"):
            if field not in artifact:
                errors.append(f"artifact_missing_field:{index}:{field}")

    provenance = capsule.get("provenance", {})
    if not isinstance(provenance, dict):
        errors.append("provenance_not_object")
        provenance = {}
    for field in ("source_records", "producer", "producer_version"):
        if field not in provenance:
            errors.append(f"missing_provenance_field:{field}")
    source_records = provenance.get("source_records", [])
    if not isinstance(source_records, list):
        errors.append("source_records_not_array")
    metrics = capsule.get("metrics", {})
    if not isinstance(metrics, dict):
        errors.append("metrics_not_object")
        metrics = {}
    for field in ("build_time_ms", "serialized_bytes", "estimated_tokens", "artifact_count", "source_count", "excluded_source_count", "cache_status"):
        if field not in metrics:
            errors.append(f"missing_metrics_field:{field}")

    return errors


def _source_path_exists(path):
    normalized = normalize_repo_path(path)
    if not normalized:
        return False
    candidate = Path(normalized)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.exists()


def _source_path_hash(path):
    normalized = normalize_repo_path(path)
    if not normalized:
        return None
    candidate = Path(normalized)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    if not candidate.exists() or not candidate.is_file():
        return None
    try:
        stat = candidate.stat()
    except OSError:
        return None
    return _hash_json_value(
        {
            "path": normalize_repo_path(candidate),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "mode": "metadata",
        }
    )


def _normalize_retrieved_artifacts(results):
    normalized_results = []
    for result in results or []:
        if not isinstance(result, dict):
            continue
        entry = dict(result)
        path = normalize_repo_path(entry.get("path"))
        entry["path"] = path
        entry["is_residue"] = str(entry.get("orientation_status") or "").strip().lower() in {
            "historical_residue",
            "superseded",
            "deprecated",
            "archived",
        }
        entry["source_exists"] = _source_path_exists(path)
        entry["source_hash"] = _source_path_hash(path)
        normalized_results.append(entry)

    def _artifact_sort_key(item):
        try:
            score = float(item.get("score", 0.0) or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        return (-score, str(item.get("path") or ""), str(item.get("orientation_status") or ""))

    normalized_results.sort(key=_artifact_sort_key)
    return normalized_results


def _build_governed_context_source_inventory(raw_sources):
    source_index = {}
    exclusions = []
    for raw in raw_sources or []:
        if not isinstance(raw, dict):
            continue
        path = normalize_repo_path(raw.get("path"))
        role = str(raw.get("role") or "unspecified").strip() or "unspecified"
        section = str(raw.get("section") or role).strip() or role
        if not path:
            exclusions.append(
                {
                    "source": None,
                    "role": role,
                    "section": section,
                    "reason": "missing_path",
                }
            )
            continue

        entry = source_index.get(path)
        if entry is None:
            entry = {
                "path": path,
                "roles": [role],
                "sections": [section],
                "exists": _source_path_exists(path),
                "source_hash": _source_path_hash(path),
            }
            source_index[path] = entry
        else:
            entry["roles"].append(role)
            entry["sections"].append(section)
            exclusions.append(
                {
                    "source": path,
                    "role": role,
                    "section": section,
                    "reason": "duplicate_source",
                }
            )

    sources = []
    for path in sorted(source_index):
        entry = dict(source_index[path])
        entry["roles"] = _stable_sorted_unique_strings(entry.get("roles", []))
        entry["sections"] = _stable_sorted_unique_strings(entry.get("sections", []))
        sources.append(entry)

    return sources, exclusions


def _stable_unique_source_records(raw_sources):
    seen = set()
    records = []
    for raw in raw_sources or []:
        if not isinstance(raw, dict):
            continue
        path = normalize_repo_path(raw.get("path"))
        if not path:
            continue
        role = str(raw.get("role") or "unspecified").strip() or "unspecified"
        section = str(raw.get("section") or role).strip() or role
        key = (path, role, section)
        if key in seen:
            continue
        seen.add(key)
        records.append({"path": path, "role": role, "section": section})
    return records


def _build_governed_context_candidate_actions(current_state, freshness, authority, patch_chain, open_debt, runtime_trace, database_health):
    actions = []
    freshness_status = str(freshness.get("db_snapshot_status") or "unknown").strip().lower()
    authority_decision = str(authority.get("decision") or "unknown").strip().lower()
    patch_decision = str(patch_chain.get("decision") or "unknown").strip().lower()
    patch_status = str(patch_chain.get("status") or "unknown").strip().lower()
    debt_summary = open_debt.get("summary", {}) if isinstance(open_debt, dict) and isinstance(open_debt.get("summary"), dict) else {}
    blocking_debt = int(debt_summary.get("blocking", 0) or 0)
    open_debt_count = int(debt_summary.get("open", 0) or 0)
    trace_report = runtime_trace.get("trace_report", {}) if isinstance(runtime_trace.get("trace_report"), dict) else {}
    trace_summary = trace_report.get("trace_summary", {}) if isinstance(trace_report.get("trace_summary"), dict) else {}
    missing_link_count = int(trace_summary.get("missing_links_count", 0) or 0)
    db_status = str(database_health.get("status") or "unknown").strip().lower()

    def add(action_id, reason, priority="medium", trigger=None):
        actions.append(
            {
                "action_id": action_id,
                "priority": priority,
                "trigger": trigger,
                "reason": reason,
            }
        )

    if db_status not in {"pass", "warning"}:
        add(
            "review_database_health",
            f"Database health is {database_health.get('status', 'unknown')}.",
            priority="high",
            trigger="database_health.status != pass",
        )

    if str(current_state.get("status") or "unknown").strip().lower() == "unavailable":
        add(
            "open_governance_runtime",
            "Current governance state is unavailable.",
            priority="high",
            trigger="current_state.status == unavailable",
        )

    if freshness_status != "fresh":
        add(
            "refresh_snapshot",
            f"Snapshot freshness is {freshness_status}.",
            priority="high",
            trigger="freshness.db_snapshot_status != fresh",
        )

    if authority_decision in {"defer", "block"}:
        add(
            "resolve_authority_boundary",
            f"Authority decision is {authority_decision}.",
            priority="high",
            trigger="authority.decision in {defer, block}",
        )

    if patch_decision in {"defer", "block"} or patch_status in {"blocked", "missing"}:
        add(
            "resolve_patch_chain",
            f"Patch chain is {patch_status} with decision {patch_decision}.",
            priority="high",
            trigger="patch_chain requires attention",
        )

    if blocking_debt > 0 or open_debt_count > 0:
        add(
            "resolve_open_debt",
            f"{blocking_debt} blocking and {open_debt_count} open debt item(s) remain.",
            priority="high",
            trigger="open_debt.summary contains unresolved items",
        )

    if missing_link_count > 0:
        add(
            "review_trace_gaps",
            f"{missing_link_count} trace gap(s) remain unresolved.",
            priority="medium",
            trigger="runtime_trace.trace_summary.missing_links_count > 0",
        )

    if not actions:
        add(
            "proceed_governed_action",
            "No obvious governed blockers remain in the capsule.",
            priority="low",
            trigger="all governed checks are within tolerance",
        )

    return actions


def _summarize_gate_authority_resolution(result):
    if not isinstance(result, dict):
        return result
    target_decisions = _summarize_target_decisions(result.get("target_decisions", []), limit=5)
    return {
        "winning_authority": result.get("winning_authority"),
        "rule": result.get("rule"),
        "runtime_boundary": result.get("runtime_boundary"),
        "decision": result.get("decision"),
        "reason": result.get("reason"),
        "target_decision_count": len(parse_json_collection(result.get("target_decisions", []))),
        "target_decisions": target_decisions,
    }


def _summarize_gate_semantic_resolution(result):
    if not isinstance(result, dict):
        return result
    target_decisions = _summarize_target_decisions(result.get("target_decisions", []), limit=5)
    return {
        "winning_authority": result.get("winning_authority"),
        "rule": result.get("rule"),
        "declared": _dedupe_trim(parse_json_collection(result.get("declared", [])), limit=10),
        "decision": result.get("decision"),
        "reason": result.get("reason"),
        "target_decision_count": len(parse_json_collection(result.get("target_decisions", []))),
        "target_decisions": target_decisions,
        "warning_count": len(parse_json_collection(result.get("warnings", []))),
        "warnings": _dedupe_trim(parse_json_collection(result.get("warnings", [])), limit=3),
    }


def _summarize_patch_chain_result(chain_result, requested_level, emitted_level):
    if not isinstance(chain_result, dict):
        return chain_result

    if emitted_level == 0:
        payload = build_patch_chain_light_summary(chain_result)
    elif emitted_level == 1:
        payload = build_patch_chain_light_summary(chain_result)
        payload.update(
            {
                "dependencies": _dedupe_trim(parse_json_collection(chain_result.get("dependencies", [])), limit=10),
                "missing_dependencies": _dedupe_trim(parse_json_collection(chain_result.get("missing_dependencies", [])), limit=10),
                "late_registration": chain_result.get("late_registration"),
                "supersession": chain_result.get("supersession", {}),
                "dependency_graph": _summarize_dependency_results(chain_result.get("dependency_results", []), limit=10),
                "warnings": _dedupe_trim(parse_json_collection(chain_result.get("warnings", [])), limit=5),
                "evidence_paths": _dedupe_trim(parse_json_collection(chain_result.get("evidence_paths", [])), limit=5),
                "runtime_path": "diagnostic",
            }
        )
    elif emitted_level == 2:
        payload = dict(chain_result)
        payload.pop("dependency_results", None)
        payload["dependency_graph"] = _summarize_dependency_results(chain_result.get("dependency_results", []), limit=10)
        payload["dependencies"] = _dedupe_trim(parse_json_collection(chain_result.get("dependencies", [])), limit=15)
        payload["missing_dependencies"] = _dedupe_trim(parse_json_collection(chain_result.get("missing_dependencies", [])), limit=10)
        payload["blockers"] = _dedupe_trim(parse_json_collection(chain_result.get("blockers", [])), limit=10)
        payload["warnings"] = _dedupe_trim(parse_json_collection(chain_result.get("warnings", [])), limit=10)
        payload["evidence_paths"] = _dedupe_trim(parse_json_collection(chain_result.get("evidence_paths", [])), limit=10)
        payload["runtime_path"] = "governance"
        payload["full_report_available"] = True
    else:
        payload = dict(chain_result)
        payload["runtime_path"] = "forensic"
        payload["full_report_available"] = True

    return _attach_evidence_level_metadata(payload, requested_level, emitted_level)


def _summarize_patch_gate_result(gate_result, requested_level, emitted_level):
    if not isinstance(gate_result, dict):
        return gate_result

    if emitted_level == 0:
        payload = build_patch_gate_light_summary(gate_result)
    elif emitted_level == 1:
        payload = {
            "patch_id": gate_result.get("patch_id"),
            "campaign_id": gate_result.get("campaign_id"),
            "requested_action": gate_result.get("requested_action"),
            "decision": gate_result.get("decision"),
            "reason": gate_result.get("reason"),
            "blocking_conditions": _dedupe_trim(parse_json_collection(gate_result.get("blocking_conditions", [])), limit=5),
            "defer_conditions": _dedupe_trim(parse_json_collection(gate_result.get("defer_conditions", [])), limit=5),
            "dependency_resolution": {
                "declared": _dedupe_trim(parse_json_collection(gate_result.get("dependency_resolution", {}).get("declared", [])), limit=10)
                if isinstance(gate_result.get("dependency_resolution"), dict)
                else [],
                "missing": _dedupe_trim(parse_json_collection(gate_result.get("dependency_resolution", {}).get("missing", [])), limit=10)
                if isinstance(gate_result.get("dependency_resolution"), dict)
                else [],
            },
            "authority_resolution": _summarize_gate_authority_resolution(gate_result.get("authority_resolution", {})),
            "semantic_authority_resolution": _summarize_gate_semantic_resolution(gate_result.get("semantic_authority_resolution", {})),
            "patch_chain": _summarize_patch_chain_result(gate_result.get("patch_chain", {}), requested_level, 1),
            "provenance_resolution": gate_result.get("provenance_resolution", {}),
            "validator_resolution": gate_result.get("validator_resolution", {}),
            "warnings": _dedupe_trim(parse_json_collection(gate_result.get("warnings", [])), limit=5),
            "evidence_paths": _dedupe_trim(parse_json_collection(gate_result.get("evidence_paths", [])), limit=5),
            "runtime_path": "diagnostic",
            "full_report_available": True,
        }
    elif emitted_level == 2:
        payload = dict(gate_result)
        payload.pop("evidence_json", None)
        payload.pop("metadata_json", None)
        payload.pop("db_snapshot", None)
        payload["current_state"] = _summarize_current_state_capsule(gate_result.get("current_state", {}))
        payload["authority_resolution"] = _summarize_gate_authority_resolution(gate_result.get("authority_resolution", {}))
        payload["semantic_authority_resolution"] = _summarize_gate_semantic_resolution(gate_result.get("semantic_authority_resolution", {}))
        payload["patch_chain"] = _summarize_patch_chain_result(gate_result.get("patch_chain", {}), requested_level, 2)
        payload["debt_resolution"] = _summarize_debt_result(gate_result.get("debt_resolution", {}))
        payload["freshness"] = _summarize_freshness_result(gate_result.get("freshness", {}))
        payload["blocking_conditions"] = _dedupe_trim(parse_json_collection(gate_result.get("blocking_conditions", [])), limit=10)
        payload["defer_conditions"] = _dedupe_trim(parse_json_collection(gate_result.get("defer_conditions", [])), limit=10)
        payload["warnings"] = _dedupe_trim(parse_json_collection(gate_result.get("warnings", [])), limit=10)
        payload["runtime_path"] = "governance"
        payload["full_report_available"] = True
    else:
        payload = dict(gate_result)
        payload["runtime_path"] = "forensic"
        payload["full_report_available"] = True

    return _attach_evidence_level_metadata(payload, requested_level, emitted_level)


def build_evidence_level_result(command, result, requested_level):
    if requested_level is None:
        return result

    emitted_level = requested_level
    if command == "patch-chain":
        return _summarize_patch_chain_result(result, requested_level, emitted_level)
    if command in {"patch-gate", "patch-file"}:
        return _summarize_patch_gate_result(result, requested_level, emitted_level)
    if command == "current-state":
        if emitted_level == 0:
            payload = _summarize_current_state_capsule(result)
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)
    if command == "authority":
        if emitted_level == 0:
            payload = _summarize_authority_result(result)
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)
    if command == "freshness":
        if emitted_level == 0:
            payload = _summarize_freshness_result(result)
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)
    if command == "debt":
        if emitted_level == 0:
            payload = _summarize_debt_result(result)
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)
    if command == "context-capsule":
        if emitted_level == 0:
            payload = _summarize_context_capsule_result(result)
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)
    if command == "events":
        if emitted_level == 0:
            payload = _summarize_events_result(result)
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)
    if command == "replay-events":
        if emitted_level == 0:
            payload = _summarize_replay_result(result)
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)
    if command == "reconcile-events":
        if emitted_level == 0:
            payload = _summarize_reconcile_result(result)
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)
    if command == "emit-event":
        if emitted_level == 0:
            payload = {
                "mode": result.get("mode"),
                "status": result.get("status"),
                "reason": result.get("reason"),
                "event": _summarize_events_result({"events": [result.get("event")]})["events"][0] if result.get("event") else None,
            }
        elif emitted_level == 1:
            payload = _trim_nested_lists(result, limit=5)
        else:
            payload = dict(result)
        return _attach_evidence_level_metadata(payload, requested_level, emitted_level)

    payload = _trim_nested_lists(result, limit=5) if emitted_level == 1 else dict(result)
    return _attach_evidence_level_metadata(payload, requested_level, emitted_level)


def build_governed_context_capsule_v1(db_path, target=None, task=None, query=None, limit=20, use_cache=True):
    started_at = time.perf_counter()
    db_file = Path(db_path)
    normalized_target = normalize_repo_path(target)
    task_text = str(task).strip() if task else None
    query_text = str(query).strip() if query else None
    focus_query = query_text or normalized_target or task_text
    request_identity = _build_governed_context_request_identity(db_file, normalized_target, task_text, query_text, limit)

    current_state = build_current_state_capsule(db_path)
    report = load_optional_json(GLOBAL_HEALTH_REPORT)
    db_health_status = extract_db_validation_status(report)
    current_state_projection = current_state.get("projection", {}) if isinstance(current_state.get("projection"), dict) else {}
    database_health = {
        "status": db_health_status if db_health_status in {"pass", "warn", "fail"} else "warn",
        "db_path": db_path,
        "schema_path": str(ROOT / "registry/db/schema.sql"),
        "integrity_check": "reported" if db_health_status != "unknown" else "skipped",
        "table_status": {},
        "row_counts": {},
        "orientation_status_values": {},
        "retrieval_smoke": {"status": "reported" if db_health_status != "unknown" else "skipped"},
        "supersession_edge_quality": {"status": "reported" if db_health_status != "unknown" else "skipped"},
        "stale_index_warnings": [] if db_health_status != "unknown" else ["Capsule fast path skipped the deep DB health audit."],
        "ssot_boundary": "global_report",
        "maintenance_recommendations": [],
    }
    database_errors = []
    freshness = current_state.get("freshness", {}) if isinstance(current_state.get("freshness"), dict) else {}

    if normalized_target:
        authority_result = build_authority_resolution_result(argparse.Namespace(db=db_path, target=normalized_target))
        debt_result = build_debt_runtime_result(db_path, target=normalized_target, status_filter="all", current_state=current_state)
    else:
        authority_result = {
            "target": None,
            "authority_owner": current_state.get("runtime", {}).get("authority_boundary", "unknown") if isinstance(current_state.get("runtime"), dict) else "unknown",
            "authority_source": None,
            "supersession": {"status": "unknown", "superseded_by": []},
            "conflict_state": current_state.get("runtime", {}).get("authority_boundary", "unknown") if isinstance(current_state.get("runtime"), dict) else "unknown",
            "decision": "defer" if (current_state.get("runtime", {}) or {}).get("authority_boundary") == "mixed" else "allow",
            "reason": "Authority boundary summarized from current-state.",
            "evidence_paths": current_state.get("evidence_paths", []),
            "warnings": current_state.get("warnings", []),
        }
        debt_result = build_debt_runtime_result(db_path, status_filter="all", current_state=current_state)

    patch_candidates = find_patch_candidates_for_target(normalized_target) if normalized_target else [find_latest_applied_patch_candidate()]
    patch_candidates = [candidate for candidate in patch_candidates if candidate and candidate[0]]
    patch_record = patch_candidates[0][0] if patch_candidates else None
    patch_path = patch_candidates[0][1] if patch_candidates else None
    if patch_record is None and current_state.get("latest_decisions"):
        latest_patch_id = current_state["latest_decisions"][0].get("patch_id")
        if latest_patch_id:
            patch_record, patch_path = load_patch_record_by_id(latest_patch_id)

    ledger_index = load_governance_change_ledger_index()
    if isinstance(patch_record, dict) and patch_record.get("patch_id"):
        patch_chain = build_patch_chain_result(
            patch_record["patch_id"],
            current_state=current_state,
            ledger_index=ledger_index,
        )
    else:
        patch_chain = {
            "patch_id": None,
            "status": "unknown",
            "dependencies": [],
            "missing_dependencies": [],
            "supersession": {"status": "unknown", "superseded_by": []},
            "late_registration": "unknown",
            "blockers": [],
            "decision": "defer",
            "reason": "No patch context is available.",
            "evidence_paths": [],
            "warnings": [],
        }

    retrieval = retrieve_artifacts(db_path, focus_query, limit=limit, explain=True)
    if not isinstance(retrieval, dict):
        retrieval = {"results": [], "warnings": []}
    relevant_artifacts = _normalize_retrieved_artifacts(retrieval.get("results", []))

    trace = run_registry_runtime_trace(db_path, focus_query, limit=limit)
    if not isinstance(trace, dict):
        trace = {"trace_report": {"resolved_links": [], "missing_links": [], "conflicts": [], "supersession_cautions": [], "warnings": []}}
    trace_report = trace.get("trace_report", {}) if isinstance(trace.get("trace_report"), dict) else {}
    normalized_trace_report = {
        "query": trace_report.get("query", focus_query),
        "mode": trace_report.get("mode", "read_only_traceability"),
        "registry_sources_read": _stable_sorted_unique_strings(trace_report.get("registry_sources_read", [])),
        "runtime_sources_read": _stable_sorted_unique_strings(trace_report.get("runtime_sources_read", [])),
        "db_sources_read": _stable_sorted_unique_strings(trace_report.get("db_sources_read", [])),
        "trace_summary": {
            "entities_count": len(trace_report.get("trace_entities", [])) if isinstance(trace_report.get("trace_entities"), list) else 0,
            "edges_count": len(trace_report.get("trace_edges", [])) if isinstance(trace_report.get("trace_edges"), list) else 0,
            "resolved_links_count": len(trace_report.get("resolved_links", [])) if isinstance(trace_report.get("resolved_links"), list) else 0,
            "missing_links_count": len(trace_report.get("missing_links", [])) if isinstance(trace_report.get("missing_links"), list) else 0,
        },
        "resolved_links": _dedupe_trim(trace_report.get("resolved_links", []), limit=10),
        "missing_links": _sorted_json_records(trace_report.get("missing_links", []), limit=10),
        "conflicts": _sorted_json_records(trace_report.get("conflicts", []), limit=10),
        "residue_only_sources": _dedupe_trim(trace_report.get("residue_only_sources", []), limit=10),
        "supersession_cautions": _dedupe_trim(trace_report.get("supersession_cautions", []) + retrieval.get("warnings", []), limit=10),
        "recommended_next_actions": _dedupe_trim(trace_report.get("recommended_next_actions", []), limit=10),
        "warnings": _dedupe_trim(trace_report.get("warnings", []) + retrieval.get("warnings", []), limit=10),
    }

    claim_graph = build_claim_evidence_graph(db_path)
    if not isinstance(claim_graph, dict):
        claim_graph = {"nodes": [], "edges": []}
    claim_graph_summary = {
        "nodes_count": len(claim_graph.get("nodes", [])) if isinstance(claim_graph.get("nodes"), list) else 0,
        "edges_count": len(claim_graph.get("edges", [])) if isinstance(claim_graph.get("edges"), list) else 0,
    }

    recent_governance_events = load_recent_governance_events(db_path, limit=1)

    raw_sources = []

    def add_sources(values, role, section):
        for value in parse_json_collection(values):
            raw_sources.append({"path": value, "role": role, "section": section})

    add_sources(current_state.get("evidence_paths", []), "current_state", "current_state")
    add_sources(freshness.get("evidence_paths", []), "freshness", "freshness")
    add_sources(authority_result.get("evidence_paths", []), "authority", "authority")
    add_sources(patch_chain.get("evidence_paths", []), "patch_chain", "patch_chain")
    add_sources(debt_result.get("evidence_paths", []), "open_debt", "open_debt")
    if isinstance(current_state_projection, dict):
        for projection_name, projection in current_state_projection.items():
            if isinstance(projection, dict):
                add_sources(projection.get("evidence_paths", []), f"projection:{projection_name}", f"projection:{projection_name}")
    add_sources(normalized_trace_report.get("registry_sources_read", []), "trace_registry_source", "runtime_trace")
    add_sources(normalized_trace_report.get("runtime_sources_read", []), "trace_runtime_source", "runtime_trace")
    add_sources(normalized_trace_report.get("db_sources_read", []), "trace_db_source", "runtime_trace")
    add_sources([artifact.get("path") for artifact in relevant_artifacts], "retrieved_artifact", "retrieval")
    add_sources([database_health.get("db_path")], "database_health", "db_health")
    add_sources([database_health.get("schema_path")], "database_health_schema", "db_health")
    if patch_path:
        raw_sources.append({"path": patch_path, "role": "patch_file", "section": "patch_chain"})
    unique_raw_sources = _stable_unique_source_records(raw_sources)
    source_inventory_limit = 128
    source_limit_exceeded = len(unique_raw_sources) > source_inventory_limit
    source_limit_omitted = max(0, len(unique_raw_sources) - source_inventory_limit)
    source_inventory_input = unique_raw_sources[:source_inventory_limit]
    source_inventory, exclusions = _build_governed_context_source_inventory(source_inventory_input)
    source_paths = [entry.get("path") for entry in source_inventory if entry.get("path")]
    source_hashes = {
        entry.get("path"): entry.get("source_hash")
        for entry in source_inventory
        if entry.get("path")
    }
    normalized_freshness = _normalize_governed_context_freshness(
        freshness,
        source_change_paths=freshness.get("source_change_paths", []),
        runtime_only_change_paths=freshness.get("runtime_only_change_paths", []),
    )
    normalized_authority = _normalize_governed_context_authority(authority_result, normalized_target=normalized_target)
    normalized_patch_chain = _normalize_governed_context_patch_chain(patch_chain)
    open_debt_items, open_debt_detail = _normalize_governed_context_open_debt(debt_result)
    source_records = _build_governed_context_source_records(source_inventory, normalized_freshness, normalized_authority)
    relevant_artifacts = _normalize_governed_context_relevant_artifacts(
        relevant_artifacts,
        normalized_freshness,
        normalized_authority,
        focus_query,
    )

    current_state_for_hash = {
        "status": current_state.get("status", "unavailable"),
        "health": {
            "global_validation": current_state.get("health", {}).get("global_validation")
            if isinstance(current_state.get("health"), dict)
            else None,
        },
        "runtime": {
            "db_first_gate": current_state.get("runtime", {}).get("db_first_gate")
            if isinstance(current_state.get("runtime"), dict)
            else None,
            "authority_boundary": current_state.get("runtime", {}).get("authority_boundary")
            if isinstance(current_state.get("runtime"), dict)
            else None,
        },
        "blocker_count": len(parse_json_collection(current_state.get("blockers", []))),
        "open_debt_count": len(parse_json_collection(current_state.get("open_debt", []))),
        "latest_decision_count": len(parse_json_collection(current_state.get("latest_decisions", []))),
    }
    freshness_for_hash = {
        "db_snapshot_status": normalized_freshness.get("db_snapshot_status", "unknown"),
        "decision": normalized_freshness.get("decision", "block"),
        "indexed_at": normalized_freshness.get("indexed_at"),
        "artifact_indexed_at": normalized_freshness.get("artifact_indexed_at"),
        "last_refresh_attempt": normalized_freshness.get("last_refresh_attempt"),
        "last_refresh_result": normalized_freshness.get("last_refresh_result"),
        "source_worktree_marker": normalized_freshness.get("source_worktree_marker"),
        "refresh_source": normalized_freshness.get("refresh_source"),
        "latest_known_worktree_change": normalized_freshness.get("latest_known_worktree_change"),
        "source_change_count": normalized_freshness.get("source_change_count", 0),
        "source_change_paths": _stable_sorted_unique_strings(normalized_freshness.get("source_change_paths", [])),
    }

    normalized_db_path = normalize_repo_path(db_file) or str(db_file)
    stable_db_source_hash = _hash_json_value(
        {
            "current_state": current_state_for_hash,
            "freshness": freshness_for_hash,
            "authority": normalized_authority,
            "patch_chain": normalized_patch_chain,
            "open_debt": open_debt_items,
            "relevant_artifacts": relevant_artifacts,
            "runtime_trace": normalized_trace_report,
            "database_health": database_health,
        }
    )
    if stable_db_source_hash:
        for record in source_records:
            if normalize_repo_path(record.get("path")) == normalized_db_path:
                record["content_hash"] = stable_db_source_hash
        for entry in source_inventory:
            if normalize_repo_path(entry.get("path")) == normalized_db_path:
                entry["source_hash"] = stable_db_source_hash
        source_hashes[normalized_db_path] = stable_db_source_hash

    warnings = _dedupe_trim(
        list(current_state.get("warnings", []))
        + list(normalized_authority.get("warnings", []))
        + list(normalized_patch_chain.get("warnings", []))
        + list(open_debt_detail.get("warnings", []))
        + list(retrieval.get("warnings", []))
        + list(normalized_trace_report.get("warnings", []))
        + list(database_health.get("stale_index_warnings", []))
        + list(database_errors),
        limit=15,
    )
    if not current_state.get("status") or current_state.get("status") == "unavailable":
        warnings.append("Current-state capsule is unavailable.")
    if database_health.get("status") == "fail":
        warnings.append("Database health check failed.")
    if source_limit_exceeded:
        warnings.append(
            f"Source inventory capped at {source_inventory_limit} records; {source_limit_omitted} additional sources were omitted."
        )
    warnings = _dedupe_trim(warnings, limit=20)

    candidate_actions = _build_governed_context_candidate_actions(
        current_state,
        normalized_freshness,
        normalized_authority,
        normalized_patch_chain,
        open_debt_detail,
        normalized_trace_report,
        database_health,
    )

    candidate_set_hash_basis = {
        "relevant_artifacts": relevant_artifacts,
        "candidate_actions": candidate_actions,
        "exclusions": exclusions,
        "authority": normalized_authority,
        "freshness": freshness_for_hash,
        "patch_chain": normalized_patch_chain,
    }
    candidate_set_hash = _hash_json_value(candidate_set_hash_basis)
    request_identity["candidate_set_hash"] = candidate_set_hash
    request_identity["candidate_set_policy_id"] = request_identity.get("candidate_policy_id")
    request_identity["candidate_set_policy_version"] = request_identity.get("candidate_policy_version")

    provenance_section_hashes = {
        "current_state": _hash_json_value(current_state_for_hash),
        "freshness": _hash_json_value(freshness_for_hash),
        "authority": _hash_json_value(normalized_authority),
        "patch_chain": _hash_json_value(normalized_patch_chain),
        "open_debt": _hash_json_value(open_debt_detail),
        "open_debt_items": _hash_json_value(open_debt_items),
        "relevant_artifacts": _hash_json_value(relevant_artifacts),
        "runtime_trace": _hash_json_value(normalized_trace_report),
        "database_health": _hash_json_value(database_health),
        "candidate_actions": _hash_json_value(candidate_actions),
        "candidate_set": candidate_set_hash,
        "exclusions": _hash_json_value(exclusions),
        "recent_governance_events": _hash_json_value(recent_governance_events),
        "source_records": _hash_json_value(source_records),
    }

    provenance = {
        "db_path": str(db_file),
        "target": normalized_target,
        "task": task_text,
        "query": query_text,
        "focus_query": focus_query,
        "schema_version": GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE,
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_paths": source_paths,
        "source_hashes": source_hashes,
        "source_records": source_records,
        "source_count": len(source_paths),
        "excluded_source_count": len(exclusions),
        "producer": "scripts.query_governance.build_governed_context_capsule_v1",
        "producer_version": GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE,
        "section_hashes": provenance_section_hashes,
    }

    hash_basis = {
        "schema_id": GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION,
        "schema_version": GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE,
        "capsule_schema_version": GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION,
        "request_identity": {
            "request_type": request_identity.get("request_type"),
            "request_scope": request_identity.get("request_scope"),
            "schema_id": request_identity.get("schema_id"),
            "schema_version": request_identity.get("schema_version"),
            "command": request_identity.get("command"),
            "operation_code": request_identity.get("operation_code"),
            "candidate_policy_id": request_identity.get("candidate_policy_id"),
            "candidate_policy_version": request_identity.get("candidate_policy_version"),
            "candidate_set_hash": request_identity.get("candidate_set_hash"),
        },
        "section_hashes": provenance_section_hashes,
        "source_fingerprint": {
            "db_path": provenance["db_path"],
            "target": provenance["target"],
            "focus_query": provenance["focus_query"],
            "schema_version": provenance["schema_version"],
            "producer": provenance["producer"],
            "producer_version": provenance["producer_version"],
            "source_paths": provenance["source_paths"],
            "source_hashes": provenance["source_hashes"],
            "source_count": provenance["source_count"],
            "excluded_source_count": provenance["excluded_source_count"],
        },
        "summary": {
        "current_state_status": current_state.get("status", "unavailable"),
            "freshness_state": normalized_freshness.get("db_snapshot_status", "unknown"),
            "authority_state": normalized_authority.get("decision", "unknown"),
            "patch_chain_state": normalized_patch_chain.get("status", "unknown"),
            "open_debt_open": open_debt_detail.get("summary", {}).get("open", 0) if isinstance(open_debt_detail.get("summary"), dict) else 0,
            "open_debt_blocking": open_debt_detail.get("summary", {}).get("blocking", 0) if isinstance(open_debt_detail.get("summary"), dict) else 0,
            "retrieval_count": len(relevant_artifacts),
            "trace_summary": normalized_trace_report.get("trace_summary", {}),
            "claim_graph_summary": claim_graph_summary,
            "database_health_status": database_health.get("status", "unknown") if isinstance(database_health, dict) else "unknown",
            "recent_governance_event_count": len(recent_governance_events),
            "candidate_action_count": len(candidate_actions),
            "warning_count": len(warnings),
            "exclusion_count": len(exclusions),
        },
    }

    capsule_hash = _hash_json_value(hash_basis)
    capsule_id = f"{GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION}:{capsule_hash[:16]}"
    serialized_core = _canonical_json_text(hash_basis)
    serialized_bytes = len(serialized_core.encode("utf-8"))
    estimated_token_count = max(1, (serialized_bytes + 3) // 4)
    cache_path = GOVERNED_CONTEXT_CAPSULE_CACHE_DIR / f"{capsule_hash}.json"
    cache_status = "MISS"
    cached_core = None
    if use_cache and cache_path.exists():
        loaded_cache = load_optional_json(cache_path)
        validation_errors = validate_governed_context_capsule_payload(loaded_cache, expected_hash=capsule_hash, expected_id=capsule_id)
        if not validation_errors and isinstance(loaded_cache, dict):
            cached_core = dict(loaded_cache)
            cache_status = "HIT"

    capsule = dict(cached_core) if isinstance(cached_core, dict) else {}
    capsule["schema_id"] = GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION
    capsule["schema_version"] = GOVERNED_CONTEXT_CAPSULE_SCHEMA_RELEASE
    capsule["capsule_schema_version"] = GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION
    capsule["capsule_id"] = capsule_id
    capsule["capsule_hash"] = capsule_hash
    capsule["request_identity"] = request_identity
    capsule["current_state"] = current_state
    capsule["freshness"] = normalized_freshness
    capsule["authority"] = normalized_authority
    capsule["patch_chain"] = normalized_patch_chain
    capsule["open_debt"] = open_debt_items
    capsule["open_debt_detail"] = open_debt_detail
    capsule["relevant_artifacts"] = relevant_artifacts
    capsule["runtime_trace"] = {
        "trace_report": normalized_trace_report,
        "claim_graph_summary": claim_graph_summary,
        "database_health": database_health,
    }
    capsule["database_health"] = database_health
    capsule["recent_governance_events"] = recent_governance_events
    capsule["candidate_actions"] = candidate_actions
    capsule["exclusions"] = exclusions
    capsule["candidate_set_hash"] = candidate_set_hash
    capsule["candidate_policy_id"] = request_identity.get("candidate_policy_id")
    capsule["candidate_policy_version"] = request_identity.get("candidate_policy_version")
    capsule["canonical_routed_request"] = request_identity.get("canonical_routed_request")
    capsule["provenance"] = provenance
    capsule["warnings"] = warnings
    capsule["summary"] = hash_basis["summary"]
    capsule["capsule_schema_version"] = GOVERNED_CONTEXT_CAPSULE_SCHEMA_VERSION
    capsule["cache_status"] = cache_status
    capsule["build_time_ms"] = round((time.perf_counter() - started_at) * 1000, 3)
    capsule["serialized_bytes"] = serialized_bytes
    capsule["estimated_token_count"] = estimated_token_count
    capsule["artifact_count"] = len(relevant_artifacts)
    capsule["source_count"] = len(source_paths)
    capsule["excluded_source_count"] = len(exclusions)
    capsule["freshness_state"] = normalized_freshness.get("db_snapshot_status", "unknown")
    capsule["authority_state"] = normalized_authority.get("decision", "unknown")
    capsule["metrics"] = _build_governed_context_metrics(
        cache_status,
        capsule["build_time_ms"],
        serialized_bytes,
        estimated_token_count,
        len(relevant_artifacts),
        len(source_paths),
        len(exclusions),
    )

    if use_cache and not isinstance(cached_core, dict):
        GOVERNED_CONTEXT_CAPSULE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with cache_path.open("w", encoding="utf-8") as handle:
                json.dump(capsule, handle, ensure_ascii=False, sort_keys=True, indent=2)
        except OSError:
            capsule["cache_status"] = "MISS"
            capsule["metrics"]["cache_status"] = "MISS"

    return capsule


def build_governed_context_capsule(db_path, target=None, task=None, query=None, limit=20, use_cache=True):
    return build_governed_context_capsule_v1(
        db_path,
        target=target,
        task=task,
        query=query,
        limit=limit,
        use_cache=use_cache,
    )


def build_context_capsule_result(db_path, target=None, task=None):
    current_state = build_current_state_capsule(db_path)
    db_file = Path(db_path)
    normalized_target = normalize_repo_path(target)
    task_text = str(task).strip() if task else None
    ledger_index = load_governance_change_ledger_index()

    if normalized_target:
        authority_result = build_authority_resolution_result(argparse.Namespace(db=db_path, target=normalized_target))
        debt_result = build_debt_runtime_result(db_path, target=normalized_target, status_filter="all", current_state=current_state)
    else:
        authority_result = {
            "target": None,
            "authority_owner": current_state.get("runtime", {}).get("authority_boundary", "unknown"),
            "authority_source": None,
            "supersession": {"status": "unknown", "superseded_by": []},
            "conflict_state": current_state.get("runtime", {}).get("authority_boundary", "unknown"),
            "decision": "defer" if current_state.get("runtime", {}).get("authority_boundary") == "mixed" else "allow",
            "reason": "Authority boundary summarized from current-state.",
            "evidence_paths": current_state.get("evidence_paths", []),
            "warnings": current_state.get("warnings", []),
        }
        debt_result = build_debt_runtime_result(db_path, status_filter="all", current_state=current_state)

    patch_candidates = find_patch_candidates_for_target(normalized_target) if normalized_target else [find_latest_applied_patch_candidate()]
    patch_candidates = [candidate for candidate in patch_candidates if candidate and candidate[0]]
    patch_record = patch_candidates[0][0] if patch_candidates else None
    patch_path = patch_candidates[0][1] if patch_candidates else None
    if patch_record is None and current_state.get("latest_decisions"):
        latest_patch_id = current_state["latest_decisions"][0].get("patch_id")
        if latest_patch_id:
            patch_record, patch_path = load_patch_record_by_id(latest_patch_id)

    if isinstance(patch_record, dict) and patch_record.get("patch_id"):
        patch_chain = build_patch_chain_result(
            patch_record["patch_id"],
            current_state=current_state,
            ledger_index=ledger_index,
        )
    else:
        patch_chain = {
            "patch_id": None,
            "status": "unknown",
            "dependencies": [],
            "missing_dependencies": [],
            "supersession": {"status": "unknown", "superseded_by": []},
            "late_registration": "unknown",
            "blockers": [],
            "decision": "defer",
            "reason": "No patch context is available.",
            "evidence_paths": [],
            "warnings": [],
        }

    debt_ids = [record.get("debt_id") for record in debt_result.get("debts", []) if record.get("debt_id")]
    blocking_items = _dedupe_trim(
        list(current_state.get("blockers", []))
        + list(patch_chain.get("blockers", []))
        + [f"debt_blocked:{record.get('debt_id')}" for record in debt_result.get("debts", []) if str(record.get("decision_effect", "")).lower() == "block"]
    )
    defer_items = _dedupe_trim(
        list(patch_chain.get("warnings", []))
        + list(authority_result.get("warnings", []))
        + list(debt_result.get("warnings", [])),
        limit=3,
    )
    warnings = _dedupe_trim(
        list(current_state.get("warnings", []))
        + list(authority_result.get("warnings", []))
        + list(patch_chain.get("warnings", []))
        + list(debt_result.get("warnings", [])),
        limit=4,
    )

    snapshot_state = "unknown"
    global_runtime_status = {
        "status": current_state.get("status", "unknown"),
        "health": current_state.get("health", {}).get("global_validation", "unknown"),
        "db_first_gate": current_state.get("runtime", {}).get("db_first_gate", "unknown"),
        "authority_boundary": current_state.get("runtime", {}).get("authority_boundary", "unknown"),
        "snapshot": snapshot_state,
    }

    freshness_state = current_state.get("freshness", {})
    freshness_summary = {
        "db_snapshot_status": freshness_state.get("db_snapshot_status", "unknown"),
        "decision": freshness_state.get("decision", "block"),
        "indexed_at": freshness_state.get("indexed_at"),
        "latest_known_worktree_change": freshness_state.get("latest_known_worktree_change"),
        "latest_runtime_only_worktree_change": freshness_state.get("latest_runtime_only_worktree_change"),
        "source_worktree_marker": freshness_state.get("source_worktree_marker"),
        "runtime_worktree_marker": freshness_state.get("runtime_worktree_marker"),
        "change_basis": freshness_state.get("change_basis", "unknown"),
        "staleness_cause": freshness_state.get("staleness_cause", "unknown"),
        "source_change_count": freshness_state.get("source_change_count", 0),
        "runtime_only_change_count": freshness_state.get("runtime_only_change_count", 0),
    }
    global_runtime_status["snapshot"] = freshness_summary["db_snapshot_status"]

    authority_summary = {
        "target": authority_result.get("target"),
        "owner": authority_result.get("authority_owner", "unknown"),
        "source": authority_result.get("authority_source"),
        "decision": authority_result.get("decision", "defer"),
        "conflict": authority_result.get("conflict_state", "unknown"),
    }

    patch_summary = {
        "patch_id": patch_chain.get("patch_id"),
        "status": patch_chain.get("status", "unknown"),
        "decision": patch_chain.get("decision", "defer"),
        "dependencies": len(patch_chain.get("dependencies", [])),
        "missing_dependencies": len(patch_chain.get("missing_dependencies", [])),
        "blockers": _dedupe_trim(patch_chain.get("blockers", []), limit=2),
    }

    debt_summary = {
        "open": debt_result.get("summary", {}).get("open", 0),
        "partial": debt_result.get("summary", {}).get("partial", 0),
        "resolved": debt_result.get("summary", {}).get("resolved", 0),
        "blocking": debt_result.get("summary", {}).get("blocking", 0),
        "items": debt_ids[:3],
        "decision": debt_result.get("decision", "allow"),
    }

    replay_projection = current_state.get("projection", {}).get("replay_reconciliation", {}) if isinstance(current_state.get("projection"), dict) else {}
    replay_summary = {
        "state": replay_projection.get("projection_state", current_state.get("runtime", {}).get("replay_reconciliation_state", "unknown")),
        "boundary": replay_projection.get("boundary_state", current_state.get("runtime", {}).get("replay_reconciliation_boundary_state", "unknown")),
        "coverage_state": replay_projection.get("coverage_state", current_state.get("runtime", {}).get("replay_reconciliation_coverage_state", "unknown")),
        "subject_count": replay_projection.get("subject_count", current_state.get("runtime", {}).get("replay_reconciliation_subject_count", 0)),
        "event_count": replay_projection.get("event_count", current_state.get("runtime", {}).get("replay_reconciliation_event_count", 0)),
        "latest_subject_id": replay_projection.get("latest_subject_id", current_state.get("runtime", {}).get("replay_reconciliation_latest_subject_id")),
        "latest_subject_type": replay_projection.get("latest_subject_type", current_state.get("runtime", {}).get("replay_reconciliation_latest_subject_type")),
        "latest_event_id": replay_projection.get("latest_event_id", current_state.get("runtime", {}).get("replay_reconciliation_latest_event_id")),
        "latest_event_type": replay_projection.get("latest_event_type", current_state.get("runtime", {}).get("replay_reconciliation_latest_event_type")),
        "latest_source_patch_id": replay_projection.get("latest_source_patch_id", current_state.get("runtime", {}).get("replay_reconciliation_latest_source_patch_id")),
        "latest_source_path": replay_projection.get("latest_source_path", current_state.get("runtime", {}).get("replay_reconciliation_latest_source_path")),
        "latest_created_at": replay_projection.get("latest_created_at", current_state.get("runtime", {}).get("replay_reconciliation_latest_created_at")),
    }

    semantic_targets = collect_patch_semantic_targets(patch_record or {}) if isinstance(patch_record, dict) else []
    semantic_summary = None
    semantic_evidence_paths = []
    if semantic_targets:
        semantic_summary = build_semantic_authority_summary(db_path, semantic_targets, current_state=current_state)
        warnings = _dedupe_trim(
            list(warnings) + list(semantic_summary.get("warnings", [])),
            limit=4,
        )
        semantic_evidence_paths = semantic_summary.get("evidence_paths", [])

    if blocking_items:
        recommended_next_action = "Resolve blockers before applying the governed action."
    elif patch_summary.get("status") == "applied":
        recommended_next_action = "No patch application is needed; address the remaining partial runtime debt."
    elif normalized_target:
        recommended_next_action = "Use patch-gate for the target if a change is still required."
    else:
        recommended_next_action = "Use the capsule to choose the next governed action."

    evidence_paths = [
        str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        str(CURRENT_STATE_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(AUTHORITY_RESOLUTION_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(PATCH_CHAIN_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(DEBT_RUNTIME_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(EVENT_BUS_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(EVENT_REPLAY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(EVENT_RECONCILIATION_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(CONTEXT_CAPSULE_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(FRESHNESS_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(SNAPSHOT_REFRESH_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(REFRESH_STABILITY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        str(SEMANTIC_AUTHORITY_MIGRATION.relative_to(ROOT)).replace("\\", "/") if SEMANTIC_AUTHORITY_MIGRATION.exists() else None,
    ]
    if patch_path:
        evidence_paths.insert(0, str(patch_path.relative_to(ROOT)).replace("\\", "/"))
    if normalized_target:
        evidence_paths.append(normalized_target)
    evidence_paths.extend(debt_result.get("evidence_paths", []))
    evidence_paths.extend(replay_projection.get("evidence_paths", []))
    if semantic_evidence_paths:
        evidence_paths.extend(semantic_evidence_paths)
    evidence_paths = _dedupe_trim(evidence_paths, limit=15)

    result = {
        "target": normalized_target,
        "task": task_text,
        "global_runtime_status": global_runtime_status,
        "freshness_summary": freshness_summary,
        "authority_summary": authority_summary,
        "patch_summary": patch_summary,
        "blocking_summary": {
            "count": len(blocking_items),
            "items": blocking_items[:3],
            "defer": defer_items,
        },
        "debt_summary": debt_summary,
        "replay_summary": replay_summary,
        "warnings": warnings,
        "required_validators": [
            "current-state",
            "freshness",
            "authority",
            "patch-chain",
            "debt",
            "patch-gate",
        ],
        "recommended_next_action": recommended_next_action,
        "minimal_evidence_paths": evidence_paths,
    }
    if semantic_summary is not None:
        result["semantic_authority_summary"] = semantic_summary

    recent_events = load_recent_governance_events(db_path, limit=1)
    if recent_events:
        result["recent_governance_events"] = recent_events

    if not result["target"]:
        result.pop("target")
    if not result["task"]:
        result.pop("task")
    if current_state.get("status") == "unavailable":
        result["global_runtime_status"]["status"] = "unavailable"
        result["recommended_next_action"] = "Open the DB runtime first."
    return result


def load_authority_resolution_catalog(conn):
    try:
        rows = conn.execute("SELECT * FROM authority_resolution_view").fetchall()
    except sqlite3.Error:
        return []
    return [dict(row) for row in rows]


def load_semantic_authority_registry_records():
    registry = load_optional_json(SEMANTIC_AUTHORITY_REGISTRY)
    if not isinstance(registry, dict):
        return []

    entries = registry.get("semantic_targets")
    if not isinstance(entries, list):
        entries = registry.get("entries")
    if not isinstance(entries, list):
        entries = registry.get("records")
    if not isinstance(entries, list):
        entries = []

    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        normalized.append(
            {
                "semantic_key": entry.get("semantic_key") or entry.get("key"),
                "semantic_type": entry.get("semantic_type") or entry.get("type"),
                "authority_source": normalize_repo_path(entry.get("authority_source"))
                or str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
                "authority_rank": entry.get("authority_rank"),
                "supersedes": entry.get("supersedes"),
                "status": entry.get("status"),
                "notes": entry.get("notes"),
                "canonical_expression": entry.get("canonical_expression"),
            }
        )
    return normalized


def load_semantic_authority_catalog(conn):
    rows = []
    try:
        rows = conn.execute("SELECT * FROM semantic_authority_view").fetchall()
    except sqlite3.Error:
        try:
            rows = conn.execute("SELECT * FROM semantic_authority_map").fetchall()
        except sqlite3.Error:
            rows = []
    if rows:
        return [dict(row) for row in rows]
    return load_semantic_authority_registry_records()


def load_claim_registry_records():
    registry = load_optional_json(CLAIM_REGISTRY)
    if not isinstance(registry, dict):
        return []

    entries = registry.get("claims")
    if not isinstance(entries, list):
        return []

    records = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        evidence_paths = [
            normalize_repo_path(path)
            for path in parse_json_collection(entry.get("evidence_paths"))
            if normalize_repo_path(path)
        ]
        records.append(
            {
                "claim_id": str(entry.get("claim_id") or entry.get("source_claim_id") or "").strip() or None,
                "source_claim_id": str(entry.get("source_claim_id") or "").strip() or None,
                "title": entry.get("title"),
                "claim_statement": entry.get("claim_statement"),
                "status": entry.get("status"),
                "claim_type": entry.get("claim_type"),
                "classification": entry.get("classification"),
                "model_class": entry.get("model_class"),
                "models_used": parse_json_collection(entry.get("models_used")),
                "model_classes": parse_json_collection(entry.get("model_classes")),
                "seeds_used": entry.get("seeds_used"),
                "falsification_run": bool(entry.get("falsification_run")),
                "evidence_paths": evidence_paths,
                "paper_path": normalize_repo_path(entry.get("paper_path")),
                "last_updated": entry.get("last_updated"),
            }
        )
    return records


def load_claim_support_matrix_records():
    registry = load_optional_json(CLAIM_SUPPORT_MATRIX)
    if not isinstance(registry, dict):
        return []

    entries = registry.get("claims")
    if not isinstance(entries, list):
        return []

    records = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        records.append(
            {
                "claim_id": str(entry.get("claim_id") or "").strip() or None,
                "claim_text": entry.get("claim_text"),
                "claim_class": entry.get("claim_class"),
                "claim_status": entry.get("claim_status"),
                "required_lemmas": parse_json_collection(entry.get("required_lemmas")),
                "required_proofs": parse_json_collection(entry.get("required_proofs")),
                "required_operators": parse_json_collection(entry.get("required_operators")),
                "required_law_chains": parse_json_collection(entry.get("required_law_chains")),
                "required_simulation_bindings": parse_json_collection(entry.get("required_simulation_bindings")),
                "minimum_tool_rigor_endorsement": entry.get("minimum_tool_rigor endorsement")
                or entry.get("minimum_tool_rigor_endorsement"),
                "provenance_requirement": entry.get("provenance_requirement"),
                "publication_allowed": bool(entry.get("publication_allowed")),
            }
        )
    return records


def build_semantic_authority_graph_projection(catalog_rows, current_state=None):
    records = [dict(row) for row in catalog_rows or [] if isinstance(row, (dict, sqlite3.Row))]
    nodes = []
    edges = []
    status_counts = {}
    rank_counts = {}
    evidence_paths = [
        str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
        str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
    ]
    if SEMANTIC_AUTHORITY_MIGRATION.exists():
        evidence_paths.append(str(SEMANTIC_AUTHORITY_MIGRATION.relative_to(ROOT)).replace("\\", "/"))

    for record in records:
        semantic_key = str(record.get("semantic_key") or record.get("key") or "").strip()
        semantic_type = str(record.get("semantic_type") or record.get("type") or "").strip() or None
        status = normalize_semantic_authority_status(record.get("status"))
        authority_rank = normalize_semantic_authority_rank(record.get("authority_rank"))
        node = {
            "semantic_key": semantic_key,
            "semantic_type": semantic_type,
            "authority_source": normalize_repo_path(record.get("authority_source"))
            or str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            "authority_rank": authority_rank,
            "status": status,
            "canonical_expression": record.get("canonical_expression"),
        }
        nodes.append(node)
        status_counts[status] = status_counts.get(status, 0) + 1
        rank_counts[authority_rank] = rank_counts.get(authority_rank, 0) + 1

        supersedes = normalize_repo_path(record.get("supersedes"))
        if supersedes:
            edges.append(
                {
                    "from": supersedes,
                    "to": semantic_key,
                    "type": "supersedes",
                    "status": status,
                }
            )

    authority_sources = [
        source
        for source in dict.fromkeys(node.get("authority_source") for node in nodes if node.get("authority_source"))
    ]
    return {
        "projection_state": "projected" if nodes else "empty",
        "semantic_authority_count": len(nodes),
        "active_count": status_counts.get("active", 0),
        "canonical_count": rank_counts.get("canonical", 0),
        "primary_count": rank_counts.get("primary", 0),
        "status_counts": status_counts,
        "rank_counts": rank_counts,
        "authority_sources": authority_sources,
        "nodes": nodes,
        "edges": edges,
        "evidence_paths": [path for path in dict.fromkeys(path for path in evidence_paths if path)],
        "coverage_state": current_state.get("coverage_state", "unknown") if current_state else "unknown",
    }


def build_claim_reasoning_projection(conn, current_state=None, claim_registry_records=None, claim_support_records=None):
    claim_records = [record for record in (claim_registry_records or load_claim_registry_records()) if isinstance(record, dict)]
    support_records = [record for record in (claim_support_records or load_claim_support_matrix_records()) if isinstance(record, dict)]

    db_claim_count = 0
    db_link_count = 0
    db_link_rows = []
    db_state = "unavailable"
    try:
        db_claim_count = int(
            conn.execute("SELECT COUNT(DISTINCT claim_id) FROM claim_evidence_links").fetchone()[0] or 0
        )
        db_link_count = int(conn.execute("SELECT COUNT(*) FROM claim_evidence_links").fetchone()[0] or 0)
        link_rows = conn.execute(
            """
            SELECT claim_id, source_path, orientation_status
            FROM claim_evidence_links
            ORDER BY claim_id, source_path
            LIMIT 10
            """
        ).fetchall()
        db_link_rows = [dict(row) for row in link_rows]
        db_state = "projected" if db_link_count > 0 else "empty"
    except sqlite3.Error:
        db_state = "unavailable"

    claim_status_counts = {}
    claim_classification_counts = {}
    claim_type_counts = {}
    claims_with_evidence = 0
    claims_with_paper = 0
    sample_claims = []
    for record in claim_records:
        status = str(record.get("status") or "unknown").strip() or "unknown"
        classification = str(record.get("classification") or "unknown").strip() or "unknown"
        claim_type = str(record.get("claim_type") or "unknown").strip() or "unknown"
        claim_status_counts[status] = claim_status_counts.get(status, 0) + 1
        claim_classification_counts[classification] = claim_classification_counts.get(classification, 0) + 1
        claim_type_counts[claim_type] = claim_type_counts.get(claim_type, 0) + 1
        if record.get("evidence_paths"):
            claims_with_evidence += 1
        if record.get("paper_path"):
            claims_with_paper += 1
        if len(sample_claims) < 5:
            sample_claims.append(
                {
                    "claim_id": record.get("claim_id"),
                    "title": record.get("title"),
                    "status": status,
                    "classification": classification,
                    "evidence_paths": record.get("evidence_paths", []),
                }
            )

    support_status_counts = {}
    support_class_counts = {}
    publication_allowed_count = 0
    required_lemma_total = 0
    required_proof_total = 0
    required_operator_total = 0
    required_law_chain_total = 0
    required_simulation_binding_total = 0
    for record in support_records:
        support_status = str(record.get("claim_status") or "unknown").strip() or "unknown"
        support_class = str(record.get("claim_class") or "unknown").strip() or "unknown"
        support_status_counts[support_status] = support_status_counts.get(support_status, 0) + 1
        support_class_counts[support_class] = support_class_counts.get(support_class, 0) + 1
        if record.get("publication_allowed"):
            publication_allowed_count += 1
        required_lemma_total += len(record.get("required_lemmas", []))
        required_proof_total += len(record.get("required_proofs", []))
        required_operator_total += len(record.get("required_operators", []))
        required_law_chain_total += len(record.get("required_law_chains", []))
        required_simulation_binding_total += len(record.get("required_simulation_bindings", []))

    return {
        "projection_state": "projected" if claim_records or support_records else "empty",
        "registry": {
            "claim_count": len(claim_records),
            "status_counts": claim_status_counts,
            "classification_counts": claim_classification_counts,
            "claim_type_counts": claim_type_counts,
            "claims_with_evidence_paths": claims_with_evidence,
            "claims_with_paper_paths": claims_with_paper,
            "sample_claims": sample_claims,
            "registry_path": str(CLAIM_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
        },
        "support_matrix": {
            "claim_count": len(support_records),
            "claim_status_counts": support_status_counts,
            "claim_class_counts": support_class_counts,
            "publication_allowed_count": publication_allowed_count,
            "required_lemma_total": required_lemma_total,
            "required_proof_total": required_proof_total,
            "required_operator_total": required_operator_total,
            "required_law_chain_total": required_law_chain_total,
            "required_simulation_binding_total": required_simulation_binding_total,
            "matrix_path": str(CLAIM_SUPPORT_MATRIX.relative_to(ROOT)).replace("\\", "/"),
        },
        "db_links": {
            "claim_count": db_claim_count,
            "link_count": db_link_count,
            "state": db_state,
            "sample_links": db_link_rows,
        },
        "reason": (
            "Claim registry and support matrix provide the governed claim summary; "
            "DB claim-evidence links are empty."
            if db_state == "empty"
            else "Claim registry and support matrix provide the governed claim summary; DB claim-evidence links are projected."
            if db_state == "projected"
            else "Claim registry and support matrix provide the governed claim summary; DB claim-evidence links are unavailable."
        ),
        "evidence_paths": [
            path
            for path in dict.fromkeys(
                path
                for path in [
                    str(CLAIM_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
                    str(CLAIM_SUPPORT_MATRIX.relative_to(ROOT)).replace("\\", "/"),
                    str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
                ]
                if path
            )
        ],
        "coverage_state": current_state.get("coverage_state", "unknown") if current_state else "unknown",
    }


def load_governance_change_ledger_index():
    ledger = load_optional_json(GOVERNANCE_CHANGE_LEDGER)
    if not isinstance(ledger, dict):
        return {}

    index = {}
    for entry in ledger.get("entries", []):
        if not isinstance(entry, dict):
            continue
        patch_id = entry.get("patch_id")
        if patch_id and patch_id not in index:
            index[patch_id] = entry
    return index


def load_patch_record_by_id(patch_id):
    patch_path = PATCH_REGISTRY_DIR / f"{patch_id}.json"
    if not patch_path.exists():
        fallback_path = ROOT / "patches" / f"{patch_id}.json"
        if not fallback_path.exists():
            return None, patch_path
        patch_path = fallback_path
    try:
        return load_json(patch_path), patch_path
    except (OSError, json.JSONDecodeError):
        return None, patch_path


def load_patch_record_by_path(patch_path):
    path = Path(patch_path)
    if not path.exists():
        return None, path
    try:
        return load_json(path), path
    except (OSError, json.JSONDecodeError):
        return None, path


def normalize_patch_chain_status(raw_status):
    status = str(raw_status or "").strip().lower()
    if status in {"applied", "approved"}:
        return "applied"
    if status in {"partial", "partially_applied", "implemented", "in_progress"}:
        return "partial"
    if status in {"registered_late", "late_registered"}:
        return "late_registered"
    if status in {"superseded", "replaced"}:
        return "superseded"
    if status in {"blocked", "blocked_pending_dependency"}:
        return "blocked"
    if status in {"missing"}:
        return "missing"
    if status in {"active", "ready", "scheduled", "proposed", "provisional", "registered"}:
        return "active"
    return "unknown"


PATCH_DEPENDENCY_TYPES = {
    "REQUIRES_COMPLETED_PREDECESSOR",
    "REQUIRES_EXISTING_EVIDENCE",
    "REQUIRES_SEMANTIC_RULE",
    "HISTORICAL_LINEAGE_ONLY",
}


def normalize_patch_dependency_type(raw_value):
    text = str(raw_value or "").strip().upper()
    if text in PATCH_DEPENDENCY_TYPES:
        return text
    return "REQUIRES_COMPLETED_PREDECESSOR"


def collect_patch_dependency_requirements(patch_record):
    dependencies = [
        str(dep).strip()
        for dep in parse_json_collection(patch_record.get("depends_on", []))
        if str(dep).strip()
    ]
    raw_requirements = patch_record.get("dependency_requirements") or patch_record.get("dependency_types") or {}
    requirement_map = {}
    if isinstance(raw_requirements, dict):
        for dep_id in dependencies:
            raw_entry = raw_requirements.get(dep_id)
            if isinstance(raw_entry, str):
                requirement_map[dep_id] = {"type": normalize_patch_dependency_type(raw_entry)}
            elif isinstance(raw_entry, dict):
                normalized = dict(raw_entry)
                normalized["type"] = normalize_patch_dependency_type(raw_entry.get("type"))
                requirement_map[dep_id] = normalized
    for dep_id in dependencies:
        requirement_map.setdefault(dep_id, {"type": "REQUIRES_COMPLETED_PREDECESSOR"})
    return requirement_map


def dependency_requirement_is_satisfied(dep_result, requirement):
    requirement_type = normalize_patch_dependency_type(requirement.get("type"))
    dep_status = str(dep_result.get("status") or "").strip().lower()
    dep_decision = str(dep_result.get("decision") or "").strip().lower()

    if requirement_type == "HISTORICAL_LINEAGE_ONLY":
        return True
    if requirement_type == "REQUIRES_COMPLETED_PREDECESSOR":
        return dep_status == "applied"
    if requirement_type == "REQUIRES_EXISTING_EVIDENCE":
        return dep_status not in {"missing", "superseded"}
    if requirement_type == "REQUIRES_SEMANTIC_RULE":
        semantic_rule_id = str(requirement.get("semantic_rule_id") or "").strip()
        semantic_authority = str(requirement.get("semantic_authority") or "").strip()
        if not semantic_rule_id and not semantic_authority:
            return False
        if dep_status in {"missing", "superseded"}:
            return False
        if dep_decision == "block" and dep_status in {"missing", "superseded"}:
            return False
        return True
    return dep_status == "applied"


def build_patch_chain_result(patch_id, current_state=None, ledger_index=None, cache=None, trail=None):
    if cache is None:
        cache = {}
    if trail is None:
        trail = []
    normalized_patch_id = str(patch_id or "").strip()
    if normalized_patch_id in cache:
        return cache[normalized_patch_id]

    ledger_index = ledger_index or load_governance_change_ledger_index()
    ledger_entry = ledger_index.get(normalized_patch_id)
    patch_record, patch_path = load_patch_record_by_id(normalized_patch_id)

    base_result = {
        "patch_id": normalized_patch_id or None,
        "status": "unknown",
        "dependencies": [],
        "missing_dependencies": [],
        "supersession": {"status": "unknown", "superseded_by": []},
        "late_registration": "unknown",
        "blockers": [],
        "decision": "defer",
        "reason": "Patch chain resolution is unavailable.",
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        ],
        "warnings": [],
    }

    if not normalized_patch_id:
        base_result["status"] = "missing"
        base_result["decision"] = "block"
        base_result["reason"] = "Patch ID is required for patch-chain resolution."
        cache[normalized_patch_id] = base_result
        return base_result

    if normalized_patch_id in trail:
        base_result.update(
            {
                "status": "blocked",
                "decision": "block",
                "reason": "Dependency cycle detected in patch chain.",
                "blockers": ["dependency_cycle_detected"],
                "warnings": ["Patch dependency traversal re-entered a previously visited patch."],
                "evidence_paths": [str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/")],
            }
        )
        cache[normalized_patch_id] = base_result
        return base_result

    if patch_record is None:
        base_result["status"] = "missing"
        base_result["decision"] = "block"
        base_result["reason"] = "Patch registry record is missing."
        base_result["blockers"] = ["missing_patch_record"]
        if ledger_entry:
            base_result["warnings"].append("Change ledger references the patch, but the registry record is missing.")
            base_result["evidence_paths"].extend(
                [
                    str(GOVERNANCE_CHANGE_LEDGER.relative_to(ROOT)).replace("\\", "/"),
                ]
            )
            diff_report = ledger_entry.get("diff_report")
            if diff_report:
                base_result["evidence_paths"].append(normalize_repo_path(diff_report) or diff_report)
        cache[normalized_patch_id] = base_result
        return base_result

    patch_status = normalize_patch_chain_status(patch_record.get("status"))
    dependencies = [
        str(dep).strip()
        for dep in patch_record.get("depends_on", [])
        if str(dep).strip()
    ]
    dependency_requirements = collect_patch_dependency_requirements(patch_record)
    dependency_results = [
        build_patch_chain_result(
            dep_id,
            current_state=current_state,
            ledger_index=ledger_index,
            cache=cache,
            trail=trail + [normalized_patch_id],
        )
        for dep_id in dependencies
    ]

    dependency_evaluation = []
    for dep_id, dep_result in zip(dependencies, dependency_results):
        requirement = dependency_requirements.get(dep_id, {"type": "REQUIRES_COMPLETED_PREDECESSOR"})
        requirement_type = normalize_patch_dependency_type(requirement.get("type"))
        satisfied = dependency_requirement_is_satisfied(dep_result, requirement)
        dependency_evaluation.append(
            {
                "patch_id": dep_id,
                "requirement_type": requirement_type,
                "satisfied": satisfied,
                "dependency_status": dep_result.get("status"),
                "dependency_decision": dep_result.get("decision"),
            }
        )

    missing_dependencies = [
        dep_id
        for dep_id, dep_result, evaluation in zip(dependencies, dependency_results, dependency_evaluation)
        if evaluation.get("requirement_type") != "HISTORICAL_LINEAGE_ONLY"
        and dep_result.get("status") == "missing"
    ]
    unresolved_dependencies = [
        dep_id
        for dep_id, evaluation in zip(dependencies, dependency_evaluation)
        if not evaluation.get("satisfied")
    ]
    late_dependencies = [
        dep_id
        for dep_id, dep_result, evaluation in zip(dependencies, dependency_results, dependency_evaluation)
        if evaluation.get("requirement_type") == "REQUIRES_COMPLETED_PREDECESSOR"
        and dep_result.get("status") == "late_registered"
    ]
    superseded_dependencies = [
        dep_id
        for dep_id, dep_result, evaluation in zip(dependencies, dependency_results, dependency_evaluation)
        if evaluation.get("requirement_type") != "HISTORICAL_LINEAGE_ONLY"
        and dep_result.get("status") == "superseded"
    ]

    blockers = []
    warnings = []
    if current_state and current_state.get("warnings"):
        warnings.extend(current_state["warnings"])

    if patch_record.get("status") and patch_status == "unknown":
        warnings.append(f"Patch status '{patch_record.get('status')}' is not normalized.")

    superseded_by = parse_json_collection(
        patch_record.get("superseded_by")
        or patch_record.get("replaced_by")
        or patch_record.get("supersedes")
    )
    supersession_status = "superseded" if patch_status == "superseded" or superseded_by else "current"

    late_registration = "true" if patch_status == "late_registered" else "false"

    if patch_status == "missing":
        blockers.append("missing_patch_record")
    if patch_status == "superseded":
        blockers.append("superseded_patch")
    if patch_status == "blocked":
        blockers.append("blocked_patch_record")

    if missing_dependencies:
        blockers.append("missing_required_dependency")
    if late_dependencies:
        blockers.append("late_registered_dependency")
    if superseded_dependencies:
        blockers.append("superseded_dependency")
    if unresolved_dependencies and patch_status not in {"applied", "late_registered"}:
        blockers.append("dependency_chain_not_satisfied")

    evidence_paths = [
        str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        str(GOVERNANCE_CHANGE_LEDGER.relative_to(ROOT)).replace("\\", "/"),
    ]
    if patch_path.exists():
        evidence_paths.append(str(patch_path.relative_to(ROOT)).replace("\\", "/"))
    diff_report = ledger_entry.get("diff_report") if ledger_entry else None
    if diff_report:
        evidence_paths.append(normalize_repo_path(diff_report) or diff_report)
    if PATCH_CHAIN_MIGRATION.exists():
        evidence_paths.append(str(PATCH_CHAIN_MIGRATION.relative_to(ROOT)).replace("\\", "/"))
    for dep_result in dependency_results:
        for path in dep_result.get("evidence_paths", []):
            evidence_paths.append(path)

    evidence_paths = [path for path in dict.fromkeys(path for path in evidence_paths if path)]

    if patch_status == "applied":
        decision = "defer"
        reason = "Patch is already applied."
        status = "applied"
    elif patch_status == "late_registered":
        decision = "defer"
        reason = "Patch is late-registered and requires provenance repair rather than re-application."
        status = "late_registered"
    elif patch_status == "superseded":
        decision = "block"
        reason = "Patch is superseded by another patch."
        status = "superseded"
    elif patch_status == "blocked":
        decision = "block"
        reason = "Patch record is blocked."
        status = "blocked"
    elif patch_status == "partial":
        decision = "defer"
        reason = "Patch is registered as partial or transitional evidence."
        status = "partial"
    elif blockers:
        decision = "block"
        reason = "Dependency chain is not yet satisfied."
        status = "blocked"
    elif patch_status == "missing":
        decision = "block"
        reason = "Patch registry record is missing."
        status = "missing"
    elif patch_status == "active":
        decision = "allow"
        reason = "Patch chain is satisfied."
        status = "active"
    else:
        decision = "defer"
        reason = "Patch chain state is deferred pending additional runtime evidence."
        status = patch_status or "unknown"

    result = {
        "patch_id": normalized_patch_id,
        "status": status,
        "dependencies": dependencies,
        "dependency_evaluation": dependency_evaluation,
        "missing_dependencies": missing_dependencies,
        "supersession": {
            "status": supersession_status,
            "superseded_by": [normalize_repo_path(item) for item in superseded_by if normalize_repo_path(item)],
        },
        "late_registration": late_registration,
        "blockers": [blocker for blocker in dict.fromkeys(blockers) if blocker],
        "decision": decision,
        "reason": reason,
        "evidence_paths": evidence_paths,
        "warnings": [warning for warning in dict.fromkeys(warnings) if warning],
    }

    if dependency_results:
        result["dependency_results"] = dependency_results

    cache[normalized_patch_id] = result
    return result


def collect_patch_target_paths(patch):
    paths = []
    for key in ("target_files", "required_changes", "files", "creates", "updated_artifacts"):
        entries = patch.get(key)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict):
                path = entry.get("path") or entry.get("file")
                if path:
                    paths.append(normalize_repo_path(path))
            elif isinstance(entry, str):
                paths.append(normalize_repo_path(entry))
    return [path for path in dict.fromkeys(paths) if path]


def build_authority_resolution_record(target, current_state=None, catalog_rows=None):
    normalized_target = normalize_repo_path(target)
    if not normalized_target:
        return {
            "target": None,
            "authority_owner": "unknown",
            "authority_source": None,
            "supersession": {"status": "unavailable", "superseded_by": []},
            "conflict_state": "unavailable",
            "decision": "defer",
            "reason": "Authority resolution requires a target surface.",
            "evidence_paths": [
                str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            ],
            "warnings": ["No target surface was supplied."],
            "source": "unavailable",
        }

    match = None
    for row in catalog_rows or []:
        pattern = normalize_repo_path(row.get("target_pattern") or row.get("target") or row.get("surface"))
        if not pattern:
            continue
        if normalized_target == pattern or fnmatch(normalized_target, pattern):
            match = row
            break

    if match is None:
        match = classify_authority_target(normalized_target)
        source = "fallback_classification"
    else:
        source = "authority_resolution_view"

    authority_source = normalize_repo_path(match.get("authority_source")) or normalized_target
    superseded_by = parse_json_collection(match.get("superseded_by"))
    evidence_paths = parse_json_collection(match.get("evidence_paths"))
    warnings = parse_json_collection(match.get("warnings"))

    if current_state and current_state.get("warnings"):
        warnings.extend(current_state["warnings"])
    if current_state and current_state.get("status") == "warn":
        warnings.append("Current-state capsule reports warnings.")

    if AUTHORITY_RESOLUTION_MIGRATION.exists():
        evidence_paths.append(str(AUTHORITY_RESOLUTION_MIGRATION.relative_to(ROOT)).replace("\\", "/"))
    if CURRENT_STATE_MIGRATION.exists():
        evidence_paths.append(str(CURRENT_STATE_MIGRATION.relative_to(ROOT)).replace("\\", "/"))
    evidence_paths.append(str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"))
    evidence_paths.append(normalized_target)

    return {
        "target": normalized_target,
        "authority_owner": match.get("authority_owner", "unknown"),
        "authority_source": authority_source,
        "supersession": {
            "status": match.get("supersession_status", "unknown"),
            "superseded_by": [normalize_repo_path(item) for item in superseded_by if normalize_repo_path(item)],
        },
        "conflict_state": match.get("conflict_state", "unavailable"),
        "decision": match.get("decision", "defer"),
        "reason": match.get("reason", "Authority resolution is unavailable."),
        "evidence_paths": [path for path in dict.fromkeys(path for path in evidence_paths if path)],
        "warnings": [warning for warning in dict.fromkeys(warnings) if warning],
        "source": source,
    }


def classify_authority_target(target):
    normalized_target = normalize_repo_path(target)
    if not normalized_target:
        return {
            "authority_owner": "unknown",
            "authority_source": None,
            "supersession_status": "unavailable",
            "superseded_by": [],
            "conflict_state": "unavailable",
            "decision": "defer",
            "reason": "Authority resolution requires a target surface.",
            "evidence_paths": [],
            "warnings": [],
        }

    proposal_candidate_patch = classify_patch_record_lifecycle(normalized_target)
    if proposal_candidate_patch is not None:
        lifecycle_class = proposal_candidate_patch["lifecycle_class"].lower()
        status = proposal_candidate_patch["status"]
        return {
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "mixed",
            "decision": "defer",
            "reason": (
                f"Explicit {lifecycle_class} patch records are preserved and queryable but are not eligible for live authority lookup "
                "without a governed lifecycle transition."
            ),
            "evidence_paths": [
                normalized_target,
                "registry/governance_change_ledger.json",
                "registry/research_debt_registry.json",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [
                f"Patch record status '{status}' is proposal/candidate state and cannot participate as live authority.",
            ],
        }

    executed_pass_boundary = classify_patch_record_executed_pass_boundary(normalized_target)
    if executed_pass_boundary is not None:
        status = executed_pass_boundary["status"]
        return {
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "mixed",
            "decision": "defer",
            "reason": (
                "Executed or PASS proposal patch records are preserved and queryable but are not eligible for live authority lookup "
                "without an explicit governed lifecycle transition."
            ),
            "evidence_paths": [
                normalized_target,
                "registry/governance_change_ledger.json",
                "registry/research_debt_registry.json",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [
                f"Patch record status '{status}' represents process execution or validation state only and does not constitute a lifecycle transition or live authority grant.",
            ],
        }

    explicit_none_authority_effect_patch = classify_patch_record_explicit_none_authority_effect(normalized_target)
    if explicit_none_authority_effect_patch is not None:
        status = explicit_none_authority_effect_patch.get("status")
        return {
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "mixed",
            "decision": "defer",
            "reason": (
                "Patch record explicitly declares authority_effect=NONE and therefore cannot participate as live authority lookup. "
                "Referenced or associated surfaces may remain independently governed under their own roles."
            ),
            "evidence_paths": [
                normalized_target,
                "registry/governance_change_ledger.json",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [
                f"Patch record status '{status}' does not override explicit authority_effect=NONE.",
            ],
        }

    closeout_work_package_patch = classify_patch_record_closeout_work_package(normalized_target)
    if closeout_work_package_patch is not None:
        status = closeout_work_package_patch.get("status")
        return {
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "mixed",
            "decision": "defer",
            "reason": (
                "Closeout/work-package patch records that aggregate predecessor verification and accounting evidence are not eligible "
                "for live authority lookup. Independently governed predecessor and implementation surfaces remain queryable under their own roles."
            ),
            "evidence_paths": [
                normalized_target,
                "reports/inference-conservation-final-audit.json",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [
                f"Patch record status '{status}' is preserved for closeout, history, rollback, and accounting purposes only.",
            ],
        }

    deterministic_routing_patch = classify_patch_record_deterministic_routing_component(normalized_target)
    if deterministic_routing_patch is not None:
        status = deterministic_routing_patch.get("status")
        return {
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "mixed",
            "decision": "defer",
            "reason": (
                "Deterministic routing component patch records that aggregate codebase-specific implementation and validation evidence "
                "are not eligible for live authority lookup. Independently governed predecessor, implementation, and runtime surfaces "
                "remain queryable under their own roles."
            ),
            "evidence_paths": [
                normalized_target,
                "registry/governance_change_ledger.json",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [
                f"Patch record status '{status}' is preserved for implementation, verification, and trace purposes only.",
            ],
        }

    historical_applied_patch = classify_patch_record_historical_applied(normalized_target)
    if historical_applied_patch is not None:
        status = historical_applied_patch.get("status")
        return {
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "mixed",
            "decision": "defer",
            "reason": (
                "Applied patch records are preserved historical records of change execution and are not eligible "
                "for live authority lookup. Independently governed predecessor, implementation, and runtime surfaces "
                "remain queryable under their own roles."
            ),
            "evidence_paths": [
                normalized_target,
                "registry/governance_change_ledger.json",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [
                f"Patch record status '{status}' represents historical process execution and does not constitute a live authority lookup candidate.",
            ],
        }

    gen_view = classify_generated_view_component(normalized_target)
    if gen_view is not None:
        return {
            "authority_owner": gen_view.get("authority_owner"),
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear" if gen_view.get("decision") == "allow" else "blocked",
            "decision": gen_view.get("decision"),
            "reason": gen_view.get("reason"),
            "evidence_paths": [
                normalized_target,
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
                "outputs/audits/global_health_report.json",
            ],
            "warnings": [],
        }

    dup_id = classify_duplicate_identity_component(normalized_target)
    if dup_id is not None:
        return {
            "authority_owner": dup_id.get("authority_owner"),
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "blocked",
            "decision": dup_id.get("decision"),
            "reason": dup_id.get("reason"),
            "evidence_paths": [
                normalized_target,
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
                "outputs/audits/global_health_report.json",
            ],
            "warnings": [],
        }

    fallback_rules = [
        {
            "patterns": ["docs/theory/foundational/5_03_26 unity/math/notes/d_derive_rel_c_definition_20260727_001.json"],
            "authority_owner": "docs",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "Canonical D-semantics definition artifact is governed as an exact docs definition surface.",
            "evidence_paths": [
                normalized_target,
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [],
        },
        {
            "patterns": ["registry/math/dependency_graph_registry.json"],
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "The dependency graph registry is a canonical registry synchronization target for additive D-semantics bindings.",
            "evidence_paths": [
                normalized_target,
                "registry/governance_change_ledger.json",
            ],
            "warnings": [],
        },
        {
            "patterns": ["registry/induction_registry.json"],
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "The induction registry is the canonical registry synchronization target for governed induction records.",
            "evidence_paths": [
                normalized_target,
                "registry/governance_change_ledger.json",
            ],
            "warnings": [],
        },
        {
            "patterns": ["governance/live/induction_queue.json"],
            "authority_owner": "governance",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "The live induction queue is the canonical governed queue for admitted induction records.",
            "evidence_paths": [
                normalized_target,
                "governance/live/governance_constitution.json",
            ],
            "warnings": [],
        },
        {
            "patterns": ["registry/db/migrations/20260703_governance_runtime_bootstrap_001.sql"],
            "authority_owner": "db_runtime",
            "authority_source": "registry/db/migrations/20260703_governance_runtime_bootstrap_001.sql",
            "supersession_status": "superseded",
            "superseded_by": [
                "registry/db/migrations/20260703_governance_runtime_current_state_002.sql",
                "registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql",
            ],
            "conflict_state": "stale",
            "decision": "defer",
            "reason": "The bootstrap migration is superseded by later runtime migrations.",
            "evidence_paths": [
                "registry/db/migrations/20260703_governance_runtime_current_state_002.sql",
                "registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql",
            ],
            "warnings": [
                "Use the later runtime migrations instead of the bootstrap surface.",
            ],
        },
        {
            "patterns": ["registry/db/migrations/20260703_governance_runtime_current_state_002.sql"],
            "authority_owner": "db_runtime",
            "authority_source": "registry/db/migrations/20260703_governance_runtime_current_state_002.sql",
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "The current-state migration is the live runtime projection for state queries.",
            "evidence_paths": [
                "registry/db/migrations/20260703_governance_runtime_current_state_002.sql",
                "registry/db/README.md",
            ],
            "warnings": [],
        },
        {
            "patterns": ["registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql"],
            "authority_owner": "db_runtime",
            "authority_source": "registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql",
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "The authority-resolution migration is the live runtime projection for ownership and supersession queries.",
            "evidence_paths": [
                "registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql",
                "registry/db/README.md",
            ],
            "warnings": [],
        },
        {
            "patterns": ["registry/db/migrations/*.sql", "registry/db/*.sqlite", "scripts/query_governance.py"],
            "authority_owner": "db_runtime",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "Live DB runtime surfaces are governed by the DB runtime gate.",
            "evidence_paths": [
                "registry/db/migrations/20260703_governance_runtime_current_state_002.sql",
                "registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [],
        },
        {
            "patterns": ["registry/governance_change_ledger.json", "registry/research_debt_registry.json", "registry/governance/patches/*.json"],
            "authority_owner": "registry",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "Registry surfaces remain authoritative for governed ledger, debt, and patch records.",
            "evidence_paths": [
                "registry/governance_change_ledger.json",
                "registry/research_debt_registry.json",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [],
        },
        {
            "patterns": ["registry/theorem_registry.json"],
            "authority_owner": "registry",
            "authority_source": "registry/theorem_registry.json",
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "The theorem registry is the canonical semantic authority source for theorem, operator-binding, and runtime-rule mappings.",
            "evidence_paths": [
                "registry/theorem_registry.json",
                "registry/db/README.md",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [],
        },
        {
            "patterns": ["registry/db/README.md"],
            "authority_owner": "registry",
            "authority_source": "registry/db/README.md",
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "The DB README is a governed registry document that describes the live runtime surface.",
            "evidence_paths": [
                "registry/db/README.md",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [],
        },
        {
            "patterns": ["docs/governance/*.md"],
            "authority_owner": "docs",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "Governance documentation remains the narrative authority for procedural guidance.",
            "evidence_paths": [
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
                "outputs/audits/global_health_report.json",
            ],
            "warnings": [],
        },
        {
            "patterns": ["docs/governance/*.json"],
            "authority_owner": "docs",
            "authority_source": normalized_target,
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "Governance JSON surfaces remain narrative authority for governed execution artifacts.",
            "evidence_paths": [
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
                "outputs/audits/global_health_report.json",
            ],
            "warnings": [],
        },
        {
            "patterns": ["docs/textbook/mono_process_textbook_complete.md"],
            "authority_owner": "textbook",
            "authority_source": "docs/textbook/mono_process_textbook_complete.md",
            "supersession_status": "current",
            "superseded_by": [],
            "conflict_state": "clear",
            "decision": "allow",
            "reason": "The textbook remains the long-form narrative authority and is not replaced by runtime projections.",
            "evidence_paths": [
                "docs/textbook/mono_process_textbook_complete.md",
                "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            ],
            "warnings": [],
        },
    ]

    for rule in fallback_rules:
        if any(fnmatch(normalized_target, pattern) for pattern in rule["patterns"]):
            authority_source = rule.get("authority_source") or normalized_target
            if "*" in authority_source:
                authority_source = normalized_target
            return {
                "authority_owner": rule.get("authority_owner", "unknown"),
                "authority_source": authority_source,
                "supersession_status": rule.get("supersession_status", "unknown"),
                "superseded_by": rule.get("superseded_by", []),
                "conflict_state": rule.get("conflict_state", "unavailable"),
                "decision": rule.get("decision", "defer"),
                "reason": rule.get("reason", "Authority resolution is unavailable."),
                "evidence_paths": rule.get("evidence_paths", []),
                "warnings": rule.get("warnings", []),
            }

    return {
        "authority_owner": "unknown",
        "authority_source": None,
        "supersession_status": "unavailable",
        "superseded_by": [],
        "conflict_state": "unavailable",
        "decision": "defer",
        "reason": "No governed authority surface matched the target.",
        "evidence_paths": [
            "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            "outputs/audits/global_health_report.json",
        ],
        "warnings": [
            "The target is not covered by the current authority catalog.",
        ],
    }


def normalize_semantic_authority_rank(raw_rank):
    rank = str(raw_rank or "").strip().lower()
    if rank in {"canonical", "primary", "supporting", "deprecated"}:
        return rank
    return "unknown"


def normalize_semantic_authority_status(raw_status):
    status = str(raw_status or "").strip().lower()
    if status in {"active", "superseded", "deprecated", "provisional"}:
        return status
    return "unknown"


def infer_authority_owner_from_source(source):
    normalized = normalize_repo_path(source)
    if not normalized:
        return "unknown"
    if normalized.startswith("registry/"):
        return "registry"
    if normalized.startswith("docs/"):
        return "docs"
    if normalized.startswith("scripts/"):
        return "runtime"
    if normalized.startswith("outputs/"):
        return "runtime"
    return "unknown"


def classify_semantic_authority_target(semantic_key, semantic_type=None):
    normalized_key = str(semantic_key or "").strip()
    normalized_type = str(semantic_type or "").strip() or None
    if not normalized_key:
        return {
            "semantic_key": None,
            "semantic_type": normalized_type,
            "authority_owner": "unknown",
            "authority_source": None,
            "authority_rank": "unknown",
            "supersedes": None,
            "status": "unknown",
            "canonical_expression": None,
            "notes": [],
            "decision": "defer",
            "reason": "Semantic authority requires a semantic key.",
            "conflict_state": "unavailable",
            "supersession": {"status": "unavailable", "superseded_by": []},
            "warnings": ["No semantic key was supplied."],
            "evidence_paths": [
                str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            ],
            "source": "unavailable",
        }

    for record in load_semantic_authority_registry_records():
        if str(record.get("semantic_key") or "").strip() != normalized_key:
            continue
        if normalized_type and str(record.get("semantic_type") or "").strip() != normalized_type:
            continue
        resolved = dict(record)
        resolved["source"] = "semantic_authority_registry"
        resolved["authority_owner"] = infer_authority_owner_from_source(resolved.get("authority_source"))
        resolved["authority_rank"] = normalize_semantic_authority_rank(resolved.get("authority_rank"))
        resolved["status"] = normalize_semantic_authority_status(resolved.get("status"))
        resolved["supersedes"] = resolved.get("supersedes")
        resolved["supersession"] = {
            "status": "superseded" if resolved.get("supersedes") else "current",
            "superseded_by": [normalize_repo_path(resolved.get("supersedes"))] if normalize_repo_path(resolved.get("supersedes")) else [],
        }
        resolved["decision"] = "allow" if resolved["status"] == "active" else "defer"
        resolved["reason"] = "Semantic authority resolved from registry source."
        resolved["conflict_state"] = "clear"
        resolved["warnings"] = []
        resolved["evidence_paths"] = [
            str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            "registry/db/README.md",
            "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
        ]
        if resolved.get("canonical_expression"):
            resolved["evidence_paths"].append(str(SEMANTIC_AUTHORITY_MIGRATION.relative_to(ROOT)).replace("\\", "/"))
        return resolved

    return {
        "semantic_key": normalized_key,
        "semantic_type": normalized_type,
        "authority_owner": "unknown",
        "authority_source": None,
        "authority_rank": "unknown",
        "supersedes": None,
        "status": "unknown",
        "canonical_expression": None,
        "notes": [],
        "decision": "defer",
        "reason": "No governed semantic authority matched the requested key.",
        "conflict_state": "unavailable",
        "supersession": {"status": "unavailable", "superseded_by": []},
        "warnings": [
            "The semantic authority map does not yet cover this key.",
        ],
        "evidence_paths": [
            str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        ],
        "source": "fallback_classification",
    }


def build_semantic_authority_record(semantic_key, semantic_type=None, current_state=None, catalog_rows=None):
    normalized_key = str(semantic_key or "").strip()
    normalized_type = str(semantic_type or "").strip() or None
    base = {
        "semantic_key": normalized_key or None,
        "semantic_type": normalized_type,
        "authority_owner": "unknown",
        "authority_source": None,
        "authority_rank": "unknown",
        "supersedes": None,
        "status": "unknown",
        "canonical_expression": None,
        "notes": [],
        "decision": "defer",
        "reason": "Semantic authority resolution is unavailable.",
        "conflict_state": "unavailable",
        "supersession": {"status": "unavailable", "superseded_by": []},
        "warnings": [],
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        ],
        "source": "unavailable",
    }

    if current_state and current_state.get("warnings"):
        base["warnings"].extend(current_state["warnings"])
    if current_state and current_state.get("status") == "warn":
        base["warnings"].append("Current-state capsule reports warnings.")

    if not normalized_key:
        base["reason"] = "Semantic authority requires a semantic key."
        base["warnings"].append("No semantic key was supplied.")
        return base

    match = None
    for row in catalog_rows or []:
        row_key = str(row.get("semantic_key") or row.get("key") or "").strip()
        row_type = str(row.get("semantic_type") or row.get("type") or "").strip() or None
        if row_key != normalized_key:
            continue
        if normalized_type and row_type and row_type != normalized_type:
            continue
        match = row
        break

    if match is None and normalized_type is not None:
        for row in catalog_rows or []:
            row_key = str(row.get("semantic_key") or row.get("key") or "").strip()
            if row_key == normalized_key:
                match = row
                break

    if match is None:
        fallback = classify_semantic_authority_target(normalized_key, semantic_type=normalized_type)
        base.update(fallback)
        return base

    source = "semantic_authority_view"
    authority_source = normalize_repo_path(match.get("authority_source")) or str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/")
    authority_rank = normalize_semantic_authority_rank(match.get("authority_rank"))
    status = normalize_semantic_authority_status(match.get("status"))
    supersedes = normalize_repo_path(match.get("supersedes"))
    semantic_type_record = str(match.get("semantic_type") or match.get("type") or "").strip() or None
    canonical_expression = match.get("canonical_expression")
    notes = parse_json_collection(match.get("notes"))
    warnings = parse_json_collection(match.get("warnings"))
    type_mismatch = False

    if normalized_type and semantic_type_record and semantic_type_record != normalized_type:
        warnings.append(
            f"Requested semantic type '{normalized_type}' does not match authoritative semantic type '{semantic_type_record}'."
        )
        type_mismatch = True

    if current_state and current_state.get("warnings"):
        warnings.extend(current_state["warnings"])
    if current_state and current_state.get("status") == "warn":
        warnings.append("Current-state capsule reports warnings.")

    if SEMANTIC_AUTHORITY_MIGRATION.exists():
        evidence_paths = [
            str(SEMANTIC_AUTHORITY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ]
    else:
        evidence_paths = []
    evidence_paths.extend(
        [
            str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        ]
    )
    if authority_source:
        evidence_paths.append(authority_source)

    supersession_status = "superseded" if status == "superseded" or supersedes else "current"
    superseded_by = [supersedes] if supersedes else []
    conflict_state = "clear"

    if status == "provisional":
        decision = "defer"
        reason = "Semantic authority is provisional."
        conflict_state = "stale"
    elif status == "superseded":
        decision = "defer" if supersedes else "block"
        reason = "Semantic authority is superseded." if supersedes else "Semantic authority is superseded without a replacement."
        conflict_state = "stale"
        warnings.append("The semantic authority record has been superseded.")
    elif status == "deprecated" or authority_rank == "deprecated":
        decision = "block"
        reason = "Semantic authority is deprecated."
        conflict_state = "stale"
        warnings.append("The semantic authority record is deprecated.")
    elif authority_rank == "canonical" and status == "active":
        decision = "allow"
        reason = "Semantic authority is canonical and active."
    elif authority_rank == "primary" and status == "active":
        decision = "allow"
        reason = "Semantic authority is primary and active."
    elif authority_rank == "supporting" and status == "active":
        decision = "allow"
        reason = "Semantic authority is supporting evidence."
        warnings.append("The semantic authority record is supporting rather than canonical.")
    elif status == "active":
        decision = "allow"
        reason = "Semantic authority is active."
    else:
        decision = "defer"
        reason = "Semantic authority rank or status is incomplete."
        conflict_state = "mixed"
        warnings.append("The semantic authority record is incomplete or unclassified.")

    if type_mismatch:
        decision = "defer"
        reason = (
            f"Requested semantic type '{normalized_type}' does not match authoritative semantic type '{semantic_type_record}'."
        )
        conflict_state = "mixed"

    result = {
        "semantic_key": normalized_key,
        "semantic_type": semantic_type_record or normalized_type,
        "authority_owner": infer_authority_owner_from_source(authority_source),
        "authority_source": authority_source,
        "authority_rank": authority_rank,
        "supersedes": supersedes,
        "status": status,
        "canonical_expression": canonical_expression,
        "notes": notes,
        "decision": decision,
        "reason": reason,
        "conflict_state": conflict_state,
        "supersession": {
            "status": supersession_status,
            "superseded_by": [item for item in superseded_by if item],
        },
        "warnings": [warning for warning in dict.fromkeys(warnings) if warning],
        "evidence_paths": [path for path in dict.fromkeys(path for path in evidence_paths if path)],
        "source": source,
    }
    return result


def collect_patch_semantic_targets(patch):
    targets = []
    for key in ("semantic_targets", "initial_semantic_targets", "affected_semantic_targets", "semantic_bindings"):
        entries = patch.get(key)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if isinstance(entry, dict):
                semantic_key = entry.get("semantic_key") or entry.get("key")
                if not semantic_key:
                    continue
                targets.append(
                    {
                        "semantic_key": str(semantic_key).strip(),
                        "semantic_type": str(entry.get("semantic_type") or entry.get("type") or "").strip() or None,
                        "authority_source": normalize_repo_path(entry.get("authority_source")),
                        "authority_rank": entry.get("authority_rank"),
                        "status": entry.get("status"),
                    }
                )
            elif isinstance(entry, str):
                targets.append({"semantic_key": entry.strip(), "semantic_type": None})
    unique = []
    seen = set()
    for target in targets:
        semantic_key = str(target.get("semantic_key") or "").strip()
        semantic_type = str(target.get("semantic_type") or "").strip() or None
        key = (semantic_key, semantic_type)
        if key in seen or not semantic_key:
            continue
        seen.add(key)
        unique.append(
            {
                "semantic_key": semantic_key,
                "semantic_type": semantic_type,
                "authority_source": target.get("authority_source"),
                "authority_rank": target.get("authority_rank"),
                "status": target.get("status"),
            }
        )
    return unique


def build_semantic_authority_summary(db_path, semantic_targets, current_state=None):
    records = []
    if not semantic_targets:
        return {
            "declared": [],
            "target_decisions": [],
            "decision": "allow",
            "reason": "No semantic targets were declared.",
            "warnings": [],
            "evidence_paths": [],
        }

    db_file = Path(db_path)
    if not db_file.exists():
        return {
            "declared": semantic_targets,
            "target_decisions": [],
            "decision": "defer",
            "reason": "Governance DB file is missing.",
            "warnings": ["The governance runtime database is unavailable."],
            "evidence_paths": [str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/")],
        }

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        ensure_runtime_schema(conn)
        catalog_rows = load_semantic_authority_catalog(conn)
    finally:
        conn.close()

    warnings = []
    evidence_paths = [
        str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        str(SEMANTIC_AUTHORITY_MIGRATION.relative_to(ROOT)).replace("\\", "/") if SEMANTIC_AUTHORITY_MIGRATION.exists() else None,
        str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
    ]
    decision = "allow"
    reason = "Semantic authority checks passed."

    for target in semantic_targets:
        if isinstance(target, dict):
            semantic_key = target.get("semantic_key")
            semantic_type = target.get("semantic_type")
        else:
            semantic_key = str(target)
            semantic_type = None
        record = build_semantic_authority_record(semantic_key, semantic_type=semantic_type, current_state=current_state, catalog_rows=catalog_rows)
        records.append(record)
        warnings.extend(record.get("warnings", []))
        evidence_paths.extend(record.get("evidence_paths", []))
        record_decision = str(record.get("decision", "defer")).lower()
        if record_decision == "block":
            decision = "block"
            reason = f"Semantic authority blocked for {record.get('semantic_key')}"
        elif record_decision == "defer" and decision != "block":
            decision = "defer"
            reason = f"Semantic authority deferred for {record.get('semantic_key')}"
        elif record_decision == "allow" and record.get("authority_rank") == "supporting" and decision == "allow":
            reason = f"Semantic authority is supported but not canonical for {record.get('semantic_key')}"

    return {
        "declared": semantic_targets,
        "target_decisions": records,
        "decision": decision,
        "reason": reason,
        "warnings": [warning for warning in dict.fromkeys(warnings) if warning],
        "evidence_paths": [path for path in dict.fromkeys(path for path in evidence_paths if path)],
    }


def db_snapshot(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(indexed_at) FROM artifacts")
    latest = cursor.fetchone()[0]
    latest_ts = parse_timestamp(latest)
    artifact_count = cursor.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0]
    canonical_active = cursor.execute(
        "SELECT COUNT(*) FROM artifacts WHERE orientation_status = 'canonical_active'"
    ).fetchone()[0]
    active_runtime = cursor.execute(
        "SELECT COUNT(*) FROM artifacts WHERE orientation_status = 'active_runtime'"
    ).fetchone()[0]
    residue_count = cursor.execute(
        "SELECT COUNT(*) FROM artifacts WHERE orientation_status IN ('historical_residue', 'archived', 'superseded', 'invalidated', 'unverified_residue')"
    ).fetchone()[0]
    stale = latest_ts is None or (datetime.now(timezone.utc) - latest_ts).days >= 14
    return {
        "latest_artifact_indexed_at": latest,
        "artifact_count": artifact_count,
        "canonical_active_count": canonical_active,
        "active_runtime_count": active_runtime,
        "residue_count": residue_count,
        "is_stale": stale,
    }


def load_db_snapshot_refresh_metadata(conn):
    cursor = conn.cursor()
    try:
        row = cursor.execute("SELECT * FROM db_snapshot_refresh_view LIMIT 1").fetchone()
    except sqlite3.Error:
        try:
            row = cursor.execute(
                """
                SELECT *
                FROM db_snapshot_refresh_metadata
                WHERE scope = 'global'
                ORDER BY updated_at DESC, last_refresh_attempt DESC
                LIMIT 1
                """
            ).fetchone()
        except sqlite3.Error:
            return {}
    if not row:
        return {}
    data = dict(row)
    if "runtime_worktree_marker" in data:
        return data
    try:
        fallback_row = cursor.execute(
            """
            SELECT *
            FROM db_snapshot_refresh_metadata
            WHERE scope = 'global'
            ORDER BY updated_at DESC, last_refresh_attempt DESC
            LIMIT 1
            """
        ).fetchone()
    except sqlite3.Error:
        return data
    return dict(fallback_row) if fallback_row else data


def _format_utc_timestamp(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        dt = parse_timestamp(str(value))
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_git_status_path(raw_path):
    path_text = str(raw_path or "").strip()
    if not path_text:
        return None
    if " -> " in path_text:
        path_text = path_text.split(" -> ", 1)[1].strip()
    return normalize_repo_path(path_text)


def load_latest_known_worktree_change():
    result = {
        "latest_known_worktree_change": None,
        "latest_runtime_only_worktree_change": None,
        "source": None,
        "change_basis": "none",
        "source_change_count": 0,
        "runtime_only_change_count": 0,
        "source_change_paths": [],
        "runtime_only_change_paths": [],
        "warnings": [],
    }

    try:
        status = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        result["warnings"].append(str(exc))
        return result

    source_paths = []
    runtime_only_paths = []
    for line in (status.stdout or "").splitlines():
        if len(line) < 4:
            continue
        normalized = _normalize_git_status_path(line[3:])
        if not normalized:
            continue
        candidate = ROOT / normalized
        if candidate.exists():
            if is_runtime_only_freshness_path(normalized):
                # Runtime-only churn is ignored for governed freshness identity.
                continue
            source_paths.append(candidate)

    if source_paths:
        latest_candidate = max(source_paths, key=lambda path: path.stat().st_mtime)
        result["latest_known_worktree_change"] = _format_utc_timestamp(
            datetime.fromtimestamp(latest_candidate.stat().st_mtime, tz=timezone.utc)
        )
        result["source"] = "git_status_mtime"
        result["change_basis"] = "mixed" if runtime_only_paths else "source_changes"
        result["source_change_count"] = len(source_paths)
        result["runtime_only_change_count"] = len(runtime_only_paths)
        result["source_change_paths"] = [normalize_repo_path(path) for path in source_paths if normalize_repo_path(path)]
        result["runtime_only_change_paths"] = [normalize_repo_path(path) for path in runtime_only_paths if normalize_repo_path(path)]
        if runtime_only_paths:
            latest_runtime_only_candidate = max(runtime_only_paths, key=lambda path: path.stat().st_mtime)
            result["latest_runtime_only_worktree_change"] = _format_utc_timestamp(
                datetime.fromtimestamp(latest_runtime_only_candidate.stat().st_mtime, tz=timezone.utc)
            )
    elif runtime_only_paths:
        latest_runtime_only_candidate = max(runtime_only_paths, key=lambda path: path.stat().st_mtime)
        result["latest_runtime_only_worktree_change"] = _format_utc_timestamp(
            datetime.fromtimestamp(latest_runtime_only_candidate.stat().st_mtime, tz=timezone.utc)
        )
        result["source"] = "git_status_runtime_only_ignored"
        result["change_basis"] = "runtime_only_only"
        result["runtime_only_change_count"] = len(runtime_only_paths)
        result["runtime_only_change_paths"] = [normalize_repo_path(path) for path in runtime_only_paths if normalize_repo_path(path)]
        return result

    try:
        commit = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", "."],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        result["warnings"].append(str(exc))
        return result

    commit_ts = (commit.stdout or "").strip()
    if commit_ts:
        result["latest_known_worktree_change"] = commit_ts
        result["source"] = "git_commit_fallback"
        result["warnings"].append("No modified or untracked files were detected; using the latest repository commit as fallback freshness evidence.")
        return result

    result["warnings"].append("Unable to determine a latest known worktree change from git status.")
    return result


def surface_requires_db_projection(target):
    normalized = normalize_repo_path(target)
    if not normalized:
        return False
    return (
        normalized == "scripts/query_governance.py"
        or normalized.startswith("registry/db/")
        or normalized.startswith("registry/db/migrations/")
        or normalized.startswith("registry/db/")
    )


def build_db_snapshot_freshness_result(db_path, current_state=None, db_snapshot_result=None, target=None, target_paths=None):
    db_file = Path(db_path)
    normalized_target = normalize_repo_path(target)
    normalized_targets = [
        normalize_repo_path(path)
        for path in parse_json_collection(target_paths or [])
        if normalize_repo_path(path)
    ]
    if normalized_target:
        normalized_targets.insert(0, normalized_target)
    normalized_targets = [path for path in dict.fromkeys(normalized_targets) if path]

    result = {
        "db_snapshot_status": "unknown",
        "decision": "block",
        "reason": "Freshness cannot be determined.",
        "indexed_at": None,
        "artifact_indexed_at": None,
        "last_refresh_attempt": None,
        "last_refresh_result": None,
        "source_worktree_marker": None,
        "runtime_worktree_marker": None,
        "error_reason": None,
        "refresh_source": "unavailable",
        "latest_known_worktree_change": None,
        "latest_runtime_only_worktree_change": None,
        "change_basis": "unknown",
        "staleness_cause": "unknown",
        "source_change_count": 0,
        "runtime_only_change_count": 0,
        "source_change_paths": [],
        "runtime_only_change_paths": [],
        "affected_runtime_surfaces": [],
        "refresh_guidance": {
            "recommended": True,
            "command": None,
            "required_before": [],
        },
        "warnings": [],
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(CURRENT_STATE_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
    }

    if not db_file.exists():
        result["reason"] = "Governance DB file is missing."
        result["warnings"].append("The governance runtime database is unavailable.")
        return result

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        ensure_runtime_schema(conn)
        if db_snapshot_result is None:
            db_snapshot_result = db_snapshot(conn)
        refresh_state = load_db_snapshot_refresh_metadata(conn)
    finally:
        conn.close()

    result["artifact_indexed_at"] = db_snapshot_result.get("latest_artifact_indexed_at") if isinstance(db_snapshot_result, dict) else None
    result["evidence_paths"].append(str(FRESHNESS_MIGRATION.relative_to(ROOT)).replace("\\", "/"))
    result["evidence_paths"].append(str(SNAPSHOT_REFRESH_MIGRATION.relative_to(ROOT)).replace("\\", "/"))
    result["evidence_paths"].append(str(REFRESH_STABILITY_MIGRATION.relative_to(ROOT)).replace("\\", "/"))

    worktree_change = load_latest_known_worktree_change()
    result["latest_known_worktree_change"] = worktree_change.get("latest_known_worktree_change")
    result["latest_runtime_only_worktree_change"] = worktree_change.get("latest_runtime_only_worktree_change")
    result["change_basis"] = worktree_change.get("change_basis", "unknown")
    result["source_change_count"] = worktree_change.get("source_change_count", 0)
    result["runtime_only_change_count"] = worktree_change.get("runtime_only_change_count", 0)
    result["source_change_paths"] = worktree_change.get("source_change_paths", [])
    result["runtime_only_change_paths"] = worktree_change.get("runtime_only_change_paths", [])
    result["warnings"].extend(worktree_change.get("warnings", []))
    if worktree_change.get("source"):
        result["evidence_paths"].append("scripts/query_governance.py")
    if worktree_change.get("source_change_paths"):
        result["evidence_paths"].extend(worktree_change.get("source_change_paths", []))

    if refresh_state:
        result["refresh_source"] = "db_snapshot_refresh_view"
        result["last_refresh_attempt"] = refresh_state.get("last_refresh_attempt")
        result["last_refresh_result"] = refresh_state.get("last_refresh_result")
        result["source_worktree_marker"] = refresh_state.get("source_worktree_marker")
        result["runtime_worktree_marker"] = refresh_state.get("runtime_worktree_marker")
        result["error_reason"] = refresh_state.get("error_reason")
        result["indexed_at"] = refresh_state.get("indexed_at") or refresh_state.get("last_refresh_attempt")
    else:
        result["refresh_source"] = "artifacts_fallback"
        result["indexed_at"] = result["artifact_indexed_at"]

    indexed_ts = parse_timestamp(result["indexed_at"])
    artifact_ts = parse_timestamp(result["artifact_indexed_at"])
    worktree_ts = parse_timestamp(result["latest_known_worktree_change"])
    marker_ts = parse_timestamp(result["source_worktree_marker"])
    runtime_marker_ts = parse_timestamp(result["runtime_worktree_marker"])
    runtime_change_ts = parse_timestamp(result["latest_runtime_only_worktree_change"])
    runtime_churn_detected = (
        runtime_change_ts is not None
        and runtime_marker_ts is not None
        and runtime_change_ts > runtime_marker_ts
    )

    db_dependent_targets = [
        path for path in normalized_targets
        if surface_requires_db_projection(path)
    ]

    if refresh_state:
        refresh_result = str(result["last_refresh_result"] or "").lower()
        if refresh_result not in {"success", "succeeded", "pass"}:
            result["db_snapshot_status"] = "stale"
            result["staleness_cause"] = "unknown"
            result["decision"] = "block" if db_dependent_targets else "warn"
            result["reason"] = (
                "The last verified snapshot refresh failed"
                + (f": {result['error_reason']}" if result["error_reason"] else ".")
            )
            result["refresh_guidance"]["recommended"] = True
            result["refresh_guidance"]["command"] = "python scripts/db/snapshot_registries.py"
            result["refresh_guidance"]["required_before"] = [
                "rerun the refresh command",
                "re-run current-state",
                "re-run patch-gate for DB-dependent targets",
            ]
            result["warnings"].append("The last snapshot refresh attempt did not succeed.")
        elif indexed_ts is None:
            result["db_snapshot_status"] = "unknown"
            result["staleness_cause"] = "unknown"
            result["decision"] = "block" if db_dependent_targets else "warn"
            result["reason"] = "The last snapshot refresh succeeded, but no indexed timestamp was recorded."
            result["refresh_guidance"]["recommended"] = True
            result["refresh_guidance"]["command"] = "python scripts/db/snapshot_registries.py"
            result["refresh_guidance"]["required_before"] = [
                "re-run current-state",
                "re-run patch-gate for DB-dependent targets",
            ]
            result["warnings"].append("Snapshot refresh metadata is incomplete.")
        elif worktree_ts is not None and indexed_ts < worktree_ts:
            result["db_snapshot_status"] = "stale"
            result["staleness_cause"] = "source_change"
            result["decision"] = "defer" if db_dependent_targets else "warn"
            if marker_ts is not None and worktree_ts > marker_ts:
                result["reason"] = (
                    "The last verified refresh succeeded at "
                    f"{result['indexed_at']}, but the latest known worktree change "
                    f"{result['latest_known_worktree_change']} is newer than the refresh marker "
                    f"{result['source_worktree_marker']}. Runtime-only DB churn, if present, is ignored for freshness."
                )
            else:
                result["reason"] = (
                    "The last verified refresh succeeded, but source-affecting worktree changes are newer than the refresh timestamp "
                    f"{result['indexed_at']}. Runtime-only DB churn, if present, is ignored for freshness."
                )
            result["refresh_guidance"]["recommended"] = True
            result["refresh_guidance"]["command"] = "python scripts/db/snapshot_registries.py"
            result["refresh_guidance"]["required_before"] = [
                "rerun the refresh command after the newer worktree changes are settled",
                "re-run current-state",
                "re-run patch-gate for DB-dependent targets",
            ]
            result["warnings"].append("The DB snapshot is older than the current worktree state.")
        else:
            result["db_snapshot_status"] = "fresh"
            result["staleness_cause"] = "runtime_churn" if runtime_churn_detected else "none"
            result["decision"] = "allow_with_note" if runtime_churn_detected else "allow"
            if db_dependent_targets:
                if runtime_churn_detected:
                    result["reason"] = (
                        "The last verified snapshot refresh succeeded and covers the requested DB-dependent target surfaces; "
                        "runtime-only DB churn is newer than the recorded runtime marker, so freshness remains valid with note."
                    )
                else:
                    result["reason"] = "The last verified snapshot refresh succeeded and covers the requested DB-dependent target surfaces."
            else:
                if runtime_churn_detected:
                    result["reason"] = (
                        "The last verified snapshot refresh succeeded and the DB snapshot is current; "
                        "runtime-only DB churn is newer than the recorded runtime marker, so freshness remains valid with note."
                    )
                else:
                    result["reason"] = "The last verified snapshot refresh succeeded and the DB snapshot is current."
            result["refresh_guidance"]["recommended"] = False
            result["refresh_guidance"]["required_before"] = []
    else:
        if indexed_ts is None:
            result["db_snapshot_status"] = "unknown"
            result["staleness_cause"] = "unknown"
            result["decision"] = "block" if db_dependent_targets else "warn"
            result["reason"] = "No verified snapshot refresh metadata or artifact index timestamp is available."
            result["refresh_guidance"]["recommended"] = True
            result["refresh_guidance"]["command"] = "python scripts/db/snapshot_registries.py"
            result["refresh_guidance"]["required_before"] = [
                "re-run current-state",
                "re-run patch-gate for DB-dependent targets",
            ]
            result["warnings"].append("Database snapshot freshness is unavailable.")
        elif artifact_ts is None:
            result["db_snapshot_status"] = "unknown"
            result["staleness_cause"] = "unknown"
            result["decision"] = "block" if db_dependent_targets else "warn"
            result["reason"] = "The artifact index timestamp is unavailable."
            result["refresh_guidance"]["recommended"] = True
            result["refresh_guidance"]["command"] = "python scripts/db/snapshot_registries.py"
            result["refresh_guidance"]["required_before"] = [
                "re-run current-state",
                "re-run patch-gate for DB-dependent targets",
            ]
            result["warnings"].append("Artifact index freshness is unavailable.")
        elif worktree_ts is None:
            if db_snapshot_result.get("is_stale"):
                result["db_snapshot_status"] = "stale"
                result["staleness_cause"] = "unknown"
                result["decision"] = "defer" if db_dependent_targets else "warn"
                if result["runtime_only_change_count"] > 0:
                    result["reason"] = "The artifact index is older than the freshness threshold; runtime-only DB churn was detected and ignored for freshness."
                else:
                    result["reason"] = "The artifact index is older than the freshness threshold and no newer source-affecting worktree timestamp is available."
            else:
                result["db_snapshot_status"] = "fresh"
                result["staleness_cause"] = "runtime_churn" if runtime_churn_detected else "none"
                result["decision"] = "allow_with_note" if runtime_churn_detected else "allow"
                if runtime_churn_detected:
                    result["reason"] = "The artifact index is within the freshness threshold and runtime-only DB churn is newer than the recorded runtime marker, so freshness remains valid with note."
                else:
                    result["reason"] = "The artifact index is within the freshness threshold and no newer source-affecting worktree timestamp is available."
        elif artifact_ts >= worktree_ts:
            result["db_snapshot_status"] = "fresh"
            result["staleness_cause"] = "runtime_churn" if runtime_churn_detected else "none"
            result["decision"] = "allow_with_note" if runtime_churn_detected else "allow"
            if runtime_churn_detected:
                result["reason"] = "The artifact index is at or after the latest source-affecting worktree change; runtime-only DB churn is newer than the recorded runtime marker, so freshness remains valid with note."
            else:
                result["reason"] = "The artifact index is at or after the latest known worktree change."
        else:
            result["db_snapshot_status"] = "stale"
            result["staleness_cause"] = "source_change"
            result["decision"] = "defer" if db_dependent_targets else "warn"
            if result["runtime_only_change_count"] > 0:
                result["reason"] = "The latest source-affecting worktree change is newer than the artifact index. Runtime-only DB churn was detected and ignored for freshness."
            else:
                result["reason"] = "The latest known worktree change is newer than the artifact index."
        result["refresh_guidance"]["recommended"] = result["db_snapshot_status"] != "fresh"
        result["refresh_guidance"]["command"] = "python scripts/db/snapshot_registries.py"
        if result["db_snapshot_status"] == "fresh":
            result["refresh_guidance"]["required_before"] = []
        else:
            result["refresh_guidance"]["required_before"] = [
                "rerun the refresh command",
                "re-run current-state",
                "re-run patch-gate for DB-dependent targets",
            ]

    if db_dependent_targets:
        result["affected_runtime_surfaces"] = db_dependent_targets
    elif result["db_snapshot_status"] != "fresh":
        result["affected_runtime_surfaces"] = [
            "current-state",
            "authority",
            "patch-chain",
            "debt",
            "context-capsule",
            "patch-gate",
            "replay-events",
            "reconcile-events",
        ]

    if current_state and current_state.get("warnings"):
        result["warnings"].extend(current_state["warnings"])

    result["warnings"] = [warning for warning in dict.fromkeys(result["warnings"]) if warning]
    result["evidence_paths"] = [path for path in dict.fromkeys(path for path in result["evidence_paths"] if path)]
    return result


def build_current_state_capsule(db_path):
    db_file = Path(db_path)
    capsule = {
        "status": "unavailable",
        "health": {
            "global_validation": "unknown",
            "source": str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        },
        "runtime": {
            "db_first_gate": "unknown",
            "authority_boundary": "unknown",
        },
        "blockers": [],
        "open_debt": [],
        "latest_decisions": [],
        "warnings": [],
        "evidence_paths": [
            str(db_file.relative_to(ROOT)).replace("\\", "/") if db_file.is_relative_to(ROOT) else str(db_file),
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(RESEARCH_DEBT_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            str(CLAIM_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            str(CLAIM_SUPPORT_MATRIX.relative_to(ROOT)).replace("\\", "/"),
            str(CURRENT_STATE_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(AUTHORITY_RESOLUTION_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(PATCH_CHAIN_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(DEBT_RUNTIME_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_BUS_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_REPLAY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_RECONCILIATION_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(REFRESH_STABILITY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(SEMANTIC_AUTHORITY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
    }

    if not db_file.exists():
        capsule["warnings"].append("Governance DB file is missing.")
        return capsule

    report = load_optional_json(GLOBAL_HEALTH_REPORT)
    capsule["health"]["global_validation"] = extract_global_validation_status(report)

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        ensure_runtime_schema(conn)
        row = conn.execute("SELECT * FROM current_state_view LIMIT 1").fetchone()
        state = dict(row) if row else {}
        snapshot = db_snapshot(conn)
        semantic_catalog = load_semantic_authority_catalog(conn)
        claim_registry_records = load_claim_registry_records()
        claim_support_records = load_claim_support_matrix_records()
        freshness = build_db_snapshot_freshness_result(
            db_path,
            current_state=state,
            db_snapshot_result=snapshot,
        )
        capsule["runtime"]["db_first_gate"] = "active" if state else "inactive"
        capsule["runtime"]["authority_boundary"] = state.get("authority_boundary") or "unknown"
        capsule["runtime"]["latest_artifact_indexed_at"] = state.get("latest_artifact_indexed_at")
        capsule["runtime"]["artifact_count"] = state.get("artifact_count", 0)
        capsule["runtime"]["canonical_active_count"] = state.get("canonical_active_count", 0)
        capsule["runtime"]["active_runtime_count"] = state.get("active_runtime_count", 0)
        capsule["runtime"]["residue_count"] = state.get("residue_count", 0)
        capsule["runtime"]["invalidated_count"] = state.get("invalidated_count", 0)
        capsule["runtime"]["decision_count"] = state.get("decision_count", 0)
        capsule["freshness"] = {
            "db_snapshot_status": freshness["db_snapshot_status"],
            "decision": freshness["decision"],
            "indexed_at": freshness["indexed_at"],
            "latest_known_worktree_change": freshness["latest_known_worktree_change"],
            "latest_runtime_only_worktree_change": freshness.get("latest_runtime_only_worktree_change"),
            "source_worktree_marker": freshness.get("source_worktree_marker"),
            "runtime_worktree_marker": freshness.get("runtime_worktree_marker"),
            "change_basis": freshness.get("change_basis", "unknown"),
            "staleness_cause": freshness.get("staleness_cause", "unknown"),
            "source_change_count": freshness.get("source_change_count", 0),
            "runtime_only_change_count": freshness.get("runtime_only_change_count", 0),
        }
        capsule["evidence_paths"] = [path for path in dict.fromkeys(capsule["evidence_paths"] + freshness["evidence_paths"]) if path]
        if freshness["warnings"]:
            capsule["warnings"].extend(freshness["warnings"])
        if freshness["db_snapshot_status"] == "stale":
            capsule["warnings"].append("Database snapshot is stale.")
        elif freshness["db_snapshot_status"] == "unknown":
            capsule["warnings"].append("Database snapshot freshness is unavailable.")

        coverage_state = state.get("coverage_state")
        if coverage_state and coverage_state not in {"active", "current", "stateful_projection"}:
            capsule["warnings"].append(f"Current-state coverage is {coverage_state}.")

        decision_count = state.get("decision_count")
        if decision_count == 0:
            capsule["warnings"].append("No governance decisions are logged yet.")

        latest_decision_id = state.get("latest_decision_id")
        if latest_decision_id:
            capsule["latest_decisions"] = collect_recent_governance_decisions(conn)
        else:
            capsule["warnings"].append("No latest governance decision is available.")

        open_debt = collect_governance_runtime_debt()
        capsule["open_debt"] = open_debt
        if open_debt:
            capsule["warnings"].append(f"{len(open_debt)} governance/runtime debt item(s) remain open.")

        debt_catalog = load_debt_runtime_catalog(conn)
        semantic_projection = build_semantic_rt_projection(
            str(db_file),
            current_state=state,
            catalog_rows=semantic_catalog,
        )
        semantic_authority_graph = build_semantic_authority_graph_projection(
            semantic_catalog,
            current_state=state,
        )
        claim_reasoning = build_claim_reasoning_projection(
            conn,
            current_state=state,
            claim_registry_records=claim_registry_records,
            claim_support_records=claim_support_records,
        )
        replay_projection = build_replay_reconciliation_projection(conn)
        debt_projection = build_debt_blocker_projection(open_debt, current_state=state)
        residue_projection = build_historical_residue_projection(current_state=state, debt_records=debt_catalog)

        capsule["projection"] = {
            "semantic_rt": semantic_projection,
            "semantic_authority_graph": semantic_authority_graph,
            "claim_reasoning": claim_reasoning,
            "replay_reconciliation": replay_projection,
            "debt_blocker": debt_projection,
            "historical_residue": residue_projection,
        }
        capsule["runtime"]["current_rt"] = semantic_projection.get("current_rt") or state.get("current_rt") or "RT := [(ℰ≠0) ⇔R δα(ℰ>0)]"
        capsule["runtime"]["semantic_projection_state"] = (
            semantic_projection.get("projection_state")
            or state.get("semantic_projection_state")
            or "unknown"
        )
        capsule["runtime"]["semantic_authority_graph_state"] = semantic_authority_graph.get("projection_state", "unknown")
        capsule["runtime"]["semantic_authority_count"] = semantic_authority_graph.get("semantic_authority_count", 0)
        capsule["runtime"]["claim_reasoning_state"] = claim_reasoning.get("projection_state", "unknown")
        capsule["runtime"]["claim_registry_count"] = claim_reasoning.get("registry", {}).get("claim_count", 0)
        capsule["runtime"]["claim_support_count"] = claim_reasoning.get("support_matrix", {}).get("claim_count", 0)
        capsule["runtime"]["claim_evidence_link_count"] = claim_reasoning.get("db_links", {}).get("link_count", 0)
        capsule["runtime"]["claim_evidence_state"] = claim_reasoning.get("db_links", {}).get("state", "unknown")
        capsule["runtime"]["replay_reconciliation_state"] = replay_projection.get("projection_state", "unknown")
        capsule["runtime"]["replay_reconciliation_boundary_state"] = replay_projection.get("boundary_state", "unknown")
        capsule["runtime"]["replay_reconciliation_coverage_state"] = replay_projection.get("coverage_state", "unknown")
        capsule["runtime"]["replay_reconciliation_subject_count"] = replay_projection.get("subject_count", 0)
        capsule["runtime"]["replay_reconciliation_event_count"] = replay_projection.get("event_count", 0)
        capsule["runtime"]["replay_reconciliation_latest_subject_id"] = replay_projection.get("latest_subject_id")
        capsule["runtime"]["replay_reconciliation_latest_subject_type"] = replay_projection.get("latest_subject_type")
        capsule["runtime"]["replay_reconciliation_latest_event_id"] = replay_projection.get("latest_event_id")
        capsule["runtime"]["replay_reconciliation_latest_event_type"] = replay_projection.get("latest_event_type")
        capsule["runtime"]["replay_reconciliation_latest_source_patch_id"] = replay_projection.get("latest_source_patch_id")
        capsule["runtime"]["replay_reconciliation_latest_source_path"] = replay_projection.get("latest_source_path")
        capsule["runtime"]["replay_reconciliation_latest_created_at"] = replay_projection.get("latest_created_at")
        capsule["runtime"]["historical_residue_state"] = (
            residue_projection.get("projection_state")
            or state.get("historical_residue_state")
            or "unknown"
        )
        capsule["runtime"]["open_runtime_debt_count"] = debt_projection.get("open_debt_count", len(open_debt))
        capsule["runtime"]["open_debt_count"] = capsule["runtime"]["open_runtime_debt_count"]
        capsule["runtime"]["live_blocker_count"] = debt_projection.get("blocking_debt_count", 0)
        capsule["runtime"]["debt_projection_state"] = debt_projection.get("projection_state", "unknown")
        if semantic_projection.get("warnings"):
            capsule["warnings"].extend(semantic_projection.get("warnings", []))
        if semantic_authority_graph.get("warnings"):
            capsule["warnings"].extend(semantic_authority_graph.get("warnings", []))
        if claim_reasoning.get("warnings"):
            capsule["warnings"].extend(claim_reasoning.get("warnings", []))
        if replay_projection.get("warnings"):
            capsule["warnings"].extend(replay_projection.get("warnings", []))
        if residue_projection.get("residual_debt_count", 0) > 0 and "Historical residue remains projected." not in capsule["warnings"]:
            capsule["warnings"].append("Historical residue remains projected.")

        if capsule["health"]["global_validation"] == "fail":
            capsule["blockers"].append("global_validation_failed")
        elif capsule["health"]["global_validation"] == "unknown":
            capsule["warnings"].append("Global validation status is unavailable.")

        capsule["warnings"] = [warning for warning in dict.fromkeys(capsule["warnings"]) if warning]

        if capsule["blockers"]:
            capsule["status"] = "fail"
        elif capsule["warnings"]:
            capsule["status"] = "warn"
        else:
            capsule["status"] = "pass"
    finally:
        conn.close()

    return capsule


def log_decision(conn, record):
    decision_timestamp = datetime.now(timezone.utc)
    decision_timestamp_slug = _governance_timestamp_slug(decision_timestamp)
    full_evidence = record.get("evidence_json", {})
    if not isinstance(full_evidence, dict):
        full_evidence = {}

    external_evidence_path = None
    external_evidence_hash = None
    try:
        external_evidence_path, external_evidence_hash = _externalize_governance_decision_evidence(
            record,
            full_evidence,
            decision_timestamp_slug,
        )
    except OSError:
        external_evidence_path = None
        external_evidence_hash = None

    compact_evidence = _build_compact_governance_decision_evidence(
        record,
        external_evidence_path=external_evidence_path,
        external_evidence_hash=external_evidence_hash,
        decision_timestamp=decision_timestamp.isoformat(),
    )
    compact_evidence["failure_codes"] = _build_governance_failure_codes(record, full_evidence.get("patch_chain", {}))
    compact_evidence["summary_counts"] = _build_governance_summary_counts(
        record,
        full_evidence,
        compact_evidence.get("artifact_paths", []),
        compact_evidence.get("artifact_hashes", {}),
        compact_evidence.get("dependency_patch_ids", []),
        full_evidence.get("patch_chain", {}) if isinstance(full_evidence.get("patch_chain", {}), dict) else {},
    )

    conn.execute(
        """
        INSERT INTO governance_decision_log (
            decision_id,
            patch_id,
            campaign_id,
            requested_action,
            decision,
            reason,
            blocking_conditions,
            authority_resolution,
            dependency_resolution,
            provenance_resolution,
            validator_resolution,
            db_snapshot_at,
            operator,
            evidence_json,
            metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["decision_id"],
            record["patch_id"],
            record.get("campaign_id"),
            record.get("requested_action"),
            record["decision"],
            record["reason"],
            json.dumps(record.get("blocking_conditions", []), ensure_ascii=False),
            json.dumps(record.get("authority_resolution", {}), ensure_ascii=False),
            json.dumps(record.get("dependency_resolution", {}), ensure_ascii=False),
            json.dumps(record.get("provenance_resolution", {}), ensure_ascii=False),
            json.dumps(record.get("validator_resolution", {}), ensure_ascii=False),
            record.get("db_snapshot_at"),
            record.get("operator"),
            json.dumps(compact_evidence, ensure_ascii=False),
            json.dumps(record.get("metadata_json", {}), ensure_ascii=False),
        ),
    )
    event_written = False
    try:
        append_governance_event(
            conn,
            {
                "event_type": "governance_decision",
                "subject_id": record["patch_id"],
                "subject_type": "patch",
                "source_patch_id": record["patch_id"],
                "source_path": "scripts/query_governance.py",
                "payload": {
                    "decision_id": record["decision_id"],
                    "campaign_id": record.get("campaign_id"),
                    "requested_action": record.get("requested_action"),
                    "decision": record["decision"],
                    "reason": record["reason"],
                    "blocking_conditions": parse_json_collection(record.get("blocking_conditions")),
                    "authority_resolution": record.get("authority_resolution", {}),
                    "dependency_resolution": record.get("dependency_resolution", {}),
                    "provenance_resolution": record.get("provenance_resolution", {}),
                    "validator_resolution": record.get("validator_resolution", {}),
                    "db_snapshot_at": record.get("db_snapshot_at"),
                    "patch_chain_status": compact_evidence.get("status"),
                    "patch_chain_decision": compact_evidence.get("patch_chain_decision"),
                    "patch_gate_decision": compact_evidence.get("patch_gate_decision"),
                    "full_evidence_path": compact_evidence.get("full_evidence_path"),
                    "full_evidence_hash": compact_evidence.get("full_evidence_hash"),
                    "failure_codes": compact_evidence.get("failure_codes", []),
                    "summary_counts": compact_evidence.get("summary_counts", {}),
                },
                "evidence_paths": [
                    str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
                    str(EVENT_BUS_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
                    compact_evidence.get("full_evidence_path"),
                    "scripts/query_governance.py",
                ],
            },
        )
        event_written = True
    except sqlite3.Error:
        pass
    conn.commit()
    return {
        "event_written": event_written,
        "full_evidence_path": compact_evidence.get("full_evidence_path"),
        "full_evidence_hash": compact_evidence.get("full_evidence_hash"),
        "compact_evidence": compact_evidence,
    }


def evaluate_patch_gate(
    db_path,
    patch,
    patch_source_path=None,
    requested_action="propose",
    log_to_db=True,
    target_override=None,
    current_state=None,
    ledger_index=None,
    patch_chain_result=None,
):
    if current_state is None:
        current_state = build_current_state_capsule(db_path)
    if ledger_index is None:
        ledger_index = load_governance_change_ledger_index()
    patch_chain = patch_chain_result or build_patch_chain_result(patch.get("patch_id"), current_state=current_state, ledger_index=ledger_index)
    patch_already_resolved = patch_chain.get("status") in {"applied", "late_registered"}
    target_paths = collect_patch_target_paths(patch)
    if target_override:
        target_paths = [normalize_repo_path(target_override)] + target_paths
    target_paths = [path for path in dict.fromkeys(path for path in target_paths if path)]
    patch_path = Path(patch_source_path) if patch_source_path else None
    result = {
        "mode": "governance_runtime",
        "db_path": str(db_path),
        "patch_file": str(patch_path) if patch_path else None,
        "patch_id": patch.get("patch_id"),
        "campaign_id": patch.get("campaign_id"),
        "requested_action": requested_action,
        "decision": "defer",
        "reason": "",
        "blocking_conditions": [],
        "defer_conditions": [],
        "patch_chain": patch_chain,
        "authority_resolution": {
            "winning_authority": "registry",
            "rule": "Authority is resolved per target surface before application; the runtime returns allow/block/defer for each governed surface.",
            "runtime_boundary": current_state.get("runtime", {}).get("authority_boundary", "unknown"),
            "target_decisions": [],
        },
        "semantic_authority_resolution": {
            "winning_authority": "registry",
            "rule": "Semantic authority is resolved for declared semantic targets before application; missing or superseded semantic authority is not silently allowed.",
            "target_decisions": [],
            "declared": [],
            "decision": "allow",
            "reason": "No semantic targets declared.",
        },
        "dependency_resolution": {
            "declared": patch.get("depends_on", []),
            "missing": []
        },
        "provenance_resolution": {
            "has_basis": bool(patch.get("basis")),
            "has_core_rule": bool(patch.get("core_rule"))
        },
        "validator_resolution": {
            "required_repo_changes_declared": bool(patch.get("required_repo_changes")),
            "success_criteria_declared": bool(patch.get("success_criteria"))
        },
        "current_state": current_state,
        "db_snapshot": {},
        "schema_bootstrapped": False,
        "warnings": [],
        "log_written": False,
        "event_written": False,
    }

    if not patch.get("patch_id"):
        result["blocking_conditions"].append("missing_patch_id")
    if not patch_already_resolved:
        if not patch.get("basis"):
            result["blocking_conditions"].append("missing_provenance")
        if not patch.get("core_rule"):
            result["blocking_conditions"].append("missing_core_rule")
        patch_mode = patch.get("mode")
        governed_transition = (
            patch_mode in {"governed_transition", "governed_workflow_extension"}
            and patch.get("transition_authorized") is True
            and bool(patch.get("transition_record_id"))
            and bool(patch.get("migration_plan_id"))
        )
        if patch_mode != "additive" and not governed_transition:
            result["blocking_conditions"].append("non_additive_patch_mode")
    if not patch.get("target_files") and not patch.get("required_repo_changes"):
        result["defer_conditions"].append("insufficient_execution_surface")

    if patch_chain["decision"] == "block":
        result["blocking_conditions"].extend(
            patch_chain.get("blockers", []) or [f"patch_chain_blocked:{patch_chain.get('patch_id') or 'unknown'}"]
        )
    elif patch_chain["decision"] == "defer":
        result["defer_conditions"].append(f"patch_chain_{patch_chain.get('status', 'unknown')}")

    declared_deps = patch.get("depends_on") or []
    missing_deps = []
    for dep in declared_deps:
        dep_path = ROOT / "registry/governance/patches" / f"{dep}.json"
        if not dep_path.exists():
            missing_deps.append(dep)
    if missing_deps:
        result["blocking_conditions"].append("missing_required_dependency")
        result["dependency_resolution"]["missing"] = missing_deps

    db_file = Path(db_path)
    if not db_file.exists():
        result["blocking_conditions"].append("missing_db_file")
        result["reason"] = "Governance DB file is missing."
        result["decision"] = "block"
        return result

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        result["schema_bootstrapped"] = ensure_runtime_schema(conn)
        result["db_snapshot"] = db_snapshot(conn)
        authority_catalog = load_authority_resolution_catalog(conn)
        authority_target_records = [
            build_authority_resolution_record(target, current_state=current_state, catalog_rows=authority_catalog)
            for target in target_paths
        ]
        result["authority_resolution"]["target_decisions"] = authority_target_records

        authority_blockers = []
        authority_defers = []
        authority_owners = []
        for record in authority_target_records:
            owner = record.get("authority_owner")
            if owner:
                authority_owners.append(owner)
            decision = str(record.get("decision", "defer")).lower()
            if decision == "block":
                authority_blockers.append(f"authority_blocked_target:{record.get('target')}")
            elif decision == "defer":
                authority_defers.append(f"authority_deferred_target:{record.get('target')}")

        if authority_owners:
            unique_owners = list(dict.fromkeys(authority_owners))
            result["authority_resolution"]["winning_authority"] = unique_owners[0] if len(unique_owners) == 1 else "mixed"
        if authority_target_records:
            if any(record.get("conflict_state") == "mixed" for record in authority_target_records):
                result["authority_resolution"]["runtime_boundary"] = "mixed"
            result["authority_resolution"]["decision"] = (
                "block"
                if authority_blockers
                else "defer"
                if authority_defers
                else "allow"
            )
        result["authority_resolution"]["reason"] = (
            "Blocked by authority conflicts."
            if authority_blockers
            else "Deferred by authority resolution."
            if authority_defers
            else "All target surfaces resolved by authority lookup."
        )

        semantic_targets = collect_patch_semantic_targets(patch)
        semantic_resolution = {
            "winning_authority": "registry",
            "rule": "Semantic authority is resolved for declared semantic targets before application; missing or superseded semantic authority is not silently allowed.",
            "target_decisions": [],
            "declared": semantic_targets,
            "decision": "allow",
            "reason": "No semantic targets declared.",
            "warnings": [],
            "evidence_paths": [
                str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
                str(SEMANTIC_AUTHORITY_MIGRATION.relative_to(ROOT)).replace("\\", "/") if SEMANTIC_AUTHORITY_MIGRATION.exists() else None,
                str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            ],
        }
        if semantic_targets:
            semantic_catalog = load_semantic_authority_catalog(conn)
            semantic_target_records = []
            semantic_blockers = []
            semantic_defers = []
            semantic_warnings = []
            for semantic_target in semantic_targets:
                semantic_record = build_semantic_authority_record(
                    semantic_target.get("semantic_key"),
                    semantic_type=semantic_target.get("semantic_type"),
                    current_state=current_state,
                    catalog_rows=semantic_catalog,
                )
                semantic_record["declared"] = semantic_target
                semantic_target_records.append(semantic_record)
                semantic_warnings.extend(semantic_record.get("warnings", []))
                effect = str(semantic_record.get("decision", "defer")).lower()
                semantic_key = semantic_record.get("semantic_key") or "unknown"
                if effect == "block":
                    semantic_blockers.append(f"semantic_blocked:{semantic_key}")
                elif effect == "defer":
                    semantic_defers.append(f"semantic_deferred:{semantic_key}")
            semantic_resolution["target_decisions"] = semantic_target_records
            if semantic_blockers and not patch_already_resolved:
                result["blocking_conditions"].extend(semantic_blockers)
            if semantic_defers and not patch_already_resolved:
                result["defer_conditions"].extend(semantic_defers)
            if semantic_warnings:
                result["warnings"].extend(semantic_warnings)
            if semantic_blockers:
                semantic_resolution["decision"] = "block"
                semantic_resolution["reason"] = "Semantic authority blocks at least one declared semantic target."
            elif semantic_defers:
                semantic_resolution["decision"] = "defer"
                semantic_resolution["reason"] = "Semantic authority defers at least one declared semantic target."
            else:
                semantic_resolution["decision"] = "allow"
                semantic_resolution["reason"] = "All declared semantic targets resolved successfully."
        result["semantic_authority_resolution"] = semantic_resolution

        debt_target = normalize_repo_path(target_override) if target_override else (target_paths[0] if len(target_paths) == 1 else None)
        debt_resolution = build_debt_runtime_result(
            db_path,
            target=debt_target,
            status_filter="all",
            current_state=current_state,
        )
        result["debt_resolution"] = debt_resolution

        debt_blockers = []
        debt_defers = []
        debt_warnings = []
        for record in debt_resolution.get("debts", []):
            effect = str(record.get("decision_effect", "warn")).lower()
            debt_id = record.get("debt_id") or "unknown"
            if effect == "block":
                debt_blockers.append(f"debt_blocked:{debt_id}")
            elif effect == "defer":
                debt_defers.append(f"debt_deferred:{debt_id}")
            else:
                debt_warnings.extend(record.get("warnings", []))

        if debt_blockers and not patch_already_resolved:
            result["blocking_conditions"].extend(debt_blockers)
        if debt_defers and not patch_already_resolved:
            result["defer_conditions"].extend(debt_defers)
        if debt_warnings:
            result["warnings"].extend(debt_warnings)
        if current_state.get("warnings"):
            result["warnings"].extend(current_state["warnings"])

        if current_state.get("blockers") and not patch_already_resolved:
            result["blocking_conditions"].extend(current_state["blockers"])
        if authority_blockers and not patch_already_resolved:
            result["blocking_conditions"].extend(authority_blockers)
        if authority_defers and not patch_already_resolved:
            result["defer_conditions"].extend(authority_defers)

        freshness_resolution = build_db_snapshot_freshness_result(
            db_path,
            current_state=current_state,
            db_snapshot_result=result["db_snapshot"],
            target_paths=target_paths,
            target=target_override,
        )
        result["freshness"] = freshness_resolution
        result["warnings"].extend(freshness_resolution.get("warnings", []))
        if freshness_resolution.get("decision") == "block" and not patch_already_resolved:
            result["blocking_conditions"].append("freshness_unknown")
        elif freshness_resolution.get("decision") == "defer" and not patch_already_resolved:
            result["defer_conditions"].append("stale_db_snapshot")
        elif freshness_resolution.get("decision") == "warn":
            result["warnings"].append("Freshness gate issued a warning.")
        elif freshness_resolution.get("decision") == "allow_with_note":
            result["warnings"].append("Freshness gate recorded runtime-only churn but did not block the patch.")
        if current_state.get("status") == "fail" and not patch_already_resolved:
            result["blocking_conditions"].append("current_state_unhealthy")

        result["blocking_conditions"] = list(dict.fromkeys(result["blocking_conditions"]))
        if result["blocking_conditions"]:
            result["decision"] = "block"
            result["reason"] = "Blocked by: " + ", ".join(result["blocking_conditions"])
        elif result["defer_conditions"]:
            result["decision"] = "defer"
            result["reason"] = "Deferred pending: " + ", ".join(result["defer_conditions"])
        else:
            result["decision"] = "defer" if patch_already_resolved else "apply"
            result["reason"] = "Patch already resolved; no application needed." if patch_already_resolved else "All runtime checks passed."

        result["evidence_json"] = {
            "basis": patch.get("basis", {}),
            "core_rule": patch.get("core_rule", {}),
            "required_repo_changes": patch.get("required_repo_changes", []),
            "semantic_targets": patch.get("semantic_targets", [])
            or patch.get("initial_semantic_targets", [])
            or patch.get("affected_semantic_targets", []),
            "non_goals": patch.get("non_goals", []),
            "success_criteria": patch.get("success_criteria", []),
            "authority_targets": target_paths,
            "authority_target_decisions": result["authority_resolution"]["target_decisions"],
            "semantic_resolution": result.get("semantic_authority_resolution", {}),
            "semantic_target_decisions": result.get("semantic_authority_resolution", {}).get("target_decisions", []),
            "patch_chain": patch_chain,
            "debt_resolution": result.get("debt_resolution", {}),
            "freshness_resolution": result.get("freshness", {}),
        }
        result["metadata_json"] = {
            "runtime_surface": "governance_decision_log",
            "bootstrap_migration": str(DEFAULT_MIGRATION),
            "current_state_migration": str(CURRENT_STATE_MIGRATION),
            "authority_resolution_migration": str(AUTHORITY_RESOLUTION_MIGRATION),
            "patch_chain_migration": str(PATCH_CHAIN_MIGRATION),
            "debt_runtime_migration": str(DEBT_RUNTIME_MIGRATION),
            "semantic_authority_migration": str(SEMANTIC_AUTHORITY_MIGRATION),
            "freshness_migration": str(FRESHNESS_MIGRATION),
            "stale_snapshot": result["db_snapshot"].get("is_stale"),
            "freshness_status": result.get("freshness", {}).get("db_snapshot_status"),
            "defer_conditions": result["defer_conditions"],
        }

        if log_to_db:
            try:
                log_result = log_decision(
                    conn,
                    {
                        "decision_id": f"DEC-{uuid.uuid4().hex[:12].upper()}",
                        "patch_id": result["patch_id"] or "UNKNOWN",
                        "campaign_id": result.get("campaign_id"),
                        "requested_action": requested_action,
                        "decision": result["decision"],
                        "reason": result["reason"],
                        "blocking_conditions": result["blocking_conditions"],
                        "defer_conditions": result["defer_conditions"],
                        "warnings": result["warnings"],
                        "authority_resolution": result["authority_resolution"],
                        "dependency_resolution": result["dependency_resolution"],
                        "provenance_resolution": result["provenance_resolution"],
                        "validator_resolution": result["validator_resolution"],
                        "db_snapshot_at": result["db_snapshot"].get("latest_artifact_indexed_at"),
                        "operator": "scripts/query_governance.py",
                        "evidence_json": result["evidence_json"],
                        "metadata_json": result["metadata_json"],
                    },
                )
                result["log_written"] = True
                result["event_written"] = bool(log_result.get("event_written"))
                if log_result.get("full_evidence_path"):
                    result["external_evidence_path"] = log_result.get("full_evidence_path")
                if log_result.get("full_evidence_hash"):
                    result["external_evidence_hash"] = log_result.get("full_evidence_hash")
            except Exception as exc:
                result["log_written"] = False
                result["event_written"] = False
                result["log_error"] = str(exc)
                result["warnings"].append(f"Decision logging failed: {exc}")
    finally:
        conn.close()

    return result


def legacy_lookup(args):
    query = normalize_text(args.tech_note or args.theorem or args.tool or args.claim, lowercase=True)
    if args.open_gaps:
        query = query or "open_gaps"

    response = {
        "mode": "legacy_query_scaffold",
        "db_path": str(args.db),
        "requested": {
            "tech_note": args.tech_note,
            "theorem": args.theorem,
            "tool": args.tool,
            "claim": args.claim,
            "open_gaps": args.open_gaps,
        },
        "normalized_query": query,
        "note": "Use context-capsule for the minimal runtime summary and bounded replay reconciliation coverage, current-state for live state, freshness for snapshot age, authority --target for surface ownership, authority --semantic for semantic authority, patch-chain --patch-id <PATCH_ID> --level <summary|diagnostic|governance|forensic> [--summary] for dependency resolution, debt --status for debt projections, emit-event to append governance facts, events to query recorded facts, replay-events to reconstruct limited diagnostic state, reconcile-events to compare replay against registry authority, or patch-gate --patch-id <PATCH_ID> --target <path-or-surface> --level <summary|diagnostic|governance|forensic> [--summary] to invoke the governance runtime gate.",
        "results": [],
    }

    if not query:
        return response

    db_file = Path(args.db)
    if not db_file.exists():
        response["note"] = "Database file missing."
        return response

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT path, orientation_status, authority_scope, evidence_confidence, indexed_at
            FROM artifacts
            WHERE LOWER(path) LIKE ?
            ORDER BY path ASC, indexed_at DESC
            LIMIT 10
            """,
            (f"%{query.lower()}%",),
        ).fetchall()
        response["results"] = [dict(row) for row in rows]
    finally:
        conn.close()

    return response


def emit_json(payload, pretty=False, fallback_payload=None, serialization_warning=None):
    try:
        if pretty:
            text = json.dumps(payload, indent=2, ensure_ascii=False)
        else:
            text = json.dumps(payload, ensure_ascii=False)
    except (MemoryError, RecursionError) as exc:
        if fallback_payload is None:
            raise
        payload = dict(fallback_payload)
        payload["serialization_warning"] = serialization_warning or f"serialization_failed:{type(exc).__name__}"
        if pretty:
            text = json.dumps(payload, indent=2, ensure_ascii=False)
        else:
            text = json.dumps(payload, ensure_ascii=False)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8"))
        sys.stdout.flush()
    else:
        sys.stdout.write(text + "\n")


def build_current_state_result(args):
    state = build_current_state_capsule(args.db)
    if state["status"] == "unavailable":
        return state
    return state


def build_authority_resolution_result(args):
    semantic_key = str(getattr(args, "semantic", "") or "").strip()
    if semantic_key:
        return build_semantic_authority_resolution_result(args)

    db_file = Path(args.db)
    target = normalize_repo_path(args.target)
    requested_role = str(getattr(args, "authority_role", "") or "").strip().upper()
    result = {
        "mode": "authority_resolution",
        "db_path": str(db_file),
        "target": target,
        "authority_role": requested_role or None,
        "authority_owner": "unknown",
        "authority_source": None,
        "supersession": {
            "status": "unavailable",
            "superseded_by": [],
        },
        "conflict_state": "unavailable",
        "decision": "defer",
        "reason": "Authority resolution is unavailable.",
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(CURRENT_STATE_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(AUTHORITY_RESOLUTION_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
        "warnings": [],
    }

    if not db_file.exists():
        result["reason"] = "Governance DB file is missing."
        result["warnings"].append("The governance runtime database is unavailable.")
        return result

    if requested_role:
        if requested_role not in Q0_ROLE_IDS:
            result["decision"] = "block"
            result["reason"] = "Unknown authority role."
            result["warnings"].append("Use one of the governed Q0 authority roles.")
            return result
        role_result = resolve_role_aware_authority(requested_role, target=target)
        result.update(
            {
                "authority_source": role_result.get("authority_source"),
                "decision": role_result.get("decision", "defer"),
                "reason": role_result.get("reason", result["reason"]),
                "evidence_paths": role_result.get("evidence_paths", result["evidence_paths"]),
                "warnings": [warning for warning in dict.fromkeys(result["warnings"] + role_result.get("warnings", [])) if warning],
            }
        )
        result["authority_owner"] = infer_authority_owner_from_source(role_result.get("authority_source"))
        result["supersession"] = {"status": "current", "superseded_by": []}
        result["conflict_state"] = "clear" if result["decision"] == "allow" else "blocked"
        return result

    target_role = classify_target_role(target)
    if target_role:
        role_result = get_authority_by_role(target_role)
        result["decision"] = "block"
        result["reason"] = "Generic mixed-role authority lookup is prohibited for the Q0 partition."
        result["warnings"] = [
            f"Declare --authority-role {target_role} when querying governed Q0 authority surfaces.",
        ]
        result["authority_source"] = role_result.get("authority_source")
        result["conflict_state"] = "mixed"
        result["evidence_paths"] = role_result.get("evidence_paths", result["evidence_paths"])
        return result

    current_state = build_current_state_capsule(args.db)
    if current_state.get("warnings"):
        result["warnings"].extend(current_state["warnings"])
    if current_state.get("status") == "warn":
        result["warnings"].append("Current-state capsule reports warnings.")

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        ensure_runtime_schema(conn)
        catalog_rows = load_authority_resolution_catalog(conn)
    finally:
        conn.close()

    resolved = build_authority_resolution_record(target, current_state=current_state, catalog_rows=catalog_rows)
    result.update(
        {
            "authority_owner": resolved.get("authority_owner", "unknown"),
            "authority_source": resolved.get("authority_source"),
            "supersession": resolved.get("supersession", {"status": "unknown", "superseded_by": []}),
            "conflict_state": resolved.get("conflict_state", "unavailable"),
            "decision": resolved.get("decision", "defer"),
            "reason": resolved.get("reason", "Authority resolution is unavailable."),
            "evidence_paths": resolved.get("evidence_paths", result["evidence_paths"]),
            "warnings": [warning for warning in dict.fromkeys(result["warnings"] + resolved.get("warnings", [])) if warning],
        }
    )

    if not target:
        result["reason"] = "Authority resolution requires a target surface."
        result["decision"] = "defer"
    return result


def build_semantic_authority_resolution_result(args):
    db_file = Path(args.db)
    semantic_key = str(getattr(args, "semantic", "") or "").strip()
    semantic_type = str(getattr(args, "semantic_type", "") or "").strip() or None
    target = normalize_repo_path(getattr(args, "target", None))
    result = {
        "mode": "semantic_authority_resolution",
        "db_path": str(db_file),
        "target": target,
        "semantic_key": semantic_key or None,
        "semantic_type": semantic_type,
        "target_authority": None,
        "authority_owner": "unknown",
        "authority_source": None,
        "authority_rank": "unknown",
        "supersession": {
            "status": "unavailable",
            "superseded_by": [],
        },
        "conflict_state": "unavailable",
        "decision": "defer",
        "reason": "Semantic authority resolution is unavailable.",
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(SEMANTIC_AUTHORITY_MIGRATION.relative_to(ROOT)).replace("\\", "/") if SEMANTIC_AUTHORITY_MIGRATION.exists() else None,
            str(SEMANTIC_AUTHORITY_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
            str(CURRENT_STATE_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
        "warnings": [],
        "source": "unavailable",
    }

    if not semantic_key:
        result["reason"] = "Semantic authority resolution requires a semantic key."
        result["warnings"].append("No semantic key was supplied.")
        return result

    if not db_file.exists():
        result["reason"] = "Governance DB file is missing."
        result["warnings"].append("The governance runtime database is unavailable.")
        return result

    current_state = build_current_state_capsule(args.db)
    if current_state.get("warnings"):
        result["warnings"].extend(current_state["warnings"])
    if current_state.get("status") == "warn":
        result["warnings"].append("Current-state capsule reports warnings.")

    if target:
        result["target_authority"] = build_authority_resolution_result(
            argparse.Namespace(db=args.db, target=target, semantic=None, semantic_type=None)
        )
        target_authority = result["target_authority"] or {}
        if target_authority.get("warnings"):
            result["warnings"].extend(target_authority.get("warnings", []))
        if target_authority.get("evidence_paths"):
            result["evidence_paths"].extend(target_authority.get("evidence_paths", []))

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        ensure_runtime_schema(conn)
        catalog_rows = load_semantic_authority_catalog(conn)
    finally:
        conn.close()

    resolved = build_semantic_authority_record(semantic_key, semantic_type=semantic_type, current_state=current_state, catalog_rows=catalog_rows)
    result.update(
        {
            "semantic_key": resolved.get("semantic_key", semantic_key),
            "semantic_type": resolved.get("semantic_type", semantic_type),
            "authority_owner": resolved.get("authority_owner", "unknown"),
            "authority_source": resolved.get("authority_source"),
            "authority_rank": resolved.get("authority_rank", "unknown"),
            "supersession": resolved.get("supersession", {"status": "unknown", "superseded_by": []}),
            "conflict_state": resolved.get("conflict_state", "unavailable"),
            "decision": resolved.get("decision", "defer"),
            "reason": resolved.get("reason", "Semantic authority resolution is unavailable."),
            "evidence_paths": resolved.get("evidence_paths", result["evidence_paths"]),
            "warnings": [warning for warning in dict.fromkeys(result["warnings"] + resolved.get("warnings", [])) if warning],
            "source": resolved.get("source", "unavailable"),
        }
    )

    if target:
        result["target"] = target
    return result


def build_debt_runtime_result_for_args(args):
    current_state = build_current_state_capsule(args.db)
    return build_debt_runtime_result(
        args.db,
        target=getattr(args, "target", None),
        status_filter=getattr(args, "status", "all"),
        current_state=current_state,
    )


def build_context_capsule_result(db_path, target=None, task=None):
    capsule = build_governed_context_capsule_v1(db_path, target=target, task=task, query=None, limit=20, use_cache=True)
    current_state = capsule.get("current_state", {}) if isinstance(capsule, dict) else {}
    current_projection = current_state.get("projection", {}) if isinstance(current_state.get("projection"), dict) else {}
    freshness = capsule.get("freshness", {}) if isinstance(capsule, dict) else {}
    authority = capsule.get("authority", {}) if isinstance(capsule, dict) else {}
    patch_chain = capsule.get("patch_chain", {}) if isinstance(capsule, dict) else {}
    open_debt = capsule.get("open_debt", []) if isinstance(capsule, dict) else []
    open_debt_detail = capsule.get("open_debt_detail", {}) if isinstance(capsule, dict) else {}
    if not isinstance(open_debt_detail, dict):
        open_debt_detail = {}
    candidate_actions = capsule.get("candidate_actions", []) if isinstance(capsule, dict) else []
    recent_events = capsule.get("recent_governance_events", []) if isinstance(capsule, dict) else []
    semantic_summary = current_projection.get("semantic_rt", {}) if isinstance(current_projection, dict) else {}
    replay_projection = current_projection.get("replay_reconciliation", {}) if isinstance(current_projection, dict) else {}
    debt_summary = open_debt_detail.get("summary", {}) if isinstance(open_debt_detail.get("summary"), dict) else {}
    debt_items = open_debt if isinstance(open_debt, list) else []
    if not debt_items and isinstance(open_debt_detail.get("debts"), list):
        debt_items = open_debt_detail.get("debts", [])
    blocking_actions = [action for action in candidate_actions if action.get("priority") in {"high", "medium"}]
    warnings = _dedupe_trim(parse_json_collection(capsule.get("warnings", [])), limit=10)

    result = {
        "target": capsule.get("request_identity", {}).get("target"),
        "task": capsule.get("request_identity", {}).get("task"),
        "global_runtime_status": {
            "status": current_state.get("status", "unknown"),
            "health": current_state.get("health", {}).get("global_validation", capsule.get("database_health", {}).get("status", "unknown")) if isinstance(current_state.get("health"), dict) else capsule.get("database_health", {}).get("status", "unknown"),
            "db_first_gate": current_state.get("runtime", {}).get("db_first_gate", "unknown") if isinstance(current_state.get("runtime"), dict) else "unknown",
            "authority_boundary": current_state.get("runtime", {}).get("authority_boundary", "unknown") if isinstance(current_state.get("runtime"), dict) else "unknown",
            "snapshot": freshness.get("db_snapshot_status", "unknown"),
        },
        "freshness_summary": {
            "db_snapshot_status": freshness.get("db_snapshot_status", "unknown"),
            "decision": freshness.get("decision", "block"),
            "indexed_at": freshness.get("indexed_at"),
            "latest_known_worktree_change": freshness.get("latest_known_worktree_change"),
            "latest_runtime_only_worktree_change": freshness.get("latest_runtime_only_worktree_change"),
            "source_worktree_marker": freshness.get("source_worktree_marker"),
            "runtime_worktree_marker": freshness.get("runtime_worktree_marker"),
            "change_basis": freshness.get("change_basis", "unknown"),
            "staleness_cause": freshness.get("staleness_cause", "unknown"),
            "source_change_count": freshness.get("source_change_count", 0),
            "runtime_only_change_count": freshness.get("runtime_only_change_count", 0),
        },
        "authority_summary": {
            "target": authority.get("target"),
            "owner": authority.get("authority_owner", "unknown"),
            "source": authority.get("authority_source"),
            "decision": authority.get("decision", "defer"),
            "conflict": authority.get("conflict_state", "unknown"),
        },
        "patch_summary": {
            "patch_id": patch_chain.get("patch_id"),
            "status": patch_chain.get("status", "unknown"),
            "decision": patch_chain.get("decision", "defer"),
            "dependencies": len(patch_chain.get("dependencies", [])),
            "missing_dependencies": len(patch_chain.get("missing_dependencies", [])),
            "blockers": _dedupe_trim(patch_chain.get("blockers", []), limit=2),
        },
        "blocking_summary": {
            "count": len(blocking_actions),
            "items": [action.get("action_id") for action in blocking_actions[:3]],
            "defer": _dedupe_trim([action.get("reason") for action in blocking_actions], limit=3),
        },
        "debt_summary": {
            "open": debt_summary.get("open", 0),
            "partial": debt_summary.get("partial", 0),
            "resolved": debt_summary.get("resolved", 0),
            "blocking": debt_summary.get("blocking", 0),
            "items": [record.get("debt_id") for record in debt_items if isinstance(record, dict) and record.get("debt_id")][:3],
            "decision": open_debt_detail.get("decision", "allow"),
        },
        "replay_summary": {
            "state": replay_projection.get("projection_state", "unknown"),
            "boundary": replay_projection.get("boundary_state", "unknown"),
            "coverage_state": replay_projection.get("coverage_state", "unknown"),
            "subject_count": replay_projection.get("subject_count", 0),
            "event_count": replay_projection.get("event_count", 0),
            "latest_subject_id": replay_projection.get("latest_subject_id"),
            "latest_subject_type": replay_projection.get("latest_subject_type"),
            "latest_event_id": replay_projection.get("latest_event_id"),
            "latest_event_type": replay_projection.get("latest_event_type"),
            "latest_source_patch_id": replay_projection.get("latest_source_patch_id"),
            "latest_source_path": replay_projection.get("latest_source_path"),
            "latest_created_at": replay_projection.get("latest_created_at"),
        },
        "warnings": warnings,
        "required_validators": [
            "current-state",
            "freshness",
            "authority",
            "patch-chain",
            "debt",
            "patch-gate",
        ],
        "recommended_next_action": (
            f"{candidate_actions[0]['action_id']}: {candidate_actions[0]['reason']}"
            if candidate_actions
            else "Use the capsule to choose the next governed action."
        ),
        "minimal_evidence_paths": capsule.get("provenance", {}).get("source_paths", [])[:15],
        "schema_id": capsule.get("schema_id"),
        "schema_version": capsule.get("schema_version"),
        "capsule_schema_version": capsule.get("capsule_schema_version"),
        "capsule_id": capsule.get("capsule_id"),
        "capsule_hash": capsule.get("capsule_hash"),
        "cache_status": capsule.get("cache_status"),
        "metrics": capsule.get("metrics", {}),
        "recent_governance_events": recent_events,
        "governed_context_capsule_v1": capsule,
    }

    if not result["target"]:
        result.pop("target")
    if not result["task"]:
        result.pop("task")

    if semantic_summary:
        result["semantic_authority_summary"] = semantic_summary

    if current_state.get("status") == "unavailable":
        result["global_runtime_status"]["status"] = "unavailable"
        result["recommended_next_action"] = "Open the DB runtime first."

    return result


def build_context_capsule_result_for_args(args):
    return build_context_capsule_result(
        args.db,
        target=getattr(args, "target", None),
        task=getattr(args, "task", None),
    )


def build_freshness_result_for_args(args):
    current_state = build_current_state_capsule(args.db)
    db_snapshot_result = None
    db_file = Path(args.db)
    if db_file.exists():
        conn = sqlite3.connect(str(db_file), timeout=1.0)
        conn.row_factory = sqlite3.Row
        try:
            ensure_runtime_schema(conn)
            db_snapshot_result = db_snapshot(conn)
        finally:
            conn.close()
    result = build_db_snapshot_freshness_result(
        args.db,
        current_state=current_state,
        db_snapshot_result=db_snapshot_result,
        target=getattr(args, "target", None),
        target_paths=parse_json_collection(getattr(args, "target_paths", [])),
    )
    result["mode"] = "db_snapshot_freshness"
    result["db_path"] = str(db_file)
    return result


def build_emit_event_result_for_args(args):
    db_file = Path(args.db)
    payload_raw = getattr(args, "payload_json", None)
    payload, valid = _parse_governance_event_payload(payload_raw)
    if not valid:
        return {
            "mode": "governance_event_emit",
            "db_path": str(db_file),
            "status": "fail",
            "reason": "Invalid payload JSON.",
            "warnings": ["payload_json is not valid JSON."],
        }

    result = {
        "mode": "governance_event_emit",
        "db_path": str(db_file),
        "status": "success",
        "event": None,
        "warnings": [],
    }

    if not db_file.exists():
        result["status"] = "unavailable"
        result["reason"] = "Governance DB file is missing."
        result["warnings"].append("The governance runtime database is unavailable.")
        return result

    conn = sqlite3.connect(str(db_file), timeout=1.0)
    conn.row_factory = sqlite3.Row
    try:
        ensure_runtime_schema(conn)
        event = append_governance_event(
            conn,
            {
                "event_type": getattr(args, "event_type", None),
                "subject_id": getattr(args, "subject_id", None),
                "subject_type": getattr(args, "subject_type", None),
                "source_patch_id": getattr(args, "source_patch_id", None),
                "source_path": getattr(args, "source_path", None),
                "payload": payload,
                "evidence_paths": parse_json_collection(getattr(args, "evidence_path", [])),
            },
        )
        conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        result["status"] = "fail"
        result["reason"] = f"Failed to append governance event: {exc}"
        result["warnings"].append(str(exc))
        return result
    finally:
        conn.close()

    result["event"] = event
    result["evidence_paths"] = event.get("evidence_paths", []) if isinstance(event, dict) else []
    return result


def build_governance_events_result_for_args(args):
    return load_governance_event_records(
        args.db,
        event_type=getattr(args, "event_type", None),
        subject_id=getattr(args, "subject_id", None),
        source_patch_id=getattr(args, "source_patch_id", None),
        limit=getattr(args, "limit", 20),
    )


def build_replay_events_result_for_args(args):
    records = load_governance_event_records(
        args.db,
        event_type=getattr(args, "event_type", None),
        subject_id=getattr(args, "subject_id", None),
        source_patch_id=getattr(args, "source_patch_id", None),
        limit=getattr(args, "limit", 20),
    )
    result = replay_governance_events(records)
    result["mode"] = "governance_event_replay"
    result["db_path"] = str(Path(args.db))
    result["filters"] = {
        "event_type": getattr(args, "event_type", None),
        "subject_id": getattr(args, "subject_id", None),
        "source_patch_id": getattr(args, "source_patch_id", None),
        "limit": getattr(args, "limit", 20),
    }
    return result


def load_authority_snapshot_for_reconciliation(db_path, subject_id=None, patch_id=None):
    normalized_subject = str(subject_id or "").strip() or None
    normalized_patch_id = str(patch_id or "").strip() or None
    resolved_patch_id = normalized_patch_id
    if resolved_patch_id is None and normalized_subject and normalized_subject.startswith("PATCH_"):
        resolved_patch_id = normalized_subject

    if resolved_patch_id:
        patch_record, patch_path = load_patch_record_by_id(resolved_patch_id)
        if isinstance(patch_record, dict):
            return {
                "subject_id": resolved_patch_id,
                "authority_kind": "patch_registry",
                "authority_owner": "registry",
                "authority_source": normalize_repo_path(patch_path),
                "status": patch_record.get("status"),
                "applied_on": patch_record.get("applied_on"),
                "campaign_id": patch_record.get("campaign_id"),
                "title": patch_record.get("title"),
                "depends_on": patch_record.get("depends_on", []),
                "updated_artifacts": patch_record.get("updated_artifacts", []),
                "summary": patch_record.get("summary", {}),
                "validation": patch_record.get("validation", {}),
                "decision_boundary": patch_record.get("summary", {}).get("runtime", {}).get("authority_boundary"),
                "warnings": [],
                "evidence_paths": [
                    normalize_repo_path(patch_path),
                    str(GOVERNANCE_CHANGE_LEDGER.relative_to(ROOT)).replace("\\", "/"),
                ],
            }

    db_registry = load_optional_json(RESEARCH_DEBT_REGISTRY)
    if isinstance(db_registry, dict) and normalized_subject:
        for item in db_registry.get("debt_items", []):
            if not isinstance(item, dict):
                continue
            if str(item.get("id") or "").strip() != normalized_subject:
                continue
            return {
                "subject_id": normalized_subject,
                "authority_kind": "debt_registry",
                "authority_owner": "registry",
                "authority_source": str(RESEARCH_DEBT_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
                "status": item.get("status"),
                "severity": item.get("severity"),
                "department": item.get("department"),
                "type": item.get("type"),
                "resolution_priority": item.get("resolution_priority"),
                "required_resolution": item.get("required_resolution", []),
                "blocks": item.get("blocks", []),
                "warnings": [],
                "evidence_paths": [
                    str(RESEARCH_DEBT_REGISTRY.relative_to(ROOT)).replace("\\", "/"),
                ],
            }

    if normalized_subject:
        authority_result = build_authority_resolution_result(argparse.Namespace(db=db_path, target=normalized_subject))
        if authority_result.get("authority_source"):
            return {
                "subject_id": normalized_subject,
                "authority_kind": "authority_resolution",
                "authority_owner": authority_result.get("authority_owner", "unknown"),
                "authority_source": authority_result.get("authority_source"),
                "status": authority_result.get("decision"),
                "supersession": authority_result.get("supersession", {}),
                "conflict_state": authority_result.get("conflict_state"),
                "decision": authority_result.get("decision"),
                "reason": authority_result.get("reason"),
                "warnings": authority_result.get("warnings", []),
                "evidence_paths": authority_result.get("evidence_paths", []),
            }

    return {
        "subject_id": normalized_subject or normalized_patch_id,
        "authority_kind": "unavailable",
        "authority_owner": "unknown",
        "authority_source": None,
        "status": "unavailable",
        "warnings": ["No authority snapshot could be resolved for the requested subject."],
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
        ],
    }


def reconcile_governance_replay_with_authority(replay_result, authority_snapshot):
    result = {
        "subject_id": replay_result.get("subject_id") or authority_snapshot.get("subject_id"),
        "replay_state": replay_result.get("reconstructed_state", {}),
        "authority_state": authority_snapshot,
        "reconciliation": "unavailable",
        "differences": [],
        "warnings": [],
        "evidence_paths": [
            str(GLOBAL_HEALTH_REPORT.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_BUS_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_REPLAY_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
            str(EVENT_RECONCILIATION_MIGRATION.relative_to(ROOT)).replace("\\", "/"),
        ],
        "authority_note": "Registry remains authority; reconciliation only reports divergence.",
    }

    replay_state = result["replay_state"] if isinstance(result["replay_state"], dict) else {}
    authority_state = authority_snapshot if isinstance(authority_snapshot, dict) else {}

    if authority_state.get("authority_kind") == "unavailable":
        result["warnings"].extend(authority_state.get("warnings", []))
        result["reconciliation"] = "unavailable"
        result["evidence_paths"] = [path for path in dict.fromkeys(result["evidence_paths"] + authority_state.get("evidence_paths", [])) if path]
        return result

    if not replay_state or replay_state.get("status") in {"unavailable", None}:
        result["warnings"].append("Replay state is unavailable for comparison.")
        result["reconciliation"] = "unavailable"
        result["evidence_paths"] = [path for path in dict.fromkeys(result["evidence_paths"] + authority_state.get("evidence_paths", [])) if path]
        return result

    replay_subject = str(result["subject_id"] or "").strip() or None
    authority_subject = str(authority_state.get("subject_id") or "").strip() or None
    if replay_subject and authority_subject and replay_subject != authority_subject:
        result["differences"].append(
            {
                "field": "subject_id",
                "replay": replay_subject,
                "authority": authority_subject,
                "note": "Replay subject and authority subject differ.",
            }
        )

    replay_status = str(replay_state.get("status") or "unknown").strip().lower()
    authority_status = str(
        authority_state.get("status")
        or authority_state.get("decision")
        or authority_state.get("summary", {}).get("status")
        or "unknown"
    ).strip().lower()
    if replay_status and authority_status and replay_status != authority_status:
        result["differences"].append(
            {
                "field": "status",
                "replay": replay_status,
                "authority": authority_status,
                "note": "Replay state status diverges from registry authority.",
            }
        )

    replay_latest_event = replay_state.get("latest_event") or {}
    if replay_latest_event.get("source_patch_id") and authority_state.get("subject_id") and replay_latest_event.get("source_patch_id") != authority_state.get("subject_id"):
        result["differences"].append(
            {
                "field": "source_patch_id",
                "replay": replay_latest_event.get("source_patch_id"),
                "authority": authority_state.get("subject_id"),
                "note": "Latest replay event source patch differs from authority subject.",
            }
        )

    if "patches" in replay_state and authority_state.get("authority_kind") == "patch_registry":
        replay_patch_state = replay_state.get("patches", {}).get(authority_state.get("subject_id"), {})
        if isinstance(replay_patch_state, dict):
            replay_patch_status = str(replay_patch_state.get("status") or "unknown").strip().lower()
            registry_patch_status = str(authority_state.get("status") or "unknown").strip().lower()
            if replay_patch_status and registry_patch_status and replay_patch_status != registry_patch_status:
                result["differences"].append(
                    {
                        "field": "patch_status",
                        "replay": replay_patch_status,
                        "authority": registry_patch_status,
                        "note": "Replayed patch status differs from registry patch status.",
                    }
                )

            replay_dependencies = replay_patch_state.get("dependencies")
            authority_dependencies = authority_state.get("depends_on", [])
            if isinstance(replay_dependencies, list) and isinstance(authority_dependencies, list):
                if len(replay_dependencies) != len(authority_dependencies):
                    result["differences"].append(
                        {
                            "field": "dependency_count",
                            "replay": len(replay_dependencies),
                            "authority": len(authority_dependencies),
                            "note": "Replayed dependency count differs from registry patch record.",
                        }
                    )

    comparable_fields = 0
    if replay_status != "unknown" and authority_status != "unknown":
        comparable_fields += 1
    if replay_subject and authority_subject:
        comparable_fields += 1
    if authority_state.get("authority_kind") == "patch_registry" and authority_state.get("status") is not None:
        comparable_fields += 1

    if not comparable_fields:
        result["reconciliation"] = "unavailable"
    elif result["differences"]:
        result["reconciliation"] = "mismatch"
    elif replay_state.get("warnings") or authority_state.get("warnings"):
        result["reconciliation"] = "partial"
    else:
        result["reconciliation"] = "match"

    for difference in result["differences"]:
        result["warnings"].append(
            f"{difference.get('field', 'difference')} mismatch: replay={difference.get('replay')} authority={difference.get('authority')}."
        )
    result["warnings"].extend(replay_state.get("warnings", []))
    result["warnings"].extend(authority_state.get("warnings", []))
    result["evidence_paths"] = [path for path in dict.fromkeys(result["evidence_paths"] + replay_result.get("evidence_paths", []) + authority_state.get("evidence_paths", [])) if path]
    return result


def build_reconcile_events_result_for_args(args):
    subject_id = getattr(args, "subject_id", None) or getattr(args, "patch_id", None)
    patch_id = getattr(args, "patch_id", None) or subject_id
    event_type = getattr(args, "event_type", None)
    if getattr(args, "subject_id", None) and getattr(args, "patch_id", None) and str(args.subject_id).strip() != str(args.patch_id).strip():
        subject_warning = "subject-id and patch-id differ; replay uses subject-id and authority uses patch-id."
    else:
        subject_warning = None

    replay_args = argparse.Namespace(
        db=args.db,
        subject_id=subject_id,
        event_type=event_type,
        source_patch_id=None,
        limit=getattr(args, "limit", 20),
    )
    replay_result = build_replay_events_result_for_args(replay_args)
    authority_snapshot = load_authority_snapshot_for_reconciliation(args.db, subject_id=subject_id, patch_id=patch_id)
    result = reconcile_governance_replay_with_authority(replay_result, authority_snapshot)
    result["mode"] = "governance_event_reconciliation"
    result["db_path"] = str(Path(args.db))
    result["filters"] = {
        "subject_id": getattr(args, "subject_id", None),
        "patch_id": getattr(args, "patch_id", None),
        "event_type": event_type,
        "limit": getattr(args, "limit", 20),
    }
    if subject_warning:
        result["warnings"].insert(0, subject_warning)
    return result


def build_authority_scope_partition_result_for_args(args):
    bundle = build_q0_authority_scope_partition_bundle()
    bundle["mode"] = "authority_scope_partition"
    bundle["db_path"] = str(Path(args.db))
    bundle["selection_summary"] = {
        "cluster_id": bundle["partition"]["cluster_id"],
        "partition_id": bundle["partition"]["partition_id"],
        "resolved_record_count": bundle["partition"]["resolved_ambiguity_count"],
        "resolved_question_count": bundle["partition"]["resolved_question_count"],
        "remaining_blocking_ambiguities": bundle["partition"]["remaining_blocking_ambiguities"],
    }
    return bundle


def load_patch_input(args):
    if getattr(args, "patch_file", None):
        return load_patch_record_by_path(args.patch_file)
    if getattr(args, "patch_id", None):
        return load_patch_record_by_id(args.patch_id)
    return None, None


def build_patch_chain_result_for_args(args):
    current_state = build_current_state_capsule(args.db)
    ledger_index = load_governance_change_ledger_index()
    patch_id = getattr(args, "patch_id", None)
    patch, patch_source = load_patch_input(args)
    if not patch_id and isinstance(patch, dict):
        patch_id = patch.get("patch_id")
    result = build_patch_chain_result(patch_id, current_state=current_state, ledger_index=ledger_index)
    if patch_source:
        source_path = normalize_repo_path(patch_source)
        if source_path and source_path not in result["evidence_paths"]:
            result["evidence_paths"].insert(0, source_path)
    return result


def build_patch_gate_result(args):
    patch, patch_source = load_patch_input(args)
    if patch is None:
        patch = {
            "patch_id": getattr(args, "patch_id", None),
            "depends_on": [],
            "target_files": [],
            "required_repo_changes": [],
        }
    return evaluate_patch_gate(
        args.db,
        patch,
        patch_source_path=patch_source,
        requested_action=getattr(args, "requested_action", "propose"),
        log_to_db=not getattr(args, "no_log", False),
        target_override=getattr(args, "target", None),
    )


def main():
    parser = argparse.ArgumentParser(description="Query the governance database, resolve authority, or evaluate a patch gate.")
    parser.add_argument("command", nargs="?", help="Optional command. Use current-state or authority for live runtime capsules.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to the SQLite governance index.")
    parser.add_argument("--target", help="Path or governed surface to resolve with the authority command.")
    parser.add_argument("--authority-role", choices=list(Q0_ROLE_IDS), help="Required Q0 authority role for role-aware authority access.")
    parser.add_argument("--patch-id", help="Patch identifier for patch-chain, reconcile-events, or patch-gate commands.")
    parser.add_argument("--patch-file", help="Path to a JSON patch to evaluate through the governance runtime gate.")
    parser.add_argument("--status", default="all", choices=["open", "partial", "resolved", "blocking", "all"], help="Debt status filter for the debt command.")
    parser.add_argument("--requested-action", default="propose", help="Requested action label for the decision log.")
    parser.add_argument("--no-log", action="store_true", help="Do not write the decision to the governance log table.")
    parser.add_argument("--task", help="Optional task label for the context-capsule command.")
    parser.add_argument("--semantic", help="Semantic authority key for the authority command or patch-gate analysis.")
    parser.add_argument("--semantic-type", dest="semantic_type", help="Semantic authority type for semantic resolution.")
    parser.add_argument("--event-type", help="Event type for emit-event, events, replay-events, or reconcile-events commands.")
    parser.add_argument("--subject-id", help="Subject identifier for emit-event, events, replay-events, or reconcile-events commands.")
    parser.add_argument(
        "--subject-type",
        choices=["patch", "debt", "authority", "validation", "capsule", "db_snapshot", "runtime", "unknown"],
        help="Subject type for emit-event commands.",
    )
    parser.add_argument("--source-patch-id", help="Source patch identifier for emit-event or events commands.")
    parser.add_argument("--source-path", help="Source path for emit-event commands.")
    parser.add_argument("--payload-json", help="JSON payload for emit-event commands.")
    parser.add_argument("--evidence-path", action="append", help="Evidence path for emit-event commands.")
    parser.add_argument("--limit", type=int, default=20, help="Result limit for events queries.")
    parser.add_argument("--json", action="store_true", help="Explicit JSON output flag for compatibility with semantic authority queries.")
    parser.add_argument("--tech-note", help="Search tech notes by keyword.")
    parser.add_argument("--theorem", help="Lookup theorem by ID.")
    parser.add_argument("--tool", help="Lookup tool by ID.")
    parser.add_argument("--claim", help="Lookup claim by ID.")
    parser.add_argument("--open-gaps", action="store_true", help="List all open gaps.")
    parser.add_argument("--level", help="Evidence level: summary, diagnostic, governance, or forensic. Use --summary as a shortcut for summary.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--summary", action="store_true", help="Alias for --level summary.")

    args = parser.parse_args()
    requested_level = _resolve_requested_evidence_level(args)

    def emit_result(command_name, result):
        if requested_level is None:
            emit_json(result, pretty=args.pretty)
            return

        payload = build_evidence_level_result(command_name, result, requested_level)
        fallback_level = requested_level - 1 if requested_level > 0 else None
        fallback_payload = (
            build_evidence_level_result(command_name, result, fallback_level)
            if fallback_level is not None
            else None
        )
        if fallback_payload is not None:
            fallback_payload = _attach_evidence_level_metadata(
                fallback_payload,
                requested_level,
                fallback_level,
                fallback_from=requested_level,
            )
        emit_json(
            payload,
            pretty=args.pretty,
            fallback_payload=fallback_payload,
            serialization_warning=f"{command_name}_evidence_level_{_evidence_level_name(requested_level)}_serialization_failed",
        )

    if args.command == "current-state":
        result = build_current_state_result(args)
        emit_result("current-state", result)
        return

    if args.command == "authority":
        result = build_authority_resolution_result(args)
        emit_result("authority", result)
        return

    if args.command == "patch-chain":
        result = build_patch_chain_result_for_args(args)
        emit_result("patch-chain", result)
        return

    if args.command == "patch-gate":
        result = build_patch_gate_result(args)
        emit_result("patch-gate", result)
        return

    if args.command == "debt":
        result = build_debt_runtime_result_for_args(args)
        emit_result("debt", result)
        return

    if args.command == "freshness":
        result = build_freshness_result_for_args(args)
        emit_result("freshness", result)
        return

    if args.command == "context-capsule":
        result = build_context_capsule_result_for_args(args)
        emit_result("context-capsule", result)
        return

    if args.command == "emit-event":
        result = build_emit_event_result_for_args(args)
        emit_result("emit-event", result)
        return

    if args.command == "events":
        result = build_governance_events_result_for_args(args)
        emit_result("events", result)
        return

    if args.command == "replay-events":
        result = build_replay_events_result_for_args(args)
        emit_result("replay-events", result)
        return

    if args.command == "reconcile-events":
        result = build_reconcile_events_result_for_args(args)
        emit_result("reconcile-events", result)
        return

    if args.command == "authority-scope-partition":
        result = build_authority_scope_partition_result_for_args(args)
        emit_result("authority-scope-partition", result)
        return

    if args.patch_file:
        patch, patch_source = load_patch_input(args)
        result = evaluate_patch_gate(
            args.db,
            patch or {},
            patch_source_path=patch_source,
            requested_action=args.requested_action,
            log_to_db=not args.no_log,
            target_override=args.target,
        )
        emit_result("patch-file", result)
        return

    result = legacy_lookup(args)
    emit_result("legacy-lookup", result)


if __name__ == "__main__":
    main()
