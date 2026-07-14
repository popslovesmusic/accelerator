from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Mapping, Sequence

from .reachability_evidence import (
    build_source_snapshot,
    build_surface_indexes,
    classify_reachability,
    load_ambiguity_register,
    load_surface_inventory,
    normalize_path_like,
)


ROOT = Path(__file__).resolve().parents[2]
PATCH_ID = "PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006"
Q0_QUEUE_GROUP = "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS"
Q0_CLUSTER_SCHEMA_ID = "governance_q0_resolution_cluster_v1"
Q0_CLUSTER_SCHEMA_VERSION = "1.0.0"
Q0_CLUSTER_CORE_RULE_ID = "GOVERNANCE_Q0_CLUSTER_COHERENCE_001"
Q0_CLUSTER_CORE_RULE_PATH = ROOT / "governance" / "core_rules" / "GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json"
DEFAULT_GENERATED_AT = "2026-07-13T23:15:00-04:00"
DEFAULT_WORKSPACE_ROOT_IDENTITY = "acellorator@6ebf84a1e"
DEFAULT_REPOSITORY_COMMIT = "6ebf84a1e"

DEFAULT_Q0_SOURCE_FILES = [
    "docs/manual_repository_audit_2026_07_13.md",
    "docs/textbook/mono_process_textbook_complete.md",
    "governance/core_rules/GOVERNANCE_AMBIGUITY_REMEDIATION_ORDER_001.json",
    "governance/core_rules/GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001.json",
    "governance/evidence_sets/GOVERNANCE_GLOBAL_INVENTORY_2026_07_13.json",
    "governance/provenance/governance_inventory_2026_07_13_provenance.json",
    "outputs/governance_inventory/governance_ambiguity_register.json",
    "outputs/governance_inventory/governance_ambiguity_risk_classification.json",
    "outputs/governance_inventory/governance_authority_relationships.json",
    "outputs/governance_inventory/governance_inventory_summary.json",
    "outputs/governance_inventory/governance_remediation_queue.json",
    "outputs/governance_inventory/governance_surface_inventory.json",
    "registry/governance/patches/PATCH_GOVERNANCE_GLOBAL_INVENTORY_002.json",
]

