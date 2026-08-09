from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .q0_cluster_selector import (
    DEFAULT_GENERATED_AT as CLUSTER_GENERATED_AT,
    select_q0_resolution_cluster,
)
from .authority_candidate_inventory import build_authority_candidate_inventory
from .governance_path_mapper import build_validation_path_map
from .reachability_evidence import build_surface_indexes, load_ambiguity_register, load_surface_inventory, normalize_path_like


ROOT = Path(__file__).resolve().parents[2]
PATCH_ID = "PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007"
PARTITION_SCHEMA_ID = "governance_q0_authority_scope_partition_v1"
PARTITION_SCHEMA_VERSION = "1.0.0"
GENERATED_AT = "2026-07-14T16:00:00-04:00"
WORKSPACE_ROOT_IDENTITY = "acellorator@6ebf84a1e"
REPOSITORY_COMMIT = "6ebf84a1e"
CORE_RULE_ID = "GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001"
CORE_RULE_TITLE = "Non-Overlapping Governance Authority Roles"
CORE_RULE_PATH = ROOT / "governance" / "core_rules" / f"{CORE_RULE_ID}.json"

ROLE_IDS = [
    "REGISTRY_STATE_AUTHORITY",
    "REGISTRY_WRITE_AUTHORITY",
    "VALIDATION_INVOCATION_AUTHORITY",
    "VALIDATION_REDUCTION_AUTHORITY",
    "INSTRUCTION_AUTHORITY",
    "GENERATED_EVIDENCE",
]

PROHIBITED_ROLE_OVERLAPS = [
    {
        "roles": ["GENERATED_EVIDENCE", "REGISTRY_STATE_AUTHORITY"],
        "rule": "A generated report cannot also serve as the source registry authority.",
    },
    {
        "roles": ["INSTRUCTION_AUTHORITY", "REGISTRY_WRITE_AUTHORITY"],
        "rule": "Documentation cannot mutate live governance state.",
    },
    {
        "roles": ["VALIDATION_INVOCATION_AUTHORITY", "REGISTRY_WRITE_AUTHORITY"],
        "rule": "The canonical validation command cannot silently alter registry authority to obtain a passing result.",
    },
    {
        "roles": ["SUPPORTING_VALIDATOR", "VALIDATION_REDUCTION_AUTHORITY"],
        "rule": "A supporting stage validator cannot independently emit the final governed status.",
    },
]

ROLE_DEFINITIONS = {
    "REGISTRY_STATE_AUTHORITY": {
        "purpose": "Canonical persisted representation of live governance records, identifiers, hashes, statuses, relationships, and transitions.",
        "allowed_actions": [
            "STORE_LIVE_RULE",
            "STORE_PATCH_STATUS",
            "STORE_AUTHORITY_TRANSITION",
            "STORE_PROVENANCE_REFERENCE",
            "STORE_HASH",
            "STORE_RELATIONSHIP",
        ],
        "prohibited_actions": [
            "DEFINE_VALIDATION_ALGORITHM_BY_EXISTENCE",
            "EXECUTE_VALIDATION",
            "INTERPRET_AMBIGUITY_WITHOUT_RULE",
            "SELF_AUTHORIZE_WRITES",
        ],
    },
    "REGISTRY_WRITE_AUTHORITY": {
        "purpose": "Exclusive controlled mechanism for adding or modifying authoritative registry state.",
        "allowed_actions": [
            "APPEND",
            "UPDATE",
            "WRITE",
            "SYNC_HASHES",
        ],
        "prohibited_actions": [
            "DELETE_WITHOUT_RAPID_ROLLBACK",
            "UNBOUNDED_OVERWRITE",
            "HIDDEN_FALLBACK_WRITE",
        ],
    },
    "VALIDATION_INVOCATION_AUTHORITY": {
        "purpose": "Canonical governed validation invocation boundary.",
        "allowed_actions": [
            "LOAD_REGISTERED_RULES",
            "RUN_REQUIRED_STAGES",
            "EMIT_REPORT",
        ],
        "prohibited_actions": [
            "CREATE_LIVE_GOVERNANCE",
            "PROMOTE_PROPOSALS",
            "MUTATE_REGISTRY_TO_FORCE_PASS",
        ],
    },
    "VALIDATION_REDUCTION_AUTHORITY": {
        "purpose": "Sole authority for reducing validation-stage results into terminal governed status.",
        "allowed_actions": [
            "REDUCE_STAGE_RESULTS",
            "RETURN_TERMINAL_STATUS",
        ],
        "prohibited_actions": [
            "ALLOW_SUPPORTING_VALIDATOR_TO_OVERRIDE",
            "TREAT_SKIPPED_AS_PASS",
        ],
    },
    "INSTRUCTION_AUTHORITY": {
        "purpose": "Prescriptive guidance for operators and agents. It may name procedures but cannot mutate live state by itself.",
        "allowed_actions": [
            "NAME_CANONICAL_COMMAND",
            "DEFINE_OPERATOR_SEQUENCE",
            "EXPLAIN_FAILURE_MODES",
            "REFERENCE_LIVE_RULES",
        ],
        "prohibited_actions": [
            "CREATE_REGISTRY_STATE",
            "ALTER_AUTHORITY_STATUS",
            "OVERRIDE_VALIDATOR_RESULT",
            "SUPERSEDE_CORE_RULE_WITH_PROSE",
        ],
    },
    "GENERATED_EVIDENCE": {
        "purpose": "Derived reports, inventories, queues, and summaries that reflect governed state but do not authorize it.",
        "allowed_actions": [
            "REPORT_OBSERVATIONS",
            "EXPORT_SUMMARIES",
            "RECORD_DIFFS",
        ],
        "prohibited_actions": [
            "AUTHORIZE_WRITES",
            "SUPERSEDE_SOURCE_AUTHORITY",
            "DEFINE_TERMINAL_STATUS_INDEPENDENTLY",
        ],
    },
}

ROLE_ASSIGNMENT_ORDER = [
    "GOV-SURF-0881",
    "GOV-SURF-0132",
    "GOV-SURF-0882",
    "GOV-SURF-0972",
    "GOV-SURF-0994",
    "GOV-SURF-0123",
    "GOV-SURF-0005",
    "GOV-SURF-0001",
    "GOV-SURF-0002",
    "GOV-SURF-0134",
    "GOV-SURF-0103",
]

