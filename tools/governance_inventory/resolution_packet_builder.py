from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .authority_candidate_inventory import build_authority_candidate_inventory, logical_sha256 as authority_logical_sha256
from .authority_lineage_mapper import build_q0_lineage_map, logical_sha256 as lineage_logical_sha256
from .governance_path_mapper import (
    build_read_path_map,
    build_validation_path_map,
    build_write_path_map,
    logical_sha256 as path_logical_sha256,
)
from .q0_cluster_selector import (
    DEFAULT_GENERATED_AT,
    PATCH_ID,
    Q0_CLUSTER_CORE_RULE_ID,
    Q0_CLUSTER_SCHEMA_ID,
    Q0_CLUSTER_SCHEMA_VERSION,
    deterministic_q0_cluster_id,
    select_q0_resolution_cluster,
)
from .reachability_evidence import normalize_path_like


ROOT = Path(__file__).resolve().parents[2]
PACKET_SCHEMA_ID = "governance_q0_resolution_packet_v1"
PACKET_SCHEMA_VERSION = "1.0.0"
GENERATED_AT = DEFAULT_GENERATED_AT


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def logical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _load_json(relative_path: str) -> dict[str, Any]:
    payload = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _queue_source_hashes(cluster: Mapping[str, Any]) -> dict[str, str]:
    return dict(sorted(cluster.get("queue_source_hashes", {}).items()))


def _cluster_summary(cluster: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": cluster["schema_id"],
        "schema_version": cluster["schema_version"],
        "cluster_id": cluster["cluster_id"],
        "seed_ambiguity_id": cluster["seed_ambiguity_id"],
        "queue_group": cluster["queue_group"],
        "queue_position_start": cluster["queue_position_start"],
        "status": cluster["status"],
        "selected_q0_count": cluster["selected_q0_count"],
        "all_q0_count": cluster["all_q0_count"],
        "excluded_q0_count": cluster["excluded_q0_count"],
        "governed_domain": cluster["governed_domain"],
        "governed_targets": cluster["governed_targets"],
        "included_ambiguity_ids": cluster["included_ambiguity_ids"],
        "excluded_neighbor_records": cluster["excluded_neighbor_records"],
        "recommended_resolution_mode": cluster["recommended_resolution_mode"],
    }


def _provenance_map(cluster: Mapping[str, Any], candidate_inventory: Mapping[str, Any], write_map: Mapping[str, Any]) -> dict[str, Any]:
    cluster_lookup = {record["surface_id"]: record for record in cluster.get("included_records", [])}
    provenance_records = []
    for record in candidate_inventory.get("records", []):
        queue_record = cluster_lookup[record["surface_id"]]
        provenance_records.append(
            {
                "surface_id": record["surface_id"],
                "ambiguity_id": record["ambiguity_id"],
                "queue_position": record["queue_position"],
                "artifact_path": record["path"],
                "surface_hash_or_version": record["hash_or_version"],
                "declared_scope": record["declared_scope"],
                "provenance_status": record["provenance_status"],
                "lineage_status": record["lineage_status"],
                "authority_effect": "NONE",
                "evidence": record["evidence"],
                "queue_record_summary": {
                    "queue_position": int(queue_record["queue_position"]),
                    "risk_score": int(queue_record["risk_score"]),
                    "severity": queue_record["severity"],
                    "risk_dimensions": queue_record["risk_dimensions"],
                },
            }
        )
    basis = {
        "schema_id": "governance_q0_provenance_map_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "cluster_id": cluster["cluster_id"],
        "record_count": len(provenance_records),
        "records": [dict(record) for record in provenance_records],
    }
    return {
        "schema_id": "governance_q0_provenance_map_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "cluster_id": cluster["cluster_id"],
        "record_count": len(provenance_records),
        "records": provenance_records,
        "logical_hash": logical_sha256(basis),
    }