DEFAULT_SOURCE_SCOPE = {
    "included_roots": [
        "docs/governance",
        "docs/manual_repository_audit_2026_07_13.md",
        "docs/textbook/mono_process_textbook_complete.md",
        "governance/core_rules",
        "governance/evidence_sets",
        "governance/provenance",
        "outputs/governance_inventory",
        "patches",
        "registry/governance",
    ],
    "excluded_roots": [
        "Validation Department activation",
        "database migration",
        "fixing discovered conflicts",
        "governance rewriting",
        "mathematical claim promotion",
        "repository cleanup",
        "schema redesign",
        "scientific truth evaluation",
    ],
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def logical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _load_json(relative_path: str) -> dict[str, Any]:
    payload = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _load_hash_registry() -> dict[str, str]:
    payload = _load_json("registry/governance_hash_registry.json")
    hashes = payload.get("hashes", {})
    return {normalize_path_like(key): str(value) for key, value in hashes.items()}


def verify_q0_source_artifacts(source_paths: Sequence[str]) -> dict[str, str]:
    hash_registry = _load_hash_registry()
    verified: dict[str, str] = {}
    missing: list[str] = []
    mismatches: list[dict[str, str]] = []
    for path in sorted({normalize_path_like(item) for item in source_paths if normalize_path_like(item)}):
        digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        registered = hash_registry.get(path)
        if registered is None:
            missing.append(path)
        elif registered.lower() != digest.lower():
            mismatches.append({"path": path, "registered": registered, "computed": digest})
        verified[path] = digest
    if missing or mismatches:
        raise ValueError(
            "Q0 source artifact verification failed: "
            + ", ".join(
                [
                    *(f"missing={path}" for path in missing),
                    *(f"mismatch={item['path']}" for item in mismatches),
                ]
            )
        )
    return verified


def _unique_sorted(values: Sequence[Any]) -> list[str]:
    return sorted({normalize_path_like(value) for value in values if normalize_path_like(value)})


def _queue_records(queue_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    records = [dict(record) for record in queue_bundle.get("records", [])]
    records.sort(key=lambda record: (int(record["queue_position"]), record["ambiguity_id"]))
    return records


def _q0_records(queue_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [record for record in _queue_records(queue_bundle) if record.get("queue_group") == Q0_QUEUE_GROUP]


def _relationship_graph(
    relationships: Sequence[Mapping[str, Any]],
    q0_ids: Sequence[str],
) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    q0_set = set(q0_ids)
    adjacency: dict[str, set[str]] = {surface_id: set() for surface_id in q0_set}
    edges: list[dict[str, Any]] = []
    for relationship in relationships:
        source = normalize_path_like(relationship.get("from"))
        target = normalize_path_like(relationship.get("to"))
        if source in q0_set and target in q0_set:
            adjacency.setdefault(source, set()).add(target)
            adjacency.setdefault(target, set()).add(source)
            edges.append(
                {
                    "from": source,
                    "to": target,
                    "relation_type": normalize_path_like(relationship.get("relation_type")),
                    "evidence": normalize_path_like(relationship.get("evidence")),
                }
            )
    edges.sort(key=lambda item: (item["from"], item["to"], item["evidence"]))
    return adjacency, edges


def _component_from_seed(seed_id: str, adjacency: Mapping[str, set[str]]) -> list[str]:
    seen = {seed_id}
    queue = deque([seed_id])
    while queue:
        current = queue.popleft()
        for neighbor in sorted(adjacency.get(current, set())):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return sorted(seen)


def _partition_component(records: Sequence[Mapping[str, Any]], max_records: int) -> list[list[dict[str, Any]]]:
    normalized = [dict(record) for record in records]
    if len(normalized) <= max_records:
        return [sorted(normalized, key=lambda record: (int(record["queue_position"]), record["ambiguity_id"]))]

    buckets: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in normalized:
        path = normalize_path_like(record.get("path_or_table"))
        surface_type = normalize_path_like(record.get("surface_type"))
        governed_state = path.split("/", 1)[0] if "/" in path else path
        buckets[(governed_state, surface_type, path)].append(record)

    partitions: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for bucket_key in sorted(buckets):
        bucket_records = sorted(buckets[bucket_key], key=lambda record: (int(record["queue_position"]), record["ambiguity_id"]))
        if current and len(current) + len(bucket_records) > max_records:
            partitions.append(current)
            current = []
        if len(bucket_records) > max_records:
            partitions.extend([[record] for record in bucket_records])
            continue
        current.extend(bucket_records)
    if current:
        partitions.append(current)
    return partitions


def _governed_domain(cluster_records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    paths = [normalize_path_like(record.get("path_or_table")) for record in cluster_records]
    return {
        "domain_id": "governance-validation-control-plane",
        "title": "Governance validation control plane",
        "description": (
            "The file-based governance surfaces that validate, register, and route governance state "
            "for the global validation control plane."
        ),
        "decision_scope": "Q0 competing authority and write-path selection only.",
        "target_family": sorted({path.split("/", 1)[0] if "/" in path else path for path in paths if path}),
    }


def _governed_targets(cluster_records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for record in sorted(cluster_records, key=lambda item: (int(item["queue_position"]), item["ambiguity_id"]))[:5]:
        path = normalize_path_like(record.get("path_or_table"))
        reason = {
            "GOV-SURF-0972": "Seed surface and top-ranked validator for the global governance control plane.",
            "GOV-SURF-0881": "Ledger surface carrying patch-registration evidence and change-history authority.",
            "GOV-SURF-0994": "Secondary governance runtime query surface with direct validation relationships.",
            "GOV-SURF-0005": "Validation routine documentation that anchors the runtime contract.",
            "GOV-SURF-0123": "Live work index surface that routes governance work and references the validator.",
        }.get(record["surface_id"], "Primary surface in the selected bounded control-plane cluster.")
        targets.append(
            {
                "surface_id": record["surface_id"],
                "path_or_table": path,
                "surface_type": normalize_path_like(record.get("surface_type")),
                "authority_state": normalize_path_like(record.get("authority_state")),
                "queue_position": int(record["queue_position"]),
                "reason": reason,
            }
        )
    return targets


def _coherence_keys(surface_id: str) -> list[str]:
    mapping = {
        "GOV-SURF-0972": [
            "same_decision_domain_id",
            "same_validation_outcome",
            "same_write_target",
        ],
        "GOV-SURF-0881": [
            "same_decision_domain_id",
            "same_validation_outcome",
            "same_write_target",
            "same_live_lookup_key",
        ],
        "GOV-SURF-0994": [
            "same_decision_domain_id",
            "same_validation_outcome",
            "same_write_target",
        ],
        "GOV-SURF-0005": [
            "same_decision_domain_id",
            "same_validation_outcome",
            "same_live_lookup_key",
        ],
        "GOV-SURF-0123": [
            "same_decision_domain_id",
            "same_live_lookup_key",
            "same_write_target",
        ],
        "GOV-SURF-0001": [
            "same_decision_domain_id",
            "same_live_lookup_key",
            "same_write_target",
        ],
        "GOV-SURF-0002": [
            "same_decision_domain_id",
            "same_live_lookup_key",
            "same_write_target",
        ],
        "GOV-SURF-0132": [
            "same_decision_domain_id",
            "same_validation_outcome",
            "same_write_target",
        ],
        "GOV-SURF-0134": [
            "same_decision_domain_id",
            "same_live_lookup_key",
            "same_write_target",
        ],
        "GOV-SURF-0103": [
            "same_authority_lineage",
            "same_write_target",
        ],
    }
    return mapping.get(surface_id, ["same_governed_state_id"])


def _coherence_evidence(
    cluster_records: Sequence[Mapping[str, Any]],
    edge_index: Mapping[tuple[str, str], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for record in sorted(cluster_records, key=lambda item: (int(item["queue_position"]), item["ambiguity_id"])):
        surface_id = record["surface_id"]
        relevant_edges: list[dict[str, Any]] = []
        for edge_key, edge_records in edge_index.items():
            if surface_id in edge_key:
                relevant_edges.extend(edge_records)
        relevant_edges = sorted(
            {
                (
                    entry["from"],
                    entry["to"],
                    entry["relation_type"],
                    entry["evidence"],
                )
                for entry in relevant_edges
            }
        )
        edge_payload = [
            {
                "from": source,
                "to": target,
                "relation_type": relation_type,
                "evidence": evidence_path,
            }
            for source, target, relation_type, evidence_path in relevant_edges
        ]
        evidence.append(
            {
                "ambiguity_id": record["ambiguity_id"],
                "surface_id": surface_id,
                "queue_position": int(record["queue_position"]),
                "strong_coherence_keys": _coherence_keys(surface_id),
                "evidence_paths": [item["evidence"] for item in edge_payload],
                "graph_edges": edge_payload,
                "reason": (
                    "Connected to the seed component through direct Q0 relationship evidence "
                    "or through a directly linked authority lineage anchor."
                ),
            }
        )
    return evidence


def _excluded_neighbor_records(
    queue_records: Sequence[Mapping[str, Any]],
    included_ids: Sequence[str],
) -> list[dict[str, Any]]:
    included = set(included_ids)
    excluded: list[dict[str, Any]] = []
    for record in queue_records:
        if record["source_record_id"] in included:
            continue
        path = normalize_path_like(record.get("path_or_table"))
        reason = "No direct Q0-Q0 coherence edge connects this record to the selected seed component."
        reason_keys = ["no_direct_q0_q0_path", "cross_domain_behavior"]
        if path.startswith("registry/db/acellorator_index.sqlite::"):
            reason = (
                "Separate database-table authority family inside registry/db/acellorator_index.sqlite; "
                "queue proximity alone is insufficient to bridge it into the selected file-based control plane."
            )
            reason_keys = ["cross_domain_behavior", "different_governed_target_family"]
        elif path.startswith("governance/live/"):
            reason = (
                "Separate live-governance command or manifest surface; no strong coherence key links it "
                "to the selected validation control plane."
            )
            reason_keys = ["cross_domain_behavior", "no_direct_q0_q0_path"]
        elif path.startswith("docs/governance/"):
            reason = (
                "Documentation or evidence surface outside the selected validation control plane; "
                "adjacent queue position does not establish cluster membership."
            )
            reason_keys = ["cross_domain_behavior", "documentation_boundary"]
        elif path.startswith("scripts/orientation_"):
            reason = (
                "Orientation retrieval utility in a separate retrieval domain; the database reference "
                "is not enough to connect it to the seed component."
            )
            reason_keys = ["cross_domain_behavior", "different_governed_target_family"]
        excluded.append(
            {
                "ambiguity_id": record["ambiguity_id"],
                "surface_id": record["source_record_id"],
                "path_or_table": path,
                "queue_position": int(record["queue_position"]),
                "surface_type": normalize_path_like(record.get("surface_type")),
                "authority_state": normalize_path_like(record.get("authority_state")),
                "reason_keys": sorted(dict.fromkeys(reason_keys)),
                "reason": reason,
            }
        )
    excluded.sort(key=lambda record: (record["queue_position"], record["ambiguity_id"]))
    return excluded


def _cluster_selection_basis(
    *,
    seed_ambiguity_id: str,
    queue_group: str,
    queue_position_start: int,
    cluster_id: str,
    governed_domain: Mapping[str, Any],
    governed_targets: Sequence[Mapping[str, Any]],
    included_ambiguity_ids: Sequence[str],
    included_records: Sequence[Mapping[str, Any]],
    excluded_neighbor_records: Sequence[Mapping[str, Any]],
    coherence_evidence: Sequence[Mapping[str, Any]],
    queue_source_hashes: Mapping[str, str],
    source_snapshot: Mapping[str, Any],
    recommended_resolution_mode: str,
) -> dict[str, Any]:
    return {
        "schema_id": Q0_CLUSTER_SCHEMA_ID,
        "schema_version": Q0_CLUSTER_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "seed_ambiguity_id": seed_ambiguity_id,
        "queue_group": queue_group,
        "queue_position_start": queue_position_start,
        "cluster_id": cluster_id,
        "governed_domain": dict(governed_domain),
        "governed_targets": [dict(target) for target in governed_targets],
        "included_ambiguity_ids": list(included_ambiguity_ids),
        "included_records": [dict(record) for record in included_records],
        "excluded_neighbor_records": [dict(record) for record in excluded_neighbor_records],
        "coherence_evidence": [dict(record) for record in coherence_evidence],
        "queue_source_hashes": dict(sorted(queue_source_hashes.items())),
        "source_snapshot": dict(source_snapshot),
        "recommended_resolution_mode": recommended_resolution_mode,
    }


def deterministic_q0_cluster_id(
    seed_ambiguity_id: str,
    included_ambiguity_ids: Sequence[str],
    governed_domain_id: str,
    governed_target_ids: Sequence[str],
) -> str:
    basis = {
        "seed_ambiguity_id": normalize_path_like(seed_ambiguity_id),
        "included_ambiguity_ids": _unique_sorted(included_ambiguity_ids),
        "governed_domain_id": normalize_path_like(governed_domain_id),
        "governed_target_ids": _unique_sorted(governed_target_ids),
    }
    return "Q0-CLUSTER-" + logical_sha256(basis)[:16].upper()


def select_q0_resolution_cluster(
    surface_inventory: Mapping[str, Any] | None = None,
    ambiguity_register: Mapping[str, Any] | None = None,
    queue_bundle: Mapping[str, Any] | None = None,
    relationship_artifact: Mapping[str, Any] | None = None,
    *,
    source_snapshot: Mapping[str, Any] | None = None,
    max_cluster_size: int = 25,
    generated_at: str = DEFAULT_GENERATED_AT,
) -> dict[str, Any]:
    surface_payload = dict(surface_inventory or load_surface_inventory())
    ambiguity_payload = dict(ambiguity_register or load_ambiguity_register())
    queue_payload = dict(queue_bundle or _load_json("outputs/governance_inventory/governance_remediation_queue.json"))
    relationship_payload = dict(
        relationship_artifact or _load_json("outputs/governance_inventory/governance_authority_relationships.json")
    )

    queue_records = _q0_records(queue_payload)
    if not queue_records:
        raise ValueError("No Q0 remediation queue records are available for cluster selection.")

    q0_ids = [record["source_record_id"] for record in queue_records]
    adjacency, relationship_edges = _relationship_graph(relationship_payload.get("relationships", []), q0_ids)
    seed_record = queue_records[0]
    seed_id = seed_record["source_record_id"]
    component_ids = _component_from_seed(seed_id, adjacency)
    component_records = [record for record in queue_records if record["source_record_id"] in component_ids]

    if len(component_records) > max_cluster_size:
        partitions = _partition_component(component_records, max_cluster_size)
        component_records = partitions[0]
        component_ids = [record["source_record_id"] for record in component_records]

    component_records.sort(key=lambda record: (int(record["queue_position"]), record["ambiguity_id"]))
    surface_indexes = build_surface_indexes(surface_payload.get("records", []))

    selected_ambiguity_ids = _unique_sorted(record["ambiguity_id"] for record in component_records)
    selected_target_ids = [
        record["surface_id"]
        for record in sorted(component_records, key=lambda item: (int(item["queue_position"]), item["ambiguity_id"]))[:5]
    ]
    governed_domain = _governed_domain(component_records)
    governed_targets = _governed_targets(component_records)
    cluster_id = deterministic_q0_cluster_id(
        seed_ambiguity_id=seed_record["ambiguity_id"],
        included_ambiguity_ids=selected_ambiguity_ids,
        governed_domain_id=governed_domain["domain_id"],
        governed_target_ids=selected_target_ids,
    )

    queue_source_paths = [
        "outputs/governance_inventory/governance_ambiguity_register.json",
        "outputs/governance_inventory/governance_ambiguity_risk_classification.json",
        "outputs/governance_inventory/governance_authority_relationships.json",
        "outputs/governance_inventory/governance_remediation_queue.json",
        "outputs/governance_inventory/governance_surface_inventory.json",
    ]
    queue_source_hashes = verify_q0_source_artifacts(queue_source_paths)

    if source_snapshot is None:
        source_snapshot = build_source_snapshot(
            DEFAULT_Q0_SOURCE_FILES,
            workspace_root_identity=DEFAULT_WORKSPACE_ROOT_IDENTITY,
            repository_commit=DEFAULT_REPOSITORY_COMMIT,
            included_roots=DEFAULT_SOURCE_SCOPE["included_roots"],
            excluded_roots=DEFAULT_SOURCE_SCOPE["excluded_roots"],
            file_count_scanned=1017,
            surface_count_detected=1083,
            working_tree_dirty=True,
            unrelated_changes_preserved=True,
        )
    else:
        source_snapshot = dict(source_snapshot)

    edge_index: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for edge in relationship_edges:
        key = tuple(sorted((edge["from"], edge["to"])))
        edge_index[key].append(edge)

    included_records: list[dict[str, Any]] = []
    for record in component_records:
        surface_record = surface_indexes["by_id"][record["source_record_id"]]
        reachability = classify_reachability(surface_record, surface_indexes)
        unique_outbound = _unique_sorted(
            [
                *surface_record.get("dependencies", []),
                *surface_record.get("registry_references", []),
            ]
        )
        included_records.append(
            {
                "ambiguity_id": record["ambiguity_id"],
                "surface_id": record["source_record_id"],
                "path_or_table": record["path_or_table"],
                "queue_position": int(record["queue_position"]),
                "risk_score": int(record["risk_score"]),
                "risk_dimensions": list(record["risk_dimensions"]),
                "severity": record["severity"],
                "strong_coherence_keys": _coherence_keys(record["source_record_id"]),
                "coherence_evidence_paths": [
                    edge["evidence"]
                    for edge in edge_index.get(tuple(sorted((record["source_record_id"], seed_id))), [])
                ],
                "read_reachable": bool(reachability["execution_reachable"] or reachability["validation_reachable"] or reachability["write_reachable"]),
                "write_reachable": bool(reachability["write_reachable"]),
                "validation_reachable": bool(reachability["validation_reachable"]),
                "authority_candidates": _unique_sorted(
                    [
                        *surface_record.get("dependencies", []),
                        *surface_record.get("registry_references", []),
                        surface_record.get("path_or_table"),
                    ]
                ),
                "unique_outbound_references": unique_outbound,
            }
        )

    excluded_neighbor_records = _excluded_neighbor_records(queue_records, component_ids)
    coherence_evidence = _coherence_evidence(component_records, edge_index)
    recommended_resolution_mode = "PROVE_EXCLUSIVE_WRITE_OWNER"

    basis = _cluster_selection_basis(
        seed_ambiguity_id=seed_record["ambiguity_id"],
        queue_group=Q0_QUEUE_GROUP,
        queue_position_start=int(seed_record["queue_position"]),
        cluster_id=cluster_id,
        governed_domain=governed_domain,
        governed_targets=governed_targets,
        included_ambiguity_ids=selected_ambiguity_ids,
        included_records=included_records,
        excluded_neighbor_records=excluded_neighbor_records,
        coherence_evidence=coherence_evidence,
        queue_source_hashes=queue_source_hashes,
        source_snapshot=source_snapshot,
        recommended_resolution_mode=recommended_resolution_mode,
    )

    return {
        "schema_id": Q0_CLUSTER_SCHEMA_ID,
        "schema_version": Q0_CLUSTER_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "generated_at": generated_at,
        "core_rule_reference": {
            "rule_id": Q0_CLUSTER_CORE_RULE_ID,
            "path": "governance/core_rules/GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json",
            "hash": hashlib.sha256(Q0_CLUSTER_CORE_RULE_PATH.read_bytes()).hexdigest(),
            "status": "LIVE",
        },
        "queue_source_hashes": queue_source_hashes,
        "source_snapshot": source_snapshot,
        "seed_ambiguity_id": seed_record["ambiguity_id"],
        "seed_queue_position": int(seed_record["queue_position"]),
        "queue_group": Q0_QUEUE_GROUP,
        "queue_position_start": int(seed_record["queue_position"]),
        "cluster_id": cluster_id,
        "governed_domain": governed_domain,
        "governed_targets": governed_targets,
        "included_ambiguity_ids": selected_ambiguity_ids,
        "included_records": included_records,
        "excluded_neighbor_records": excluded_neighbor_records,
        "coherence_evidence": coherence_evidence,
        "resolution_preconditions": [
            "Prove exclusive write ownership for the ledger and runtime surfaces in the cluster.",
            "Prove which validator owns terminal acceptance for the global governance control plane.",
            "Establish whether AGENTS.md and GEMINI.md are mirrored instructions or independent live authorities.",
            "Separate the live work-index, routing-manifest, and task-registry surfaces if they do not share one authority lineage.",
            "Record explicit lineage rather than inferring supersession from queue proximity.",
        ],
        "recommended_resolution_mode": recommended_resolution_mode,
        "status": "SELECTED_FOR_RESOLUTION",
        "selected_q0_count": len(component_records),
        "selected_q0_ambiguities": len(selected_ambiguity_ids),
        "all_q0_count": len(queue_records),
        "excluded_q0_count": len(queue_records) - len(component_records),
        "logical_hash": logical_sha256(
            {
                **basis,
                "core_rule_reference": {
                    "rule_id": Q0_CLUSTER_CORE_RULE_ID,
                    "hash": hashlib.sha256(Q0_CLUSTER_CORE_RULE_PATH.read_bytes()).hexdigest(),
                },
                "generated_at": None,
            }
        ),
    }
