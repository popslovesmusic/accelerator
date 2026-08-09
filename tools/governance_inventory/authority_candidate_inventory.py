from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from .q0_cluster_selector import (
    PATCH_ID,
    Q0_CLUSTER_SCHEMA_ID,
    Q0_CLUSTER_SCHEMA_VERSION,
    select_q0_resolution_cluster,
)
from .reachability_evidence import build_surface_indexes, classify_reachability, normalize_path_like


ROOT = Path(__file__).resolve().parents[2]
AUTHORITIES_SCHEMA_ID = "governance_q0_authority_candidates_v1"
AUTHORITIES_SCHEMA_VERSION = "1.0.0"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def logical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _load_json(relative_path: str) -> dict[str, Any]:
    payload = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _surface_index(surface_inventory: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return build_surface_indexes(surface_inventory.get("records", []))["by_id"]


def _selected_surface_ids(cluster: Mapping[str, Any]) -> list[str]:
    return [record["surface_id"] for record in sorted(cluster.get("included_records", []), key=lambda item: (int(item["queue_position"]), item["ambiguity_id"]))]


def _incoming_dependent_count(surface_record: Mapping[str, Any]) -> int:
    dependents = surface_record.get("dependents", [])
    return len([item for item in dependents if normalize_path_like(item)])


def _outbound_reference_count(surface_record: Mapping[str, Any]) -> int:
    outbound = {
        normalize_path_like(value)
        for key in ("dependencies", "registry_references")
        for value in (surface_record.get(key) or [])
        if normalize_path_like(value)
    }
    return len(outbound)


def _lineage_status(surface_record: Mapping[str, Any], cluster_surface_ids: Sequence[str]) -> str:
    if surface_record.get("supersedes") or surface_record.get("superseded_by"):
        return "EXPLICIT_SUPERSESSION"
    if surface_record.get("surface_id") == "GOV-SURF-0103":
        return "INDIRECT_REFERENCE_ONLY"
    if any(normalize_path_like(value) for value in surface_record.get("dependencies", [])):
        return "REFERENCE_ONLY"
    if any(surface_id != surface_record.get("surface_id") for surface_id in cluster_surface_ids):
        return "REFERENCE_ONLY"
    return "MISSING_EXPLICIT_LINEAGE"


def _candidate_authority_record(
    surface_record: Mapping[str, Any],
    queue_record: Mapping[str, Any],
    cluster_surface_ids: Sequence[str],
) -> dict[str, Any]:
    reachability = classify_reachability(surface_record, {"by_id": {}})
    claimed_scope = normalize_path_like(surface_record.get("declared_scope")) or "unknown"
    evidence = list(surface_record.get("evidence") or [])
    read_reachable = bool(
        _incoming_dependent_count(surface_record)
        or _outbound_reference_count(surface_record)
        or reachability["execution_reachable"]
        or reachability["validation_reachable"]
    )
    return {
        "ambiguity_id": queue_record["ambiguity_id"],
        "queue_position": int(queue_record["queue_position"]),
        "surface_id": normalize_path_like(surface_record.get("surface_id")),
        "path": normalize_path_like(surface_record.get("path_or_table")),
        "surface_type": normalize_path_like(surface_record.get("surface_type")).upper(),
        "current_classification": normalize_path_like(surface_record.get("authority_state")).upper(),
        "hash_or_version": normalize_path_like(surface_record.get("hash_or_version")),
        "declared_scope": claimed_scope,
        "claimed_scope": claimed_scope,
        "provenance_status": "VERIFIED" if normalize_path_like(surface_record.get("hash_or_version")) and evidence else "MISSING",
        "lineage_status": _lineage_status(surface_record, cluster_surface_ids),
        "read_reachable": read_reachable,
        "write_reachable": bool(reachability["write_reachable"]),
        "validation_reachable": bool(reachability["validation_reachable"]),
        "active_consumer_count": _incoming_dependent_count(surface_record),
        "active_writer_count": _outbound_reference_count(surface_record),
        "evidence": [
            {
                "path": normalize_path_like(item.get("path")),
                "location": normalize_path_like(item.get("location")),
                "evidence_type": normalize_path_like(item.get("evidence_type")),
            }
            for item in evidence
        ],
    }


def build_authority_candidate_inventory(
    cluster: Mapping[str, Any] | None = None,
    *,
    surface_inventory: Mapping[str, Any] | None = None,
    queue_bundle: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    selected_cluster = dict(cluster or select_q0_resolution_cluster(surface_inventory=surface_inventory, queue_bundle=queue_bundle))
    surface_payload = dict(surface_inventory or _load_json("outputs/governance_inventory/governance_surface_inventory.json"))
    queue_payload = dict(queue_bundle or _load_json("outputs/governance_inventory/governance_remediation_queue.json"))
    q0_records = [dict(record) for record in queue_payload.get("records", []) if record.get("queue_group") == "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS"]
    q0_records.sort(key=lambda record: (int(record["queue_position"]), record["ambiguity_id"]))
    queue_by_id = {record["source_record_id"]: record for record in q0_records}
    surface_index = _surface_index(surface_payload)
    cluster_surface_ids = _selected_surface_ids(selected_cluster)

    candidate_records: list[dict[str, Any]] = []
    for surface_id in cluster_surface_ids:
        surface_record = surface_index[surface_id]
        queue_record = queue_by_id[surface_id]
        candidate_records.append(_candidate_authority_record(surface_record, queue_record, cluster_surface_ids))

    counts = {
        "candidate_count": len(candidate_records),
        "read_reachable": sum(1 for record in candidate_records if record["read_reachable"]),
        "write_reachable": sum(1 for record in candidate_records if record["write_reachable"]),
        "validation_reachable": sum(1 for record in candidate_records if record["validation_reachable"]),
        "provenance_verified": sum(1 for record in candidate_records if record["provenance_status"] == "VERIFIED"),
        "lineage_reference_only": sum(1 for record in candidate_records if record["lineage_status"] == "REFERENCE_ONLY"),
        "lineage_indirect": sum(1 for record in candidate_records if record["lineage_status"] == "INDIRECT_REFERENCE_ONLY"),
        "lineage_explicit_supersession": sum(1 for record in candidate_records if record["lineage_status"] == "EXPLICIT_SUPERSESSION"),
    }
    basis = {
        "schema_id": AUTHORITIES_SCHEMA_ID,
        "schema_version": AUTHORITIES_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "cluster_id": selected_cluster["cluster_id"],
        "candidate_records": [dict(record) for record in candidate_records],
    }

    return {
        "schema_id": AUTHORITIES_SCHEMA_ID,
        "schema_version": AUTHORITIES_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "cluster_schema_reference": {
            "schema_id": Q0_CLUSTER_SCHEMA_ID,
            "schema_version": Q0_CLUSTER_SCHEMA_VERSION,
            "cluster_id": selected_cluster["cluster_id"],
        },
        "record_count": len(candidate_records),
        "counts": counts,
        "records": candidate_records,
        "logical_hash": logical_sha256(basis),
    }