def _state_consistency_risks(cluster: Mapping[str, Any], candidate_inventory: Mapping[str, Any]) -> list[dict[str, Any]]:
    records = list(candidate_inventory.get("records", []))
    lookup = {record["surface_id"]: record for record in records}
    return [
        {
            "risk_id": "RISK_Q0_001",
            "description": "Multiple validation-capable surfaces in the same component can accept or reject the same terminal outcome.",
            "affected_surfaces": ["GOV-SURF-0972", "GOV-SURF-0994", "GOV-SURF-0005"],
            "evidence": "The selected cluster connects the global validator, runtime query surface, and validation routine documentation by direct references.",
        },
        {
            "risk_id": "RISK_Q0_002",
            "description": "Ledger and hash registry updates are coupled to global validation, so an ambiguous write owner can overwrite or append conflicting authority evidence.",
            "affected_surfaces": ["GOV-SURF-0881", "GOV-SURF-0972", "GOV-SURF-0994"],
            "evidence": "The seed component directly links the validator, ledger, and query runtime surfaces.",
        },
        {
            "risk_id": "RISK_Q0_003",
            "description": "Instruction files, live work indices, and routing manifests appear in the same authority domain and can be mistaken for one canonical authority family.",
            "affected_surfaces": ["GOV-SURF-0001", "GOV-SURF-0002", "GOV-SURF-0123", "GOV-SURF-0132", "GOV-SURF-0134"],
            "evidence": "The selected component includes the root instruction files and live governance routing manifests in one connected authority neighborhood.",
        },
        {
            "risk_id": "RISK_Q0_004",
            "description": "The Validation Department architecture record remains a live-looking authority candidate without explicit supersession lineage.",
            "affected_surfaces": ["GOV-SURF-0103", "GOV-SURF-0881"],
            "evidence": "The architecture record enters the component through the ledger relationship but has no explicit CREATED_BY or SUPERSEDES evidence in the source artifacts.",
        },
    ]


def _candidate_resolution_options() -> list[dict[str, Any]]:
    return [
        {
            "option_id": "OPT_001",
            "mode": "PROVE_EXCLUSIVE_WRITE_OWNER",
            "authority_effect": "NONE",
            "required_migrations": [
                "Prove a single writer for the ledger and runtime control-plane surfaces.",
                "Keep all current readers on their present live surfaces until write ownership is proven.",
            ],
            "reader_changes": [
                "No reader redirection in this patch.",
                "Readers continue to observe the current live surfaces as transitional evidence only.",
            ],
            "writer_changes": [
                "No writer is deactivated in this patch.",
                "Only evidence about writer ownership is recorded.",
            ],
            "validation_consequences": [
                "A later patch may narrow validation acceptance to one canonical owner.",
                "The inventory completion gate remains blocked until the ambiguity set shrinks.",
            ],
            "rollback_requirements": [
                "Remove the packet artifacts and the Q0 cluster rule if the write-owner proof is invalidated.",
                "Preserve the original queue, classification, and inventory evidence unchanged.",
            ],
        },
        {
            "option_id": "OPT_002",
            "mode": "SELECT_CANONICAL_AUTHORITY",
            "authority_effect": "NONE",
            "required_migrations": [
                "Redirect readers to one canonical authority surface.",
                "Retire or demote the competing surfaces in a later patch only after proof exists.",
            ],
            "reader_changes": [
                "Reader routing would be rewritten in a later patch, not here.",
            ],
            "writer_changes": [
                "Writer ownership would be collapsed into one authority path in a later patch.",
            ],
            "validation_consequences": [
                "Validation acceptance would become simpler after authority consolidation.",
            ],
            "rollback_requirements": [
                "Restore the cluster packet and the original reader routing evidence.",
            ],
        },
        {
            "option_id": "OPT_003",
            "mode": "SEPARATE_AUTHORITY_DOMAINS",
            "authority_effect": "NONE",
            "required_migrations": [
                "Partition the cluster by governed target family.",
                "Split validation, instruction, routing, and ledger concerns into explicit domain boundaries.",
            ],
            "reader_changes": [
                "Readers remain scoped to their current family boundaries until the split is proven.",
            ],
            "writer_changes": [
                "Writers are confined to their family-specific target boundaries in a later patch.",
            ],
            "validation_consequences": [
                "Validation gates become domain-specific rather than cluster-wide.",
            ],
            "rollback_requirements": [
                "Remove the partitioning proposal and preserve the bounded cluster packet.",
            ],
        },
    ]


