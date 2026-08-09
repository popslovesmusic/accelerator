from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .q0_cluster_selector import PATCH_ID
from .reachability_evidence import normalize_path_like


ROOT = Path(__file__).resolve().parents[2]
LINEAGE_SCHEMA_ID = "governance_q0_lineage_map_v1"
LINEAGE_SCHEMA_VERSION = "1.0.0"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def logical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def build_q0_lineage_map(
    selected_cluster: Mapping[str, Any],
    relationship_artifact: Mapping[str, Any],
) -> dict[str, Any]:
    cluster_ids = {record["surface_id"] for record in selected_cluster.get("included_records", [])}
    relationships: list[dict[str, Any]] = []
    missing_lineage: list[dict[str, Any]] = []
    for relationship in relationship_artifact.get("relationships", []):
        source = normalize_path_like(relationship.get("from"))
        target = normalize_path_like(relationship.get("to"))
        if source in cluster_ids and target in cluster_ids:
            relationships.append(
                {
                    "from": source,
                    "to": target,
                    "relation_type": normalize_path_like(relationship.get("relation_type")),
                    "evidence": normalize_path_like(relationship.get("evidence")),
                    "lineage_classification": "REFERENCE_ONLY",
                }
            )
    for record in selected_cluster.get("included_records", []):
        missing_lineage.append(
            {
                "surface_id": record["surface_id"],
                "ambiguity_id": record["ambiguity_id"],
                "lineage_status": "NO_EXPLICIT_SUPERSESSION",
                "reason": "No CREATED_BY, PREDECESSOR_OF, SUCCESSOR_OF, SUPERSEDES, or SUPERSEDED_BY relation is explicit in the source artifacts.",
            }
        )
    relationships.sort(key=lambda item: (item["from"], item["to"], item["evidence"]))
    missing_lineage.sort(key=lambda item: item["surface_id"])
    basis = {
        "schema_id": LINEAGE_SCHEMA_ID,
        "schema_version": LINEAGE_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "cluster_id": selected_cluster.get("cluster_id"),
        "relationship_types": [
            "CREATED_BY",
            "PREDECESSOR_OF",
            "SUCCESSOR_OF",
            "SUPERSEDES",
            "SUPERSEDED_BY",
            "DERIVED_FROM",
            "GENERATED_FROM",
            "PROPOSES_CHANGE_TO",
            "DUPLICATE_CANDIDATE_OF",
        ],
        "relationships": [dict(item) for item in relationships],
        "missing_lineage": [dict(item) for item in missing_lineage],
    }
    return {
        "schema_id": LINEAGE_SCHEMA_ID,
        "schema_version": LINEAGE_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "cluster_id": selected_cluster.get("cluster_id"),
        "relationship_types": basis["relationship_types"],
        "relationships": relationships,
        "missing_lineage": missing_lineage,
        "logical_hash": logical_sha256(basis),
    }