ROLE_ASSIGNMENTS = {
    "GOV-SURF-0881": {
        "assigned_roles": ["REGISTRY_STATE_AUTHORITY"],
        "explicitly_denied_roles": [
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "INSTRUCTION_AUTHORITY",
            "GENERATED_EVIDENCE",
        ],
        "scope": {
            "scope_id": "CHANGE_HISTORY",
            "title": "Change-history registry state",
            "description": "The append-only governance change ledger stores approval and history records for governed patches.",
        },
    },
    "GOV-SURF-0132": {
        "assigned_roles": ["REGISTRY_STATE_AUTHORITY"],
        "explicitly_denied_roles": [
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "INSTRUCTION_AUTHORITY",
            "GENERATED_EVIDENCE",
        ],
        "scope": {
            "scope_id": "TOOL_ROUTING_METADATA",
            "title": "Tool-routing registry state",
            "description": "The live tool-routing manifest stores deterministic routing metadata separate from raw rigor declarations.",
        },
    },
    "GOV-SURF-0882": {
        "assigned_roles": ["GENERATED_EVIDENCE"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "INSTRUCTION_AUTHORITY",
        ],
        "scope": {
            "scope_id": "HASH_INTEGRITY_EVIDENCE",
            "title": "Integrity-hash evidence",
            "description": "The hash registry is a derived integrity surface that records hashes but does not create semantic authority.",
        },
    },
    "GOV-SURF-0972": {
        "assigned_roles": ["VALIDATION_INVOCATION_AUTHORITY", "VALIDATION_REDUCTION_AUTHORITY"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "INSTRUCTION_AUTHORITY",
            "GENERATED_EVIDENCE",
        ],
        "scope": {
            "scope_id": "VALIDATION_BOUNDARY",
            "title": "Canonical validation boundary",
            "description": "Module-style validation invocation and fail-closed terminal reduction for governed repository checks.",
        },
    },
    "GOV-SURF-0994": {
        "assigned_roles": ["GENERATED_EVIDENCE"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "INSTRUCTION_AUTHORITY",
        ],
        "scope": {
            "scope_id": "GOVERNANCE_QUERY_EVIDENCE",
            "title": "Governance query evidence",
            "description": "The query helper emits diagnostic authority snapshots and should not be mistaken for a live registry.",
        },
    },
    "GOV-SURF-0123": {
        "assigned_roles": ["GENERATED_EVIDENCE"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "INSTRUCTION_AUTHORITY",
        ],
        "scope": {
            "scope_id": "MASTER_WORK_INDEX_PROJECTION",
            "title": "Work-index projection",
            "description": "The live work index is a projection and index surface, not a source of live authority.",
        },
    },
    "GOV-SURF-0005": {
        "assigned_roles": ["INSTRUCTION_AUTHORITY"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "GENERATED_EVIDENCE",
        ],
        "scope": {
            "scope_id": "VALIDATION_ROUTINE_GUIDANCE",
            "title": "Validation routine guidance",
            "description": "The global validation routine document is prescriptive guidance for operating the validator boundary.",
        },
    },
    "GOV-SURF-0001": {
        "assigned_roles": ["INSTRUCTION_AUTHORITY"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "GENERATED_EVIDENCE",
        ],
        "scope": {
            "scope_id": "AGENT_INSTRUCTIONS",
            "title": "Agent instructions",
            "description": "AGENTS.md is operator-facing guidance and cannot directly create live governance state.",
        },
    },
    "GOV-SURF-0002": {
        "assigned_roles": ["INSTRUCTION_AUTHORITY"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "GENERATED_EVIDENCE",
        ],
        "scope": {
            "scope_id": "GEMINI_INSTRUCTIONS",
            "title": "Gemini instructions",
            "description": "GEMINI.md is operator-facing guidance and cannot directly create live governance state.",
        },
    },
    "GOV-SURF-0134": {
        "assigned_roles": ["INSTRUCTION_AUTHORITY"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "GENERATED_EVIDENCE",
        ],
        "scope": {
            "scope_id": "PROGRAM_TASK_GUIDANCE",
            "title": "Program task registry guidance",
            "description": "The program task registry is prescriptive guidance for governed work assignment, not live authority creation.",
        },
    },
    "GOV-SURF-0103": {
        "assigned_roles": ["INSTRUCTION_AUTHORITY"],
        "explicitly_denied_roles": [
            "REGISTRY_STATE_AUTHORITY",
            "REGISTRY_WRITE_AUTHORITY",
            "VALIDATION_INVOCATION_AUTHORITY",
            "VALIDATION_REDUCTION_AUTHORITY",
            "GENERATED_EVIDENCE",
        ],
        "scope": {
            "scope_id": "VALIDATION_DEPARTMENT_ARCHITECTURE",
            "title": "Validation department architecture guidance",
            "description": "The mini-agent architecture record is foundational guidance and not a live proposal or registry authority.",
        },
    },
}