def _required_resolution_tests() -> list[str]:
    return [
        "The seed is the first canonical Q0 queue entry.",
        "The selected cluster includes the seed.",
        "Every additional included ambiguity has at least one strong coherence key.",
        "Queue adjacency alone cannot add an ambiguity.",
        "Cross-domain records are excluded.",
        "All candidate authorities have neutral evidence and no preferred winner is named.",
        "All proven writers, readers, and validators are mapped deterministically.",
        "No ambiguity status changes.",
        "The original 514 ambiguity count remains unchanged.",
        "The inventory remains PARTIAL and the completion gate remains BLOCKED.",
        "The full regression environment blocker remains OPEN.",
    ]


def _rollback_boundary(cluster: Mapping[str, Any], candidate_inventory: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "boundary_description": "Remove only the Q0 cluster-selection and resolution-packet artifacts; keep the original inventory, queue, classification, provenance, and ambiguity register unchanged.",
        "restorable_artifacts": [
            "governance/core_rules/GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json",
            "outputs/governance_inventory/q0_selected_resolution_cluster.json",
            "outputs/governance_inventory/q0_resolution_authority_candidates.json",
            "outputs/governance_inventory/q0_resolution_write_paths.json",
            "outputs/governance_inventory/q0_resolution_read_paths.json",
            "outputs/governance_inventory/q0_resolution_validation_paths.json",
            "outputs/governance_inventory/q0_resolution_lineage.json",
            "outputs/governance_inventory/q0_resolution_packet.json",
            "docs/governance/q0_resolution_packet_review.md",
            "patches/PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006.json",
        ],
        "unaffected_artifacts": [
            "outputs/governance_inventory/governance_ambiguity_register.json",
            "outputs/governance_inventory/governance_ambiguity_risk_classification.json",
            "outputs/governance_inventory/governance_authority_relationships.json",
            "outputs/governance_inventory/governance_remediation_queue.json",
            "outputs/governance_inventory/governance_surface_inventory.json",
            "governance/core_rules/GOVERNANCE_AMBIGUITY_REMEDIATION_ORDER_001.json",
            "governance/core_rules/GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001.json",
            "governance/evidence_sets/GOVERNANCE_GLOBAL_INVENTORY_2026_07_13.json",
            "governance/provenance/governance_inventory_2026_07_13_provenance.json",
        ],
        "rollback_steps": [
            "Delete the new Q0 cluster-selection artifacts.",
            "Remove the new core-rule and the patch completion record.",
            "Leave all source inventory artifacts and unrelated dirty workspace changes untouched.",
        ],
        "selected_cluster_id": cluster["cluster_id"],
        "selected_candidate_count": candidate_inventory["record_count"],
    }


