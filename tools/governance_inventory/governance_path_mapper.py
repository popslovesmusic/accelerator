from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .authority_candidate_inventory import build_authority_candidate_inventory
from .q0_cluster_selector import PATCH_ID, select_q0_resolution_cluster
from .reachability_evidence import normalize_path_like


ROOT = Path(__file__).resolve().parents[2]
PATH_SCHEMA_ID = "governance_q0_path_maps_v1"
PATH_SCHEMA_VERSION = "1.0.0"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def logical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _entry_point(path: str) -> str:
    if path.startswith("scripts/") and path.endswith(".py"):
        module = path[:-3].replace("/", ".")
        return f"python -m {module}"
    return path


def _transaction_boundary(surface_type: str, path: str) -> str:
    if path.startswith("registry/db/"):
        return "sqlite transaction"
    if path.startswith("registry/"):
        return "registry file transaction"
    if path.startswith("scripts/"):
        return "runtime validation transaction"
    if path.startswith("governance/live/"):
        return "live governance file transaction"
    return f"{surface_type.lower()} file transaction"


def _write_operation_types(surface_type: str, path: str) -> list[str]:
    if path == "scripts/global_validate.py":
        return ["APPEND", "UPDATE"]
    if path == "scripts/query_governance.py":
        return ["UPDATE", "APPEND"]
    if path == "registry/governance_change_ledger.json":
        return ["APPEND", "UPDATE"]
    if path == "registry/governance_hash_registry.json":
        return ["UPDATE", "APPEND"]
    if path.startswith("registry/db/"):
        return ["APPEND", "UPDATE"]
    if surface_type in {"ENFORCEMENT_CODE", "LEDGER"}:
        return ["UPDATE", "APPEND"]
    if surface_type in {"REGISTRY", "SSOT"}:
        return ["UPDATE"]
    return ["UPDATE"]


def _validator_rule_ids() -> list[str]:
    return [
        "GOVERNANCE_Q0_CLUSTER_COHERENCE_001",
        "GOVERNANCE_AMBIGUITY_REMEDIATION_ORDER_001",
        "GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001",
    ]


def _candidate_sources_for(surface_id: str, cluster_path_map: Mapping[str, str]) -> list[str]:
    mapping = {
        "GOV-SURF-0972": [
            "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            "registry/governance_change_ledger.json",
            "registry/governance_hash_registry.json",
            "scripts/query_governance.py",
        ],
        "GOV-SURF-0881": [
            "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            "registry/governance_hash_registry.json",
            "scripts/global_validate.py",
            "scripts/query_governance.py",
        ],
        "GOV-SURF-0994": [
            "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            "registry/governance_change_ledger.json",
            "registry/governance_hash_registry.json",
            "scripts/global_validate.py",
        ],
        "GOV-SURF-0005": [
            "scripts/global_validate.py",
            "scripts/query_governance.py",
        ],
        "GOV-SURF-0123": [
            "AGENTS.md",
            "GEMINI.md",
            "scripts/global_validate.py",
        ],
        "GOV-SURF-0001": [
            "GEMINI.md",
            "scripts/global_validate.py",
        ],
        "GOV-SURF-0002": [
            "AGENTS.md",
            "scripts/global_validate.py",
        ],
        "GOV-SURF-0132": [
            "scripts/global_validate.py",
            "registry/tool_manifest.json",
        ],
        "GOV-SURF-0134": [
            "AGENTS.md",
            "registry/governance_change_ledger.json",
        ],
        "GOV-SURF-0103": [
            "registry/governance_change_ledger.json",
        ],
    }
    return sorted({normalize_path_like(item) for item in mapping.get(surface_id, cluster_path_map.values()) if normalize_path_like(item)})


def _selection_rule(surface_id: str) -> str:
    if surface_id in {"GOV-SURF-0972", "GOV-SURF-0881", "GOV-SURF-0994", "GOV-SURF-0005"}:
        return "prefer the shortest direct dependency path inside the selected cluster; fail closed when the path is ambiguous."
    if surface_id in {"GOV-SURF-0123", "GOV-SURF-0001", "GOV-SURF-0002", "GOV-SURF-0132", "GOV-SURF-0134"}:
        return "prefer the live instruction or registry surface already referenced by the selected cluster; fail closed on disagreement."
    return "fail closed and surface the ambiguity for the next resolution patch."


def _fallback_behavior(surface_id: str) -> str:
    if surface_id == "GOV-SURF-0103":
        return "block and preserve the architecture record as non-authoritative evidence."
    return "block and preserve all existing authorities."


