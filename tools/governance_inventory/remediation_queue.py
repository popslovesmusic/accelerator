from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ambiguity_risk import (
    AMBIGUITY_RISK_SCHEMA_ID,
    AMBIGUITY_RISK_SCHEMA_VERSION,
    QUEUE_GROUP_ORDER,
    SEVERITY_ORDER,
    build_ambiguity_risk_classification,
)
from .reachability_evidence import load_ambiguity_register, load_surface_inventory


REMEDIATION_QUEUE_SCHEMA_ID = "governance_remediation_queue_v1"
REMEDIATION_QUEUE_SCHEMA_VERSION = "1.0.0"


def _queue_sort_key(record: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        QUEUE_GROUP_ORDER.index(record["queue_group"]),
        SEVERITY_ORDER.index(record["severity"]),
        -int(record["risk_score"]),
        0 if record["write_reachable"] else 1,
        0 if record["validation_reachable"] else 1,
        0 if record["execution_reachable"] else 1,
        -len(record["authority_candidates"]),
        record["ambiguity_id"],
    )


def sort_queue_records(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    ordered: list[dict[str, Any]] = [dict(record) for record in records]
    ordered.sort(key=_queue_sort_key)
    for index, record in enumerate(ordered, start=1):
        record["queue_position"] = index
    return ordered


def build_remediation_queue_bundle(
    surface_inventory: Mapping[str, Any] | None = None,
    ambiguity_register: Mapping[str, Any] | None = None,
    *,
    source_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    classification = build_ambiguity_risk_classification(
        surface_inventory or load_surface_inventory(),
        ambiguity_register or load_ambiguity_register(),
        source_snapshot=source_snapshot,
    )
    queue_records = sort_queue_records(classification["records"])
    counts_by_queue = Counter(record["queue_group"] for record in queue_records)
    counts_by_severity = Counter(record["severity"] for record in queue_records)
    counts_by_dimension = Counter(dimension for record in queue_records for dimension in record["risk_dimensions"])
    counts_by_resolution = Counter(record["recommended_resolution_mode"] for record in queue_records)
    counts_by_class = Counter(record["ambiguity_class"] for record in queue_records)
    basis = {
        "schema_id": REMEDIATION_QUEUE_SCHEMA_ID,
        "schema_version": REMEDIATION_QUEUE_SCHEMA_VERSION,
        "core_rule_reference": classification["core_rule_reference"],
        "record_count": len(queue_records),
        "records": [
            {
                "queue_position": record["queue_position"],
                "ambiguity_id": record["ambiguity_id"],
                "ambiguity_class": record["ambiguity_class"],
                "queue_group": record["queue_group"],
                "severity": record["severity"],
                "risk_score": record["risk_score"],
                "risk_dimensions": record["risk_dimensions"],
                "authority_candidates": record["authority_candidates"],
                "recommended_resolution_mode": record["recommended_resolution_mode"],
                "write_reachable": record["write_reachable"],
                "validation_reachable": record["validation_reachable"],
                "execution_reachable": record["execution_reachable"],
            }
            for record in queue_records
        ],
    }
    logical = json.dumps(basis, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema_id": REMEDIATION_QUEUE_SCHEMA_ID,
        "schema_version": REMEDIATION_QUEUE_SCHEMA_VERSION,
        "source_classification_schema_id": AMBIGUITY_RISK_SCHEMA_ID,
        "source_classification_schema_version": AMBIGUITY_RISK_SCHEMA_VERSION,
        "core_rule_reference": classification["core_rule_reference"],
        "record_count": len(queue_records),
        "counts": {
            "queue_groups": dict(counts_by_queue),
            "severity": dict(counts_by_severity),
            "risk_dimensions": dict(counts_by_dimension),
            "resolution_modes": dict(counts_by_resolution),
            "ambiguity_class": dict(counts_by_class),
        },
        "source_snapshot": dict(source_snapshot or classification.get("source_snapshot") or {}),
        "records": queue_records,
        "logical_hash": hashlib.sha256(logical).hexdigest(),
        "classification_logical_hash": classification["logical_hash"],
    }