def build_q0_resolution_packet_bundle(
    *,
    surface_inventory: Mapping[str, Any] | None = None,
    ambiguity_register: Mapping[str, Any] | None = None,
    queue_bundle: Mapping[str, Any] | None = None,
    relationship_artifact: Mapping[str, Any] | None = None,
    source_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    cluster = select_q0_resolution_cluster(
        surface_inventory=surface_inventory,
        ambiguity_register=ambiguity_register,
        queue_bundle=queue_bundle,
        relationship_artifact=relationship_artifact,
        source_snapshot=source_snapshot,
    )
    candidate_inventory = build_authority_candidate_inventory(
        cluster,
        surface_inventory=surface_inventory,
        queue_bundle=queue_bundle,
    )
    write_path_map = build_write_path_map(candidate_inventory)
    read_path_map = build_read_path_map(candidate_inventory)
    validation_path_map = build_validation_path_map(candidate_inventory, cluster)
    lineage_map = build_q0_lineage_map(
        cluster,
        relationship_artifact or _load_json("outputs/governance_inventory/governance_authority_relationships.json"),
    )
    provenance_map = _provenance_map(cluster, candidate_inventory, write_path_map)
    packet = {
        "schema_id": PACKET_SCHEMA_ID,
        "schema_version": PACKET_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "generated_at": GENERATED_AT,
        "core_rule_reference": cluster["core_rule_reference"],
        "queue_source_hashes": _queue_source_hashes(cluster),
        "source_snapshot": dict(cluster["source_snapshot"]),
        "cluster_summary": _cluster_summary(cluster),
        "authority_candidates": candidate_inventory["records"],
        "write_path_map": write_path_map,
        "read_path_map": read_path_map,
        "validation_path_map": validation_path_map,
        "lineage_map": lineage_map,
        "provenance_map": provenance_map,
        "state_consistency_risks": _state_consistency_risks(cluster, candidate_inventory),
        "candidate_resolution_options": _candidate_resolution_options(),
        "required_resolution_tests": _required_resolution_tests(),
        "rollback_boundary": _rollback_boundary(cluster, candidate_inventory),
        "unresolved_questions": [
            "Which surface owns exclusive writes to the governance ledger and hash registry?",
            "Which surface is the canonical validation owner for the global governance control plane?",
            "Are AGENTS.md and GEMINI.md mirrored instructions or independent live authorities?",
            "Does the Validation Department architecture record remain a live authority candidate or only a historical proposal boundary?",
        ],
    }
    packet["logical_hash"] = logical_sha256(
        {
            "schema_id": packet["schema_id"],
            "schema_version": packet["schema_version"],
            "patch_id": packet["patch_id"],
            "core_rule_reference": packet["core_rule_reference"],
            "queue_source_hashes": packet["queue_source_hashes"],
            "source_snapshot": packet["source_snapshot"],
            "cluster_summary": packet["cluster_summary"],
            "authority_candidates": packet["authority_candidates"],
            "write_path_map": packet["write_path_map"],
            "read_path_map": packet["read_path_map"],
            "validation_path_map": packet["validation_path_map"],
            "lineage_map": packet["lineage_map"],
            "provenance_map": packet["provenance_map"],
            "state_consistency_risks": packet["state_consistency_risks"],
            "candidate_resolution_options": packet["candidate_resolution_options"],
            "required_resolution_tests": packet["required_resolution_tests"],
            "rollback_boundary": packet["rollback_boundary"],
            "unresolved_questions": packet["unresolved_questions"],
            "cluster_schema_reference": {
                "schema_id": Q0_CLUSTER_SCHEMA_ID,
                "schema_version": Q0_CLUSTER_SCHEMA_VERSION,
                "cluster_id": packet["cluster_summary"]["cluster_id"],
            },
            "candidate_inventory_reference": {
                "schema_id": candidate_inventory["schema_id"],
                "schema_version": candidate_inventory["schema_version"],
                "record_count": candidate_inventory["record_count"],
                "logical_hash": candidate_inventory["logical_hash"],
            },
            "path_map_logical_hashes": {
                "write": write_path_map["logical_hash"],
                "read": read_path_map["logical_hash"],
                "validation": validation_path_map["logical_hash"],
                "lineage": lineage_map["logical_hash"],
                "provenance": provenance_map["logical_hash"],
            },
        }
    )
    packet["cluster_schema_reference"] = {
        "schema_id": Q0_CLUSTER_SCHEMA_ID,
        "schema_version": Q0_CLUSTER_SCHEMA_VERSION,
        "cluster_id": cluster["cluster_id"],
    }
    packet["candidate_inventory_reference"] = {
        "schema_id": candidate_inventory["schema_id"],
        "schema_version": candidate_inventory["schema_version"],
        "record_count": candidate_inventory["record_count"],
        "logical_hash": candidate_inventory["logical_hash"],
    }
    packet["path_map_logical_hashes"] = {
        "write": write_path_map["logical_hash"],
        "read": read_path_map["logical_hash"],
        "validation": validation_path_map["logical_hash"],
        "lineage": lineage_map["logical_hash"],
        "provenance": provenance_map["logical_hash"],
    }
    return {
        "cluster": cluster,
        "candidate_inventory": candidate_inventory,
        "write_path_map": write_path_map,
        "read_path_map": read_path_map,
        "validation_path_map": validation_path_map,
        "lineage_map": lineage_map,
        "provenance_map": provenance_map,
        "packet": packet,
    }


def _write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def build_q0_review_markdown(bundle: Mapping[str, Any]) -> str:
    cluster = bundle["cluster"]
    candidate_inventory = bundle["candidate_inventory"]
    packet = bundle["packet"]
    write_path_map = bundle["write_path_map"]
    read_path_map = bundle["read_path_map"]
    validation_path_map = bundle["validation_path_map"]
    lineage_map = bundle["lineage_map"]
    lines = [
        "# Q0 Governance Cluster Resolution Packet Review",
        "",
        "## Scope",
        "Deterministic selection of the first coherent Q0 cluster and preparation of a neutral resolution packet.",
        "",
        "## Directly Observed",
        f"- Cluster ID: `{cluster['cluster_id']}`",
        f"- Seed ambiguity: `{cluster['seed_ambiguity_id']}`",
        f"- Included ambiguities: {len(cluster['included_ambiguity_ids'])}",
        f"- Excluded Q0 neighbors: {cluster['excluded_q0_count']}",
        f"- Candidate authorities: {candidate_inventory['record_count']}",
        f"- Write paths: {write_path_map['record_count']}",
        f"- Read paths: {read_path_map['record_count']}",
        f"- Validation paths: {validation_path_map['record_count']}",
        f"- Lineage records: {len(lineage_map['relationships'])}",
        f"- Packet logical hash: `{packet['logical_hash']}`",
        "",
        "## Cluster",
        f"- Domain: {cluster['governed_domain']['title']}",
        f"- Target family: {', '.join(cluster['governed_domain']['target_family'])}",
        f"- Recommended mode: {cluster['recommended_resolution_mode']}",
        "",
        "## State Consistency Risks",
    ]
    for risk in packet["state_consistency_risks"]:
        lines.append(f"- {risk['risk_id']}: {risk['description']}")
    lines.extend([
        "",
        "## Candidate Resolution Options",
    ])
    for option in packet["candidate_resolution_options"]:
        lines.append(f"- {option['option_id']}: {option['mode']}")
    lines.extend([
        "",
        "## Failure Modes / Uncertainty",
        "- This packet does not choose a canonical authority.",
        "- This packet does not change any authority status.",
        "- The inventory completion gate remains blocked by 514 ambiguities.",
        "- The complete project regression suite remains blocked by unrelated missing dependencies.",
    ])
    return "\n".join(lines) + "\n"


def write_q0_resolution_artifacts(
    *,
    cluster_path: str | Path,
    authority_candidates_path: str | Path,
    write_paths_path: str | Path,
    read_paths_path: str | Path,
    validation_paths_path: str | Path,
    lineage_path: str | Path,
    packet_path: str | Path,
    review_path: str | Path,
    surface_inventory: Mapping[str, Any] | None = None,
    ambiguity_register: Mapping[str, Any] | None = None,
    queue_bundle: Mapping[str, Any] | None = None,
    relationship_artifact: Mapping[str, Any] | None = None,
    source_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = build_q0_resolution_packet_bundle(
        surface_inventory=surface_inventory,
        ambiguity_register=ambiguity_register,
        queue_bundle=queue_bundle,
        relationship_artifact=relationship_artifact,
        source_snapshot=source_snapshot,
    )
    _write_json(Path(cluster_path), bundle["cluster"])
    _write_json(Path(authority_candidates_path), bundle["candidate_inventory"])
    _write_json(Path(write_paths_path), bundle["write_path_map"])
    _write_json(Path(read_paths_path), bundle["read_path_map"])
    _write_json(Path(validation_paths_path), bundle["validation_path_map"])
    _write_json(Path(lineage_path), bundle["lineage_map"])
    _write_json(Path(packet_path), bundle["packet"])
    Path(review_path).parent.mkdir(parents=True, exist_ok=True)
    Path(review_path).write_text(build_q0_review_markdown(bundle), encoding="utf-8", newline="\n")
    bundle["artifacts"] = {
        "cluster": {"path": str(cluster_path), "hash": hashlib.sha256(Path(cluster_path).read_bytes()).hexdigest()},
        "authority_candidates": {
            "path": str(authority_candidates_path),
            "hash": hashlib.sha256(Path(authority_candidates_path).read_bytes()).hexdigest(),
        },
        "write_paths": {"path": str(write_paths_path), "hash": hashlib.sha256(Path(write_paths_path).read_bytes()).hexdigest()},
        "read_paths": {"path": str(read_paths_path), "hash": hashlib.sha256(Path(read_paths_path).read_bytes()).hexdigest()},
        "validation_paths": {
            "path": str(validation_paths_path),
            "hash": hashlib.sha256(Path(validation_paths_path).read_bytes()).hexdigest(),
        },
        "lineage": {"path": str(lineage_path), "hash": hashlib.sha256(Path(lineage_path).read_bytes()).hexdigest()},
        "packet": {"path": str(packet_path), "hash": hashlib.sha256(Path(packet_path).read_bytes()).hexdigest()},
        "review": {"path": str(review_path), "hash": hashlib.sha256(Path(review_path).read_bytes()).hexdigest()},
    }
    return bundle