def build_write_path_map(candidate_inventory: Mapping[str, Any]) -> dict[str, Any]:
    records = list(candidate_inventory.get("records", []))
    selected_cluster = candidate_inventory.get("cluster_schema_reference", {})
    path_map: list[dict[str, Any]] = []
    for record in records:
        path = normalize_path_like(record["path"])
        surface_type = normalize_path_like(record["surface_type"]).upper()
        path_map.append(
            {
                "writer_id": record["surface_id"],
                "writer_path": path,
                "entry_point": _entry_point(path),
                "target": path,
                "operation_types": _write_operation_types(surface_type, path),
                "authorization_source": record["current_classification"],
                "transaction_boundary": _transaction_boundary(surface_type, path),
                "validation_before_write": True,
                "validation_after_write": True,
                "active_status": "ACTIVE",
                "queue_position": int(record["queue_position"]),
                "cluster_id": selected_cluster.get("cluster_id"),
            }
        )
    path_map.sort(key=lambda record: (record["queue_position"], record["writer_id"]))
    basis = {
        "schema_id": PATH_SCHEMA_ID,
        "schema_version": PATH_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "kind": "write",
        "cluster_id": selected_cluster.get("cluster_id"),
        "records": [dict(record) for record in path_map],
    }
    return {
        "schema_id": PATH_SCHEMA_ID,
        "schema_version": PATH_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "kind": "write",
        "cluster_id": selected_cluster.get("cluster_id"),
        "record_count": len(path_map),
        "records": path_map,
        "logical_hash": logical_sha256(basis),
    }


def build_read_path_map(candidate_inventory: Mapping[str, Any]) -> dict[str, Any]:
    records = list(candidate_inventory.get("records", []))
    cluster_path_map = {record["surface_id"]: record["path"] for record in records}
    read_map: list[dict[str, Any]] = []
    for record in records:
        path = normalize_path_like(record["path"])
        read_map.append(
            {
                "consumer_id": record["surface_id"],
                "consumer_path": path,
                "entry_point": _entry_point(path),
                "lookup_key": "governance-validation-control-plane",
                "candidate_sources": _candidate_sources_for(record["surface_id"], cluster_path_map),
                "selection_rule": _selection_rule(record["surface_id"]),
                "fallback_behavior": _fallback_behavior(record["surface_id"]),
                "active_status": "ACTIVE",
                "queue_position": int(record["queue_position"]),
            }
        )
    read_map.sort(key=lambda record: (record["queue_position"], record["consumer_id"]))
    basis = {
        "schema_id": PATH_SCHEMA_ID,
        "schema_version": PATH_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "kind": "read",
        "cluster_id": candidate_inventory.get("cluster_schema_reference", {}).get("cluster_id"),
        "records": [dict(record) for record in read_map],
    }
    return {
        "schema_id": PATH_SCHEMA_ID,
        "schema_version": PATH_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "kind": "read",
        "cluster_id": candidate_inventory.get("cluster_schema_reference", {}).get("cluster_id"),
        "record_count": len(read_map),
        "records": read_map,
        "logical_hash": logical_sha256(basis),
    }


def build_validation_path_map(candidate_inventory: Mapping[str, Any], selected_cluster: Mapping[str, Any]) -> dict[str, Any]:
    records = [dict(record) for record in candidate_inventory.get("records", []) if record.get("validation_reachable")]
    validation_map: list[dict[str, Any]] = []
    cluster_ids = [record["surface_id"] for record in selected_cluster.get("included_records", [])]
    for record in records:
        path = normalize_path_like(record["path"])
        validation_map.append(
            {
                "validator_id": record["surface_id"],
                "validator_path": path,
                "entry_point": _entry_point(path),
                "validated_target": selected_cluster.get("governed_domain", {}).get("domain_id", "governance-validation-control-plane"),
                "governing_rule_ids": _validator_rule_ids(),
                "terminal_status_effect": {
                    "inventory_completion_gate": "BLOCKED",
                    "patch_006_resolution_gate": "PASS",
                    "reason": "The cluster remains evidentiary only until a later authority-resolution patch proves exclusive ownership.",
                },
                "candidate_authority_dependencies": [
                    dependency
                    for dependency in cluster_ids
                    if dependency != record["surface_id"]
                ],
                "active_status": "ACTIVE",
                "queue_position": int(record["queue_position"]),
            }
        )
    validation_map.sort(key=lambda record: (record["queue_position"], record["validator_id"]))
    basis = {
        "schema_id": PATH_SCHEMA_ID,
        "schema_version": PATH_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "kind": "validation",
        "cluster_id": candidate_inventory.get("cluster_schema_reference", {}).get("cluster_id"),
        "records": [dict(record) for record in validation_map],
    }
    return {
        "schema_id": PATH_SCHEMA_ID,
        "schema_version": PATH_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "kind": "validation",
        "cluster_id": candidate_inventory.get("cluster_schema_reference", {}).get("cluster_id"),
        "record_count": len(validation_map),
        "records": validation_map,
        "logical_hash": logical_sha256(basis),
    }