WRITE_OWNER_ASSIGNMENTS = [
    {
        "scope_id": "CORE_RULE_STATE",
        "registry_path": "governance/core_rules/GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json",
        "authorized_writer_id": "scripts/governance/register_q0_authority_scope_partition.py",
        "authorized_entry_point": "python -m scripts.governance.register_q0_authority_scope_partition",
        "allowed_operations": ["STORE_LIVE_RULE", "STORE_PATCH_STATUS"],
        "denied_operations": ["DELETE", "REPLACE", "MERGE"],
        "validation_before_write": ["schema validation", "hash verification"],
        "atomicity_or_rollback_behavior": "Atomic file write; fail closed on validation mismatch.",
        "hash_synchronization_behavior": "The writer computes exact-byte SHA-256 before ledger registration.",
        "audit_behavior": "Record the governing rule path and patch id in the change ledger.",
    },
    {
        "scope_id": "CHANGE_HISTORY",
        "registry_path": "registry/governance_change_ledger.json",
        "authorized_writer_id": "scripts/governance/register_q0_authority_scope_partition.py",
        "authorized_entry_point": "python -m scripts.governance.register_q0_authority_scope_partition",
        "allowed_operations": ["APPEND", "UPDATE"],
        "denied_operations": ["DELETE", "MERGE"],
        "validation_before_write": ["entry schema validation", "approval-reference validation"],
        "atomicity_or_rollback_behavior": "Append the ledger entry only after all governed artifacts are written successfully.",
        "hash_synchronization_behavior": "Maintain the change ledger as an append-only record of the partition registration.",
        "audit_behavior": "Store the diff report path and patch id in the appended ledger entry.",
    },
    {
        "scope_id": "TOOL_ROUTING_METADATA",
        "registry_path": "governance/live/tool_routing_manifest.json",
        "authorized_writer_id": "scripts/governance/register_q0_authority_scope_partition.py",
        "authorized_entry_point": "python -m scripts.governance.register_q0_authority_scope_partition",
        "allowed_operations": ["APPEND", "UPDATE"],
        "denied_operations": ["DELETE", "MERGE"],
        "validation_before_write": ["schema validation", "hash verification"],
        "atomicity_or_rollback_behavior": "No mutation is required by this patch; the writer exists only as the exclusive declared mechanism.",
        "hash_synchronization_behavior": "Any future manifest update must synchronize through the same writer boundary.",
        "audit_behavior": "Keep routing metadata separate from live validation and registry-state authority.",
    },
    {
        "scope_id": "PARTITION_REGISTRY",
        "registry_path": "governance/authority_partitions/Q0_AUTHORITY_SCOPE_PARTITION_001.json",
        "authorized_writer_id": "scripts/governance/register_q0_authority_scope_partition.py",
        "authorized_entry_point": "python -m scripts.governance.register_q0_authority_scope_partition",
        "allowed_operations": ["STORE_PARTITION_RECORD", "UPDATE"],
        "denied_operations": ["DELETE", "MERGE"],
        "validation_before_write": ["partition schema validation", "role-overlap validation"],
        "atomicity_or_rollback_behavior": "Write the partition record atomically after the supporting evidence files are present.",
        "hash_synchronization_behavior": "The partition record hashes all governed evidence it references.",
        "audit_behavior": "Store the partition identifier and governing rule identifiers in the registry record.",
    },
]

VALIDATION_REDUCTION_RULE_ID = "GOVERNANCE_VALIDATION_FAIL_CLOSED_001"
VALIDATION_PARTITION_RULE_IDS = [
    "GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001",
    VALIDATION_REDUCTION_RULE_ID,
]

INSTRUCTION_SURFACE_IDS = [
    "GOV-SURF-0001",
    "GOV-SURF-0002",
    "GOV-SURF-0005",
    "GOV-SURF-0134",
    "GOV-SURF-0103",
]

