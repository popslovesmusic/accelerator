from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from .reachability_evidence import (
    build_surface_indexes,
    classify_reachability,
    load_ambiguity_register,
    load_surface_inventory,
    normalize_path_like,
    normalized_basename,
    resolve_related_surface_ids,
    resolve_reference_paths,
)


AMBIGUITY_RISK_SCHEMA_ID = "governance_ambiguity_risk_classification_v1"
AMBIGUITY_RISK_SCHEMA_VERSION = "1.0.0"
CORE_RULE_ID = "GOVERNANCE_AMBIGUITY_REMEDIATION_ORDER_001"

RISK_DIMENSION_WEIGHTS = {
    "COMPETING_LIVE_AUTHORITY": 100,
    "WRITE_AUTHORITY_UNCLEAR": 90,
    "VALIDATION_AUTHORITY_UNCLEAR": 80,
    "AUTHORITY_LINEAGE_MISSING": 70,
    "LIVE_VERSUS_PROPOSAL_UNCLEAR": 60,
    "CURRENT_VERSUS_HISTORICAL_UNCLEAR": 50,
    "SOURCE_VERSUS_GENERATED_UNCLEAR": 40,
    "DUPLICATE_IDENTITY_UNCLEAR": 30,
    "DOCUMENTATION_ONLY": 10,
}

QUEUE_GROUP_ORDER = [
    "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS",
    "Q1_VALIDATION_AUTHORITY",
    "Q2_AUTHORITY_LINEAGE",
    "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION",
    "Q4_GENERATED_VIEW_BOUNDARY",
    "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION",
]

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

RESOLUTION_MODES = [
    "SELECT_CANONICAL_AUTHORITY",
    "PROVE_WRITE_OWNER",
    "PROVE_VALIDATOR_OWNER",
    "ESTABLISH_LINEAGE",
    "CLASSIFY_PROPOSAL",
    "CLASSIFY_HISTORICAL",
    "CLASSIFY_GENERATED_VIEW",
    "MERGE_IDENTITY_RECORDS",
    "DOCUMENT_ONLY",
]

ROOT = Path(__file__).resolve().parents[2]
CORE_RULE_PATH = ROOT / "governance" / "core_rules" / "GOVERNANCE_AMBIGUITY_REMEDIATION_ORDER_001.json"


def _normalize_unique(values: Sequence[Any]) -> list[str]:
    items = {normalize_path_like(value) for value in values if normalize_path_like(value)}
    return sorted(items)


def _duplicate_title_groups(indexes: Mapping[str, Any]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for key, records in indexes.get("by_title", {}).items():
        surface_ids = sorted({
            normalize_path_like(record.get("surface_id"))
            for record in records
            if normalize_path_like(record.get("surface_id"))
        })
        if len(surface_ids) > 1:
            groups[key] = surface_ids
    return groups


def _duplicate_basename_groups(indexes: Mapping[str, Any]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for key, records in indexes.get("by_basename", {}).items():
        surface_ids = sorted({
            normalize_path_like(record.get("surface_id"))
            for record in records
            if normalize_path_like(record.get("surface_id"))
        })
        if len(surface_ids) > 1:
            groups[key] = surface_ids
    return groups


def _core_rule_hash() -> str:
    return hashlib.sha256(CORE_RULE_PATH.read_bytes()).hexdigest()


def _provenance_missing(surface_record: Mapping[str, Any], ambiguity_record: Mapping[str, Any]) -> bool:
    return not surface_record.get("hash_or_version") or not surface_record.get("evidence") or not ambiguity_record.get("evidence")


def _resolved_related_paths(surface_record: Mapping[str, Any]) -> list[str]:
    related: list[str] = []
    for key in ("dependencies", "registry_references", "supersedes", "superseded_by"):
        values = surface_record.get(key)
        if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
            related.extend(normalize_path_like(value) for value in values if normalize_path_like(value))
    return sorted({value for value in related if value})


def _authority_candidates(
    surface_record: Mapping[str, Any],
    indexes: Mapping[str, Any],
    duplicate_title_groups: Mapping[str, list[str]],
    duplicate_basename_groups: Mapping[str, list[str]],
) -> list[str]:
    surface_id = normalize_path_like(surface_record.get("surface_id"))
    candidates = {surface_id} if surface_id else set()
    path_index = indexes.get("by_path", {})
    for reference in _resolved_related_paths(surface_record):
        candidates.update(resolve_reference_paths(reference, path_index))
    title_key = normalize_path_like(surface_record.get("title_or_name")).lower()
    if title_key in duplicate_title_groups:
        candidates.update(duplicate_title_groups[title_key])
    basename_key = normalized_basename(surface_record.get("path_or_table"))
    if basename_key in duplicate_basename_groups:
        candidates.update(duplicate_basename_groups[basename_key])
    return sorted(candidate for candidate in candidates if candidate)


def _risk_dimensions(
    ambiguity_record: Mapping[str, Any],
    surface_record: Mapping[str, Any],
    indexes: Mapping[str, Any],
    reachability: Mapping[str, Any],
    authority_candidates: Sequence[str],
    duplicate_title_groups: Mapping[str, list[str]],
    duplicate_basename_groups: Mapping[str, list[str]],
) -> list[str]:
    dimensions: list[str] = []
    authority_state = normalize_path_like(surface_record.get("authority_state")).upper()
    surface_type = normalize_path_like(surface_record.get("surface_type")).upper()
    if authority_state in {"EXPLICIT_LIVE_AUTHORITY", "IMPLIED_AUTHORITY"} and (
        len(authority_candidates) > 1
        or bool(reachability["write_reachable"])
        or bool(reachability["execution_reachable"])
    ):
        dimensions.append("COMPETING_LIVE_AUTHORITY")
    if reachability["write_reachable"] and authority_state != "EXPLICIT_NON_AUTHORITATIVE":
        dimensions.append("WRITE_AUTHORITY_UNCLEAR")
    if reachability["validation_reachable"]:
        dimensions.append("VALIDATION_AUTHORITY_UNCLEAR")
    if not _resolved_related_paths(surface_record):
        dimensions.append("AUTHORITY_LINEAGE_MISSING")
    if authority_state == "PROPOSAL":
        dimensions.append("LIVE_VERSUS_PROPOSAL_UNCLEAR")
    if authority_state == "HISTORICAL":
        dimensions.append("CURRENT_VERSUS_HISTORICAL_UNCLEAR")
    if authority_state == "GENERATED_VIEW":
        dimensions.append("SOURCE_VERSUS_GENERATED_UNCLEAR")
    title_key = normalize_path_like(surface_record.get("title_or_name")).lower()
    basename_key = normalized_basename(surface_record.get("path_or_table"))
    if (
        title_key in duplicate_title_groups
        or basename_key in duplicate_basename_groups
    ):
        dimensions.append("DUPLICATE_IDENTITY_UNCLEAR")
    if authority_state == "EXPLICIT_NON_AUTHORITATIVE" and not dimensions and surface_type in {"GENERATED_REPORT", "HISTORICAL_RECORD", "TEST"}:
        dimensions.append("DOCUMENTATION_ONLY")
    if not dimensions:
        dimensions.append("DOCUMENTATION_ONLY")
    return sorted(dict.fromkeys(dimensions))


def _queue_group(risk_dimensions: Sequence[str]) -> str:
    dims = set(risk_dimensions)
    if "COMPETING_LIVE_AUTHORITY" in dims or "WRITE_AUTHORITY_UNCLEAR" in dims:
        return "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS"
    if "VALIDATION_AUTHORITY_UNCLEAR" in dims:
        return "Q1_VALIDATION_AUTHORITY"
    if "LIVE_VERSUS_PROPOSAL_UNCLEAR" in dims or "CURRENT_VERSUS_HISTORICAL_UNCLEAR" in dims:
        return "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION"
    if "SOURCE_VERSUS_GENERATED_UNCLEAR" in dims:
        return "Q4_GENERATED_VIEW_BOUNDARY"
    if "AUTHORITY_LINEAGE_MISSING" in dims:
        return "Q2_AUTHORITY_LINEAGE"
    return "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION"


def _ambiguity_class(queue_group: str, risk_dimensions: Sequence[str]) -> str:
    dims = set(risk_dimensions)
    if queue_group == "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS":
        if "COMPETING_LIVE_AUTHORITY" in dims:
            return "COMPETING_LIVE_AUTHORITY"
        return "WRITE_AUTHORITY_UNCLEAR"
    if queue_group == "Q1_VALIDATION_AUTHORITY":
        return "VALIDATION_AUTHORITY_UNCLEAR"
    if queue_group == "Q2_AUTHORITY_LINEAGE":
        return "AUTHORITY_LINEAGE_MISSING"
    if queue_group == "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION":
        if "LIVE_VERSUS_PROPOSAL_UNCLEAR" in dims:
            return "LIVE_VERSUS_PROPOSAL_UNCLEAR"
        return "CURRENT_VERSUS_HISTORICAL_UNCLEAR"
    if queue_group == "Q4_GENERATED_VIEW_BOUNDARY":
        return "SOURCE_VERSUS_GENERATED_UNCLEAR"
    if "DUPLICATE_IDENTITY_UNCLEAR" in dims:
        return "DUPLICATE_IDENTITY_UNCLEAR"
    return "DOCUMENTATION_ONLY"


def _recommended_resolution_mode(queue_group: str, risk_dimensions: Sequence[str]) -> str:
    dims = set(risk_dimensions)
    if queue_group == "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS":
        return "SELECT_CANONICAL_AUTHORITY" if "COMPETING_LIVE_AUTHORITY" in dims else "PROVE_WRITE_OWNER"
    if queue_group == "Q1_VALIDATION_AUTHORITY":
        return "PROVE_VALIDATOR_OWNER"
    if queue_group == "Q2_AUTHORITY_LINEAGE":
        return "ESTABLISH_LINEAGE"
    if queue_group == "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION":
        return "CLASSIFY_PROPOSAL" if "LIVE_VERSUS_PROPOSAL_UNCLEAR" in dims else "CLASSIFY_HISTORICAL"
    if queue_group == "Q4_GENERATED_VIEW_BOUNDARY":
        return "CLASSIFY_GENERATED_VIEW"
    return "MERGE_IDENTITY_RECORDS" if "DUPLICATE_IDENTITY_UNCLEAR" in dims else "DOCUMENT_ONLY"


def _required_evidence(
    risk_dimensions: Sequence[str],
    reachability: Mapping[str, Any],
    provenance_missing: bool,
) -> list[str]:
    evidence: list[str] = []
    dim_set = set(risk_dimensions)
    if "COMPETING_LIVE_AUTHORITY" in dim_set:
        evidence.extend(["canonical_authority_selection", "candidate_set_trace"])
    if "WRITE_AUTHORITY_UNCLEAR" in dim_set:
        evidence.extend(["exclusive_write_owner", "mutation_path_trace"])
    if "VALIDATION_AUTHORITY_UNCLEAR" in dim_set:
        evidence.extend(["validator_owner", "acceptance_rule_trace"])
    if "AUTHORITY_LINEAGE_MISSING" in dim_set:
        evidence.extend(["predecessor_record", "successor_record", "supersession_trace"])
    if "LIVE_VERSUS_PROPOSAL_UNCLEAR" in dim_set:
        evidence.extend(["proposal_status_trace", "patch_registration_trace"])
    if "CURRENT_VERSUS_HISTORICAL_UNCLEAR" in dim_set:
        evidence.extend(["history_transition_trace", "archive_boundary_note"])
    if "SOURCE_VERSUS_GENERATED_UNCLEAR" in dim_set:
        evidence.extend(["source_binding", "generated_view_boundary_marker"])
    if "DUPLICATE_IDENTITY_UNCLEAR" in dim_set:
        evidence.extend(["identity_disambiguation", "logical_identity_trace"])
    if "DOCUMENTATION_ONLY" in dim_set:
        evidence.extend(["scope_note"])
    if provenance_missing:
        evidence.append("provenance_record")
    if not reachability.get("execution_reachable"):
        evidence.append("execution_anchor_trace")
    if not reachability.get("validation_reachable"):
        evidence.append("validation_anchor_trace")
    if not reachability.get("write_reachable"):
        evidence.append("write_owner_trace")
    return sorted(dict.fromkeys(evidence))


def _risk_score(
    risk_dimensions: Sequence[str],
    reachability: Mapping[str, Any],
    authority_candidates: Sequence[str],
    provenance_missing: bool,
    surface_record: Mapping[str, Any],
) -> int:
    score = sum(RISK_DIMENSION_WEIGHTS[dimension] for dimension in dict.fromkeys(risk_dimensions))
    if reachability.get("execution_reachable"):
        score += 40
    if reachability.get("write_reachable"):
        score += 60
    if reachability.get("validation_reachable"):
        score += 50
    if len(authority_candidates) > 1:
        score += 50
    if provenance_missing:
        score += 20
    if normalize_path_like(surface_record.get("authority_state")).upper() == "GENERATED_VIEW" and (
        reachability.get("execution_reachable") or reachability.get("validation_reachable")
    ):
        score += 40
    return score


def _severity_from_score(score: int, risk_dimensions: Sequence[str]) -> str:
    if score >= 100:
        return "CRITICAL"
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW" if risk_dimensions == ["DOCUMENTATION_ONLY"] else "MEDIUM"


def classify_ambiguity_record(
    ambiguity_record: Mapping[str, Any],
    surface_record: Mapping[str, Any],
    indexes: Mapping[str, Any],
) -> dict[str, Any]:
    reachability = classify_reachability(surface_record, indexes)
    duplicate_title_groups = _duplicate_title_groups(indexes)
    duplicate_basename_groups = _duplicate_basename_groups(indexes)
    authority_candidates = _authority_candidates(
        surface_record,
        indexes,
        duplicate_title_groups,
        duplicate_basename_groups,
    )
    risk_dimensions = _risk_dimensions(
        ambiguity_record,
        surface_record,
        indexes,
        reachability,
        authority_candidates,
        duplicate_title_groups,
        duplicate_basename_groups,
    )
    provenance_missing = _provenance_missing(surface_record, ambiguity_record)
    queue_group = _queue_group(risk_dimensions)
    risk_score = _risk_score(risk_dimensions, reachability, authority_candidates, provenance_missing, surface_record)
    severity = _severity_from_score(risk_score, risk_dimensions)
    source_id = normalize_path_like(ambiguity_record.get("surface_id")) or normalize_path_like(surface_record.get("surface_id"))
    path = normalize_path_like(surface_record.get("path_or_table"))
    related_paths = _resolved_related_paths(surface_record)
    affected_surfaces = _normalize_unique([path, *related_paths])
    unique_basename = normalized_basename(path)
    return {
        "ambiguity_id": f"AMB-{source_id}",
        "source_record_id": source_id,
        "surface_id": source_id,
        "ambiguity_class": _ambiguity_class(queue_group, risk_dimensions),
        "path_or_table": path,
        "surface_type": normalize_path_like(surface_record.get("surface_type")).upper(),
        "title_or_name": normalize_path_like(surface_record.get("title_or_name")),
        "authority_state": normalize_path_like(surface_record.get("authority_state")).upper(),
        "storage_state": normalize_path_like(surface_record.get("storage_state")).upper(),
        "affected_surfaces": affected_surfaces,
        "risk_dimensions": risk_dimensions,
        "risk_score": risk_score,
        "severity": severity,
        "execution_reachable": bool(reachability["execution_reachable"]),
        "execution_reachability_status": reachability["execution_reachability_status"],
        "write_reachable": bool(reachability["write_reachable"]),
        "write_reachability_status": reachability["write_reachability_status"],
        "validation_reachable": bool(reachability["validation_reachable"]),
        "validation_reachability_status": reachability["validation_reachability_status"],
        "authority_candidates": authority_candidates,
        "required_evidence": _required_evidence(risk_dimensions, reachability, provenance_missing),
        "recommended_resolution_mode": _recommended_resolution_mode(queue_group, risk_dimensions),
        "queue_group": queue_group,
        "queue_position": 0,
        "status": "QUEUED",
        "provenance_missing": provenance_missing,
        "direct_related_paths": related_paths,
        "identity_basis": {
            "title": normalize_path_like(surface_record.get("title_or_name")).lower(),
            "basename": unique_basename,
        },
    }


def build_ambiguity_risk_classification(
    surface_inventory: Mapping[str, Any] | None = None,
    ambiguity_register: Mapping[str, Any] | None = None,
    *,
    source_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    surface_payload = dict(surface_inventory or load_surface_inventory())
    ambiguity_payload = dict(ambiguity_register or load_ambiguity_register())
    surface_records = surface_payload.get("records", [])
    ambiguity_records = ambiguity_payload.get("ambiguities", [])
    indexes = build_surface_indexes(surface_records)
    classification_records: list[dict[str, Any]] = []
    for ambiguity_record in ambiguity_records:
        surface_id = normalize_path_like(ambiguity_record.get("surface_id"))
        surface_record = indexes["by_id"].get(surface_id)
        if not surface_record:
            continue
        classification_records.append(classify_ambiguity_record(ambiguity_record, surface_record, indexes))
    classification_records.sort(key=lambda record: record["ambiguity_id"])
    counts_by_queue = Counter(record["queue_group"] for record in classification_records)
    counts_by_severity = Counter(record["severity"] for record in classification_records)
    counts_by_dimension = Counter(dimension for record in classification_records for dimension in record["risk_dimensions"])
    counts_by_resolution = Counter(record["recommended_resolution_mode"] for record in classification_records)
    counts_by_class = Counter(record["ambiguity_class"] for record in classification_records)
    basis = {
        "schema_id": AMBIGUITY_RISK_SCHEMA_ID,
        "schema_version": AMBIGUITY_RISK_SCHEMA_VERSION,
        "core_rule_reference": {
            "rule_id": CORE_RULE_ID,
            "hash": _core_rule_hash(),
        },
        "record_count": len(classification_records),
        "records": [
            {
                "ambiguity_id": record["ambiguity_id"],
                "source_record_id": record["source_record_id"],
                "ambiguity_class": record["ambiguity_class"],
                "risk_dimensions": record["risk_dimensions"],
                "risk_score": record["risk_score"],
                "severity": record["severity"],
                "queue_group": record["queue_group"],
                "recommended_resolution_mode": record["recommended_resolution_mode"],
            }
            for record in classification_records
        ],
    }
    logical = json.dumps(basis, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result = {
        "schema_id": AMBIGUITY_RISK_SCHEMA_ID,
        "schema_version": AMBIGUITY_RISK_SCHEMA_VERSION,
        "core_rule_reference": {
            "rule_id": CORE_RULE_ID,
            "path": "governance/core_rules/GOVERNANCE_AMBIGUITY_REMEDIATION_ORDER_001.json",
            "hash": _core_rule_hash(),
        },
        "record_count": len(classification_records),
        "counts": {
            "queue_groups": dict(counts_by_queue),
            "severity": dict(counts_by_severity),
            "risk_dimensions": dict(counts_by_dimension),
            "resolution_modes": dict(counts_by_resolution),
            "ambiguity_class": dict(counts_by_class),
        },
        "source_snapshot": dict(source_snapshot or {}),
        "records": classification_records,
        "logical_hash": hashlib.sha256(logical).hexdigest(),
    }
    return result