GENERATED_EVIDENCE_SURFACE_IDS = [
    "GOV-SURF-0882",
    "GOV-SURF-0994",
    "GOV-SURF-0123",
]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def logical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _load_json(relative_path: str) -> dict[str, Any]:
    payload = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _surface_index(surface_inventory: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return build_surface_indexes(surface_inventory.get("records", []))["by_id"]


def _queue_index(queue_bundle: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        normalize_path_like(record.get("source_record_id")): dict(record)
        for record in queue_bundle.get("records", [])
        if normalize_path_like(record.get("source_record_id"))
    }


def _ambiguity_index(ambiguity_register: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        normalize_path_like(record.get("surface_id")): dict(record)
        for record in ambiguity_register.get("ambiguities", [])
        if normalize_path_like(record.get("surface_id"))
    }


def _claim_ids(ambiguity_record: Mapping[str, Any]) -> list[dict[str, Any]]:
    claims = []
    questions = list(ambiguity_record.get("questions", []))
    for index, question in enumerate(questions, 1):
        claims.append(
            {
                "claim_id": f"{ambiguity_record['surface_id']}#Q{index}",
                "ambiguity_id": ambiguity_record["surface_id"],
                "question_index": index,
                "question": question,
            }
        )
    if not claims:
        claims.append(
            {
                "claim_id": f"{ambiguity_record['surface_id']}#Q1",
                "ambiguity_id": ambiguity_record["surface_id"],
                "question_index": 1,
                "question": None,
            }
        )
    return claims


def _governing_evidence_for_surface(
    surface_id: str,
    *,
    cluster: Mapping[str, Any],
    surface_index: Mapping[str, Mapping[str, Any]],
    ambiguity_index: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    surface_record = surface_index.get(surface_id, {})
    ambiguity_record = ambiguity_index.get(surface_id, {})

    for item in surface_record.get("evidence", []) or []:
        evidence.append(
            {
                "path": normalize_path_like(item.get("path")),
                "location": normalize_path_like(item.get("location")),
                "evidence_type": normalize_path_like(item.get("evidence_type")),
            }
        )

    for item in ambiguity_record.get("evidence", []) or []:
        payload = {
            "path": normalize_path_like(item.get("path")),
            "location": normalize_path_like(item.get("location")),
            "evidence_type": normalize_path_like(item.get("evidence_type")),
        }
        if payload not in evidence:
            evidence.append(payload)

    for entry in cluster.get("coherence_evidence", []):
        if entry.get("surface_id") == surface_id:
            for path in entry.get("evidence_paths", []):
                payload = {
                    "path": normalize_path_like(path),
                    "location": "cluster coherence evidence",
                    "evidence_type": "DIRECT",
                }
                if payload not in evidence:
                    evidence.append(payload)

    if surface_id == "GOV-SURF-0882":
        evidence.append(
            {
                "path": "registry/governance_hash_registry.json",
                "location": "hash registry content",
                "evidence_type": "DIRECT",
            }
        )

    return evidence


def _role_assignment_record(
    surface_id: str,
    *,
    cluster: Mapping[str, Any],
    surface_index: Mapping[str, Mapping[str, Any]],
    ambiguity_index: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    surface_record = surface_index.get(surface_id, {})
    role_spec = ROLE_ASSIGNMENTS.get(surface_id, {})
    return {
        "surface_id": surface_id,
        "surface_path": normalize_path_like(surface_record.get("path_or_table")),
        "surface_type": normalize_path_like(surface_record.get("surface_type")),
        "authority_state": normalize_path_like(surface_record.get("authority_state")),
        "assigned_roles": list(role_spec.get("assigned_roles", [])),
        "explicitly_denied_roles": list(role_spec.get("explicitly_denied_roles", [])),
        "scope": dict(role_spec.get("scope", {})),
        "governing_evidence": _governing_evidence_for_surface(
            surface_id,
            cluster=cluster,
            surface_index=surface_index,
            ambiguity_index=ambiguity_index,
        ),
        "read_reachable": bool(surface_record.get("read_reachable")),
        "write_reachable": bool(surface_record.get("write_reachable")),
        "validation_reachable": bool(surface_record.get("validation_reachable")),
        "instruction_reachable": "INSTRUCTION_AUTHORITY" in role_spec.get("assigned_roles", []),
    }


def _validation_reducer_assignment(
    cluster: Mapping[str, Any],
    validation_map: Mapping[str, Any],
) -> dict[str, Any]:
    records = list(validation_map.get("records", []))
    canonical = next((record for record in records if record.get("validator_id") == "GOV-SURF-0972"), {})
    supporting = [record for record in records if record.get("validator_id") != "GOV-SURF-0972"]
    return {
        "canonical_invocation": "python -m scripts.global_validate",
        "canonical_reducer_rule_id": VALIDATION_REDUCTION_RULE_ID,
        "canonical_reducer_surface_id": canonical.get("validator_id", "GOV-SURF-0972"),
        "canonical_reducer_surface_path": canonical.get("validator_path", "scripts/global_validate.py"),
        "validated_target": cluster.get("governed_domain", {}).get("domain_id"),
        "governing_rule_ids": list(VALIDATION_PARTITION_RULE_IDS),
        "supporting_validator_ids": [record.get("validator_id") for record in supporting],
        "supporting_validator_paths": [record.get("validator_path") for record in supporting],
        "terminal_status_effect": {
            "scope_partition_gate": "PASS",
            "inventory_completion_gate": "BLOCKED",
            "reason": "The selected cluster is partitioned into explicit non-overlapping authority roles, but the broader inventory remains incomplete.",
        },
        "active_status": "ACTIVE",
    }


def _instruction_partition(surface_index: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    entries = []
    for surface_id in INSTRUCTION_SURFACE_IDS:
        surface = surface_index.get(surface_id, {})
        entries.append(
            {
                "surface_id": surface_id,
                "surface_path": normalize_path_like(surface.get("path_or_table")),
                "surface_type": normalize_path_like(surface.get("surface_type")),
                "assigned_roles": ["INSTRUCTION_AUTHORITY"],
                "explicitly_denied_roles": [
                    "REGISTRY_STATE_AUTHORITY",
                    "REGISTRY_WRITE_AUTHORITY",
                    "VALIDATION_INVOCATION_AUTHORITY",
                    "VALIDATION_REDUCTION_AUTHORITY",
                ],
                "scope": normalize_path_like(surface.get("declared_scope")) or "prescriptive guidance only",
            }
        )
    return {
        "primary_surface": "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
        "role": "INSTRUCTION_AUTHORITY",
        "required_content": [
            "Canonical validation invocation",
            "Governance-only invocation and its limited scope",
            "Terminal status meanings",
            "Blocked-environment reporting rule",
            "Statement that the document does not create registry authority",
            "References to the live core rules controlling validation",
        ],
        "instruction_surface_assignments": entries,
        "constraint": "Instruction text may describe authority but may not serve as the sole proof of registry-state authority.",
    }


def _generated_evidence_partition(surface_index: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    entries = []
    for surface_id in GENERATED_EVIDENCE_SURFACE_IDS:
        surface = surface_index.get(surface_id, {})
        entries.append(
            {
                "surface_id": surface_id,
                "surface_path": normalize_path_like(surface.get("path_or_table")),
                "surface_type": normalize_path_like(surface.get("surface_type")),
                "authority_effect": "NONE",
                "generation_note": "Derived evidence surface; not a live authority source.",
            }
        )
    return {
        "surfaces": entries,
        "authority_effect": "NONE",
        "requirements": [
            "Reference source authority identifiers.",
            "Reference source hashes where applicable.",
            "Declare generation method.",
            "Declare whether the output is current or stale.",
            "Never be selected as a write target for live authority.",
        ],
    }


def _resolved_claims(
    cluster: Mapping[str, Any],
    ambiguity_index: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    for record in cluster.get("included_records", []):
        ambiguity_record = ambiguity_index.get(record["surface_id"], {})
        for claim in _claim_ids(ambiguity_record):
            resolved.append(
                {
                    "claim_id": claim["claim_id"],
                    "ambiguity_id": claim["ambiguity_id"],
                    "surface_id": record["surface_id"],
                    "question_index": claim["question_index"],
                    "question": claim["question"],
                    "closed_by_roles": list(ROLE_ASSIGNMENTS.get(record["surface_id"], {}).get("assigned_roles", [])),
                    "resolution_basis": "Non-overlapping authority scopes separate registry-state, validation, instruction, and generated-evidence roles.",
                }
            )
    resolved.sort(key=lambda item: (item["ambiguity_id"], item["question_index"], item["claim_id"]))
    return resolved


def _remaining_claims(
    queue_bundle: Mapping[str, Any],
    cluster: Mapping[str, Any],
    resolved_surface_ids: Sequence[str],
    *,
    ambiguity_index: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    resolved = set(resolved_surface_ids)
    remaining: list[dict[str, Any]] = []
    for record in queue_bundle.get("records", []):
        surface_id = normalize_path_like(record.get("source_record_id"))
        if surface_id in resolved:
            continue
        remaining.append(
            {
                "claim_id": record.get("ambiguity_id"),
                "ambiguity_id": record.get("ambiguity_id"),
                "surface_id": surface_id,
                "queue_position": int(record.get("queue_position") or 0),
                "risk_score": int(record.get("risk_score") or 0),
                "severity": normalize_path_like(record.get("severity")),
                "question_count": len(ambiguity_index.get(surface_id, {}).get("questions", [])),
                "status": "QUEUED",
                "reason": "Not directly closed by the current scope partition.",
            }
        )
    remaining.sort(key=lambda item: (item["queue_position"], item["claim_id"]))
    return remaining


def _queue_partition_artifact(
    cluster: Mapping[str, Any],
    queue_bundle: Mapping[str, Any],
    resolved_claims: Sequence[Mapping[str, Any]],
    remaining_claims: Sequence[Mapping[str, Any]],
    *,
    ambiguity_index: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    resolved_surface_ids = {claim["surface_id"] for claim in resolved_claims}
    resolved_question_counts: dict[str, int] = {}
    for claim in resolved_claims:
        resolved_question_counts[claim["surface_id"]] = len(ambiguity_index.get(claim["surface_id"], {}).get("questions", []))
    resolved_records = [
        {
            "ambiguity_id": record.get("ambiguity_id"),
            "surface_id": record.get("source_record_id"),
            "queue_position": int(record.get("queue_position") or 0),
            "risk_score": int(record.get("risk_score") or 0),
            "severity": normalize_path_like(record.get("severity")),
            "status": "RESOLVED_BY_SCOPE_PARTITION",
            "resolved_question_count": resolved_question_counts.get(normalize_path_like(record.get("source_record_id")), 0),
        }
        for record in queue_bundle.get("records", [])
        if normalize_path_like(record.get("source_record_id")) in resolved_surface_ids
    ]
    resolved_records.sort(key=lambda item: (item["queue_position"], item["ambiguity_id"]))
    basis = {
        "schema_id": "governance_q0_scope_partition_queue_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "cluster_id": cluster["cluster_id"],
        "resolved_records": resolved_records,
        "remaining_claims": list(remaining_claims),
    }
    return {
        "schema_id": "governance_q0_scope_partition_queue_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "cluster_id": cluster["cluster_id"],
        "queue_group": cluster["queue_group"],
        "resolved_record_count": len(resolved_records),
        "resolved_question_count": len(resolved_claims),
        "remaining_record_count": len(remaining_claims),
        "resolved_records": resolved_records,
        "remaining_records": list(remaining_claims),
        "logical_hash": logical_sha256(basis),
    }


def _before_state(
    cluster: Mapping[str, Any],
    queue_bundle: Mapping[str, Any],
    candidate_inventory: Mapping[str, Any],
) -> dict[str, Any]:
    basis = {
        "schema_id": "governance_q0_scope_partition_state_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "phase": "before",
        "cluster_id": cluster["cluster_id"],
        "queue_group": cluster["queue_group"],
        "selected_candidate_count": candidate_inventory["record_count"],
        "selected_surface_ids": [record["surface_id"] for record in cluster.get("included_records", [])],
        "queue_record_count": len(queue_bundle.get("records", [])),
        "blocked_record_count": len(queue_bundle.get("records", [])),
    }
    state = {
        "schema_id": "governance_q0_scope_partition_state_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "phase": "before",
        "cluster_id": cluster["cluster_id"],
        "queue_group": cluster["queue_group"],
        "selected_candidate_count": candidate_inventory["record_count"],
        "selected_surface_ids": [record["surface_id"] for record in cluster.get("included_records", [])],
        "queue_record_count": len(queue_bundle.get("records", [])),
        "blocked_record_count": len(queue_bundle.get("records", [])),
        "resolved_record_count": 0,
        "resolved_question_count": 0,
        "remaining_record_count": len(queue_bundle.get("records", [])),
        "remaining_blocking_ambiguities": len(queue_bundle.get("records", [])),
        "status": "BEFORE_PARTITION",
        "logical_hash": logical_sha256(basis),
    }
    return state


def _after_state(
    cluster: Mapping[str, Any],
    partition: Mapping[str, Any],
    queue_bundle: Mapping[str, Any],
    resolved_claims: Sequence[Mapping[str, Any]],
    remaining_claims: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    basis = {
        "schema_id": "governance_q0_scope_partition_state_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "phase": "after",
        "cluster_id": cluster["cluster_id"],
        "partition_id": partition["partition_id"],
        "queue_group": cluster["queue_group"],
        "resolved_record_count": len({claim["surface_id"] for claim in resolved_claims}),
        "resolved_question_count": len(resolved_claims),
        "remaining_record_count": len(remaining_claims),
        "remaining_blocking_ambiguities": len(remaining_claims),
        "role_assignments": partition["role_assignments"],
        "write_owner_assignments": partition["write_owner_assignments"],
        "validation_reducer_assignment": partition["validation_reducer_assignment"],
    }
    return {
        "schema_id": "governance_q0_scope_partition_state_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "phase": "after",
        "cluster_id": cluster["cluster_id"],
        "partition_id": partition["partition_id"],
        "queue_group": cluster["queue_group"],
        "resolved_record_count": len({claim["surface_id"] for claim in resolved_claims}),
        "resolved_question_count": len(resolved_claims),
        "remaining_record_count": len(remaining_claims),
        "remaining_blocking_ambiguities": len(remaining_claims),
        "role_assignments": partition["role_assignments"],
        "write_owner_assignments": partition["write_owner_assignments"],
        "validation_reducer_assignment": partition["validation_reducer_assignment"],
        "instruction_surface_assignments": partition["instruction_partition"]["instruction_surface_assignments"],
        "generated_evidence_assignments": partition["generated_evidence_partition"]["surfaces"],
        "status": "AFTER_PARTITION",
        "logical_hash": logical_sha256(basis),
    }


def _diff_state(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    basis = {
        "schema_id": "governance_q0_scope_partition_diff_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "before_hash": before["logical_hash"],
        "after_hash": after["logical_hash"],
        "resolved_record_count_delta": int(after["resolved_record_count"]) - int(before["resolved_record_count"]),
        "resolved_question_count_delta": int(after["resolved_question_count"]) - int(before["resolved_question_count"]),
        "remaining_record_count_delta": int(after["remaining_record_count"]) - int(before["remaining_record_count"]),
        "remaining_blocking_ambiguities_delta": int(after["remaining_blocking_ambiguities"]) - int(before["remaining_blocking_ambiguities"]),
    }
    return {
        "schema_id": "governance_q0_scope_partition_diff_v1",
        "schema_version": "1.0.0",
        "patch_id": PATCH_ID,
        "before_hash": before["logical_hash"],
        "after_hash": after["logical_hash"],
        "resolved_record_count_delta": int(after["resolved_record_count"]) - int(before["resolved_record_count"]),
        "resolved_question_count_delta": int(after["resolved_question_count"]) - int(before["resolved_question_count"]),
        "remaining_record_count_delta": int(after["remaining_record_count"]) - int(before["remaining_record_count"]),
        "remaining_blocking_ambiguities_delta": int(after["remaining_blocking_ambiguities"]) - int(before["remaining_blocking_ambiguities"]),
        "role_assignment_count": len(after["role_assignments"]),
        "write_owner_count": len(after["write_owner_assignments"]),
        "validation_support_count": len(after["validation_reducer_assignment"]["supporting_validator_ids"]),
        "logical_hash": logical_sha256(basis),
    }


def _partition_id(
    cluster: Mapping[str, Any],
    role_assignments: Sequence[Mapping[str, Any]],
    write_owner_assignments: Sequence[Mapping[str, Any]],
    validation_assignment: Mapping[str, Any],
) -> str:
    basis = {
        "cluster_id": cluster["cluster_id"],
        "governed_domain_id": cluster["governed_domain"]["domain_id"],
        "role_assignments": [
            {
                "surface_id": record["surface_id"],
                "assigned_roles": list(record["assigned_roles"]),
            }
            for record in role_assignments
        ],
        "write_owner_assignments": [
            {
                "scope_id": record["scope_id"],
                "registry_path": record["registry_path"],
                "authorized_writer_id": record["authorized_writer_id"],
            }
            for record in write_owner_assignments
        ],
        "validation_assignment": {
            "canonical_invocation": validation_assignment["canonical_invocation"],
            "canonical_reducer_rule_id": validation_assignment["canonical_reducer_rule_id"],
            "canonical_reducer_surface_id": validation_assignment["canonical_reducer_surface_id"],
        },
    }
    return "Q0-SCOPE-PARTITION-" + logical_sha256(basis)[:16].upper()


def _authority_roles() -> list[dict[str, Any]]:
    return [
        {"role_id": role_id, **ROLE_DEFINITIONS[role_id]}
        for role_id in ROLE_IDS
    ]


def _core_rule() -> dict[str, Any]:
    return {
        "rule_id": CORE_RULE_ID,
        "title": CORE_RULE_TITLE,
        "status": "LIVE",
        "authority_type": "CORE_GOVERNANCE_RULE",
        "scope": "Selected Q0 registry-state, validation, instruction, and generated-evidence surfaces only.",
        "effect": "Separates live authority roles into non-overlapping scopes without conferring authority by implication.",
        "statement": (
            "A governed domain may contain multiple live authority surfaces only when each surface has an explicit, "
            "non-overlapping authority role. State authority, mutation authority, validation authority, and instruction "
            "authority must be separately declared. No surface may exercise another role by implication."
        ),
        "authority_effect": "LIVE_SCOPE_CONSTRAINT",
        "role_constraints": [
            "Registry authority determines the authoritative stored governance state.",
            "Write authority determines which bounded mechanism may mutate that state.",
            "Validation authority determines whether governed state satisfies applicable rules.",
            "Instruction authority documents required procedures and interfaces but cannot itself mutate or validate live state.",
            "Generated reports remain derived evidence and hold none of these authorities unless separately declared.",
        ],
        "prohibited_interpretations": [
            "listed means authorized",
            "generated means live authority",
            "documentation means mutation authority",
            "validation invocation means registry ownership",
        ],
        "source_patch_id": PATCH_ID,
    }


def _registry_state_partition() -> dict[str, Any]:
    return {
        "authority_principle": "Registry records are authoritative for stored governance state only within their declared schema and record scope.",
        "required_proofs": [
            "Each live rule is stored in its declared core-rule authority location.",
            "Each patch state is stored in its declared patch registry location.",
            "Each transition is stored in its declared transition location.",
            "The ledger records history but does not independently override the current state record.",
            "The hash registry proves integrity but does not define semantic authority.",
        ],
        "potential_subpartitions": [
            {
                "scope": "CORE_RULE_STATE",
                "authority_surface": "governance/core_rules/",
                "write_owner_id": "scripts/governance/register_q0_authority_scope_partition.py",
            },
            {
                "scope": "PATCH_STATE",
                "authority_surface": "governance/authority_partitions/",
                "write_owner_id": "scripts/governance/register_q0_authority_scope_partition.py",
            },
            {
                "scope": "CHANGE_HISTORY",
                "authority_surface": "registry/governance_change_ledger.json",
                "write_owner_id": "scripts/governance/register_q0_authority_scope_partition.py",
            },
            {
                "scope": "INTEGRITY_HASHES",
                "authority_surface": "registry/governance_hash_registry.json",
                "write_owner_id": "scripts/governance/register_q0_authority_scope_partition.py",
            },
            {
                "scope": "TOOL_ROUTING_METADATA",
                "authority_surface": "governance/live/tool_routing_manifest.json",
                "write_owner_id": "scripts/governance/register_q0_authority_scope_partition.py",
            },
        ],
        "constraint": "These are complementary state scopes, not competing global authorities.",
    }


def _selected_claim_basis(
    cluster: Mapping[str, Any],
    resolved_claims: Sequence[Mapping[str, Any]],
    remaining_claims: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_id": PARTITION_SCHEMA_ID,
        "schema_version": PARTITION_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "cluster_id": cluster["cluster_id"],
        "resolved_record_count": len({claim["surface_id"] for claim in resolved_claims}),
        "resolved_question_count": len(resolved_claims),
        "remaining_record_count": len(remaining_claims),
        "remaining_blocking_ambiguities": len(remaining_claims),
    }


def build_q0_authority_scope_partition_bundle(
    *,
    surface_inventory: Mapping[str, Any] | None = None,
    ambiguity_register: Mapping[str, Any] | None = None,
    queue_bundle: Mapping[str, Any] | None = None,
    relationship_artifact: Mapping[str, Any] | None = None,
    source_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    surface_payload = dict(surface_inventory or load_surface_inventory())
    ambiguity_payload = dict(ambiguity_register or load_ambiguity_register())
    queue_payload = dict(queue_bundle or _load_json("outputs/governance_inventory/governance_remediation_queue.json"))
    relationship_payload = dict(
        relationship_artifact or _load_json("outputs/governance_inventory/governance_authority_relationships.json")
    )

    cluster = select_q0_resolution_cluster(
        surface_inventory=surface_payload,
        ambiguity_register=ambiguity_payload,
        queue_bundle=queue_payload,
        relationship_artifact=relationship_payload,
        source_snapshot=source_snapshot,
    )
    candidate_inventory = build_authority_candidate_inventory(
        cluster,
        surface_inventory=surface_payload,
        queue_bundle=queue_payload,
    )
    validation_map = build_validation_path_map(candidate_inventory, cluster)

    surface_index = _surface_index(surface_payload)
    ambiguity_index = _ambiguity_index(ambiguity_payload)
    queue_index = _queue_index(queue_payload)

    role_assignments = [
        _role_assignment_record(surface_id, cluster=cluster, surface_index=surface_index, ambiguity_index=ambiguity_index)
        for surface_id in ROLE_ASSIGNMENT_ORDER
    ]
    role_assignments.sort(key=lambda item: (ROLE_ASSIGNMENT_ORDER.index(item["surface_id"]), item["surface_id"]))

    validation_assignment = _validation_reducer_assignment(cluster, validation_map)
    write_owner_assignments = [dict(record) for record in WRITE_OWNER_ASSIGNMENTS]
    partition_id = _partition_id(cluster, role_assignments, write_owner_assignments, validation_assignment)

    resolved_claims = _resolved_claims(cluster, ambiguity_index)
    remaining_claims = _remaining_claims(
        queue_payload,
        cluster,
        [record["surface_id"] for record in cluster.get("included_records", [])],
        ambiguity_index=ambiguity_index,
    )

    instruction_partition = _instruction_partition(surface_index)
    generated_evidence_partition = _generated_evidence_partition(surface_index)
    registry_state_partition = _registry_state_partition()

    partition = {
        "schema_id": PARTITION_SCHEMA_ID,
        "schema_version": PARTITION_SCHEMA_VERSION,
        "patch_id": PATCH_ID,
        "generated_at": GENERATED_AT,
        "partition_id": partition_id,
        "cluster_id": cluster["cluster_id"],
        "governed_domain_id": cluster["governed_domain"]["domain_id"],
        "governed_domain": dict(cluster["governed_domain"]),
        "core_rule_reference": {
            "rule_id": CORE_RULE_ID,
            "path": str(CORE_RULE_PATH.relative_to(ROOT)).replace("\\", "/"),
        },
        "authority_roles": _authority_roles(),
        "role_assignments": role_assignments,
        "prohibited_role_overlaps": PROHIBITED_ROLE_OVERLAPS,
        "registry_state_partition": registry_state_partition,
        "write_owner_assignments": write_owner_assignments,
        "validation_reducer_assignment": validation_assignment,
        "validation_partition": {
            "canonical_invocation": validation_assignment["canonical_invocation"],
            "terminal_reducer_rule_id": validation_assignment["canonical_reducer_rule_id"],
            "terminal_reducer_surface_id": validation_assignment["canonical_reducer_surface_id"],
            "terminal_reducer_surface_path": validation_assignment["canonical_reducer_surface_path"],
            "supporting_validator_ids": validation_assignment["supporting_validator_ids"],
            "supporting_validator_paths": validation_assignment["supporting_validator_paths"],
            "governing_rule_ids": validation_assignment["governing_rule_ids"],
            "active_status": validation_assignment["active_status"],
        },
        "instruction_partition": instruction_partition,
        "generated_evidence_partition": generated_evidence_partition,
        "resolved_ambiguity_claims": resolved_claims,
        "remaining_ambiguity_claims": remaining_claims,
        "resolved_ambiguity_count": len({claim["surface_id"] for claim in resolved_claims}),
        "resolved_question_count": len(resolved_claims),
        "remaining_blocking_ambiguities": len(remaining_claims),
        "governing_rule_ids": [
            "GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001",
            "GOVERNANCE_Q0_CLUSTER_COHERENCE_001",
            "GOVERNANCE_VALIDATION_FAIL_CLOSED_001",
            "GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001",
        ],
        "rollback_snapshot_id": "Q0-SCOPE-SNAPSHOT-" + logical_sha256(
            {
                "cluster_id": cluster["cluster_id"],
                "source_snapshot_hash": cluster["source_snapshot"]["logical_snapshot_sha256"],
                "partition_id": partition_id,
                "resolved_question_count": len(resolved_claims),
            }
        )[:16].upper(),
        "status": "PARTITIONED",
        "authority_effect": "LIVE_SCOPE_CONSTRAINT",
        "scope_partition_contract": {
            "schema_id": PARTITION_SCHEMA_ID,
            "status": "LIVE",
            "identity_rule": "Deterministic digest over the selected cluster, governed domain, role assignments, write owners, and reducer assignment.",
            "role_overlaps_blocked": True,
        },
        "summary": {
            "selected_candidate_count": candidate_inventory["record_count"],
            "resolved_record_count": len({claim["surface_id"] for claim in resolved_claims}),
            "resolved_question_count": len(resolved_claims),
            "remaining_record_count": len(remaining_claims),
            "remaining_blocking_ambiguities": len(remaining_claims),
            "completion_mode": "SEPARATE_NON_OVERLAPPING_SCOPES",
        },
        "source_snapshot": dict(cluster["source_snapshot"]),
        "queue_source_hashes": dict(cluster["queue_source_hashes"]),
    }
    partition["logical_hash"] = logical_sha256(
        {
            "schema_id": partition["schema_id"],
            "schema_version": partition["schema_version"],
            "patch_id": partition["patch_id"],
            "generated_at": partition["generated_at"],
            "partition_id": partition["partition_id"],
            "cluster_id": partition["cluster_id"],
            "governed_domain_id": partition["governed_domain_id"],
            "authority_roles": partition["authority_roles"],
            "role_assignments": partition["role_assignments"],
            "prohibited_role_overlaps": partition["prohibited_role_overlaps"],
            "registry_state_partition": partition["registry_state_partition"],
            "write_owner_assignments": partition["write_owner_assignments"],
            "validation_reducer_assignment": partition["validation_reducer_assignment"],
            "validation_partition": partition["validation_partition"],
            "instruction_partition": partition["instruction_partition"],
            "generated_evidence_partition": partition["generated_evidence_partition"],
            "resolved_ambiguity_claims": partition["resolved_ambiguity_claims"],
            "remaining_ambiguity_claims": partition["remaining_ambiguity_claims"],
            "governing_rule_ids": partition["governing_rule_ids"],
            "rollback_snapshot_id": partition["rollback_snapshot_id"],
            "status": partition["status"],
            "authority_effect": partition["authority_effect"],
            "summary": partition["summary"],
            "source_snapshot": partition["source_snapshot"],
            "queue_source_hashes": partition["queue_source_hashes"],
        }
    )

    before_state = _before_state(cluster, queue_payload, candidate_inventory)
    after_state = _after_state(cluster, partition, queue_payload, resolved_claims, remaining_claims)
    diff_state = _diff_state(before_state, after_state)
    queue_artifact = _queue_partition_artifact(
        cluster,
        queue_payload,
        resolved_claims,
        remaining_claims,
        ambiguity_index=ambiguity_index,
    )

    before_state["resolved_record_count"] = 0
    before_state["resolved_question_count"] = 0
    before_state["remaining_record_count"] = len(queue_payload.get("records", []))
    before_state["remaining_blocking_ambiguities"] = len(queue_payload.get("records", []))
    after_state["resolved_record_count"] = len({claim["surface_id"] for claim in resolved_claims})
    after_state["resolved_question_count"] = len(resolved_claims)
    after_state["remaining_blocking_ambiguities"] = len(remaining_claims)

    claim_basis = _selected_claim_basis(cluster, resolved_claims, remaining_claims)

    review_markdown = build_q0_authority_scope_partition_review_markdown(
        {
            "cluster": cluster,
            "partition": partition,
            "resolved_claims": resolved_claims,
            "remaining_claims": remaining_claims,
            "queue_artifact": queue_artifact,
        }
    )

    return {
        "cluster": cluster,
        "candidate_inventory": candidate_inventory,
        "core_rule": _core_rule(),
        "partition": partition,
        "before_state": before_state,
        "after_state": after_state,
        "diff": diff_state,
        "queue_artifact": queue_artifact,
        "resolved_claim_basis": claim_basis,
        "review_markdown": review_markdown,
        "artifacts": {},
    }


def build_q0_authority_scope_partition_review_markdown(bundle: Mapping[str, Any]) -> str:
    cluster = bundle["cluster"]
    partition = bundle["partition"]
    resolved_claims = bundle["resolved_claims"]
    remaining_claims = bundle["remaining_claims"]
    queue_artifact = bundle["queue_artifact"]
    lines = [
        "# Q0 Authority Scope Partition Review",
        "",
        "## Scope",
        "Partition the selected Q0 domain into explicit non-overlapping authority roles.",
        "",
        "## Directly Observed",
        f"- Cluster ID: `{cluster['cluster_id']}`",
        f"- Partition ID: `{partition['partition_id']}`",
        f"- Resolved ambiguity records: {partition['resolved_ambiguity_count']}",
        f"- Resolved question strings: {partition['resolved_question_count']}",
        f"- Remaining blocking ambiguities: {partition['remaining_blocking_ambiguities']}",
        f"- Queue remaining records: {queue_artifact['remaining_record_count']}",
        "",
        "## Authority Roles",
    ]
    for role in partition["authority_roles"]:
        lines.append(f"- {role['role_id']}: {role['purpose']}")
    lines.extend(
        [
            "",
            "## Resolution",
            f"- Canonical validation invocation: `{partition['validation_partition']['canonical_invocation']}`",
            f"- Terminal reducer rule: `{partition['validation_partition']['terminal_reducer_rule_id']}`",
            f"- Write owners: {len(partition['write_owner_assignments'])}",
            f"- Instruction surfaces: {len(partition['instruction_partition']['instruction_surface_assignments'])}",
            f"- Generated evidence surfaces: {len(partition['generated_evidence_partition']['surfaces'])}",
            "",
            "## Resolved Claims",
        ]
    )
    for claim in resolved_claims[:12]:
        lines.append(f"- {claim['claim_id']}: {claim['question']}")
    lines.extend(
        [
            "",
            "## Remaining Claims",
            f"- Remaining claim records: {len(remaining_claims)}",
            "",
            "## Failure Modes / Uncertainty",
            "- The inventory remains partial.",
            "- The broader completion gate remains blocked by unresolved ambiguities.",
            "- The partition does not alter unrelated dirty workspace changes.",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _repo_relative(path: str | Path) -> str:
    return str(Path(path).resolve().relative_to(ROOT)).replace("\\", "/")


def write_q0_authority_scope_partition_artifacts(
    *,
    core_rule_path: str | Path,
    partition_path: str | Path,
    before_state_path: str | Path,
    after_state_path: str | Path,
    diff_path: str | Path,
    write_owners_path: str | Path,
    validation_path: str | Path,
    instruction_path: str | Path,
    queue_path: str | Path,
    review_path: str | Path,
    surface_inventory: Mapping[str, Any] | None = None,
    ambiguity_register: Mapping[str, Any] | None = None,
    queue_bundle: Mapping[str, Any] | None = None,
    relationship_artifact: Mapping[str, Any] | None = None,
    source_snapshot: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = build_q0_authority_scope_partition_bundle(
        surface_inventory=surface_inventory,
        ambiguity_register=ambiguity_register,
        queue_bundle=queue_bundle,
        relationship_artifact=relationship_artifact,
        source_snapshot=source_snapshot,
    )
    _write_json(Path(core_rule_path), bundle["core_rule"])
    _write_json(Path(partition_path), bundle["partition"])
    _write_json(Path(before_state_path), bundle["before_state"])
    _write_json(Path(after_state_path), bundle["after_state"])
    _write_json(Path(diff_path), bundle["diff"])
    _write_json(Path(write_owners_path), {"write_owner_assignments": bundle["partition"]["write_owner_assignments"]})
    _write_json(Path(validation_path), bundle["partition"]["validation_partition"])
    _write_json(Path(instruction_path), bundle["partition"]["instruction_partition"])
    _write_json(Path(queue_path), bundle["queue_artifact"])
    Path(review_path).parent.mkdir(parents=True, exist_ok=True)
    Path(review_path).write_text(bundle["review_markdown"], encoding="utf-8", newline="\n")

    bundle["artifacts"] = {
        "core_rule": {"path": _repo_relative(core_rule_path), "hash": hashlib.sha256(Path(core_rule_path).read_bytes()).hexdigest()},
        "partition": {"path": _repo_relative(partition_path), "hash": hashlib.sha256(Path(partition_path).read_bytes()).hexdigest()},
        "before_state": {"path": _repo_relative(before_state_path), "hash": hashlib.sha256(Path(before_state_path).read_bytes()).hexdigest()},
        "after_state": {"path": _repo_relative(after_state_path), "hash": hashlib.sha256(Path(after_state_path).read_bytes()).hexdigest()},
        "diff": {"path": _repo_relative(diff_path), "hash": hashlib.sha256(Path(diff_path).read_bytes()).hexdigest()},
        "write_owners": {"path": _repo_relative(write_owners_path), "hash": hashlib.sha256(Path(write_owners_path).read_bytes()).hexdigest()},
        "validation": {"path": _repo_relative(validation_path), "hash": hashlib.sha256(Path(validation_path).read_bytes()).hexdigest()},
        "instruction": {"path": _repo_relative(instruction_path), "hash": hashlib.sha256(Path(instruction_path).read_bytes()).hexdigest()},
        "queue": {"path": _repo_relative(queue_path), "hash": hashlib.sha256(Path(queue_path).read_bytes()).hexdigest()},
        "review": {"path": _repo_relative(review_path), "hash": hashlib.sha256(Path(review_path).read_bytes()).hexdigest()},
    }
    return bundle
