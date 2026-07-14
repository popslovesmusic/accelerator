from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.governance_inventory import build_q0_authority_scope_partition_bundle


ROLE_IDS = (
    "REGISTRY_STATE_AUTHORITY",
    "REGISTRY_WRITE_AUTHORITY",
    "VALIDATION_INVOCATION_AUTHORITY",
    "VALIDATION_REDUCTION_AUTHORITY",
    "INSTRUCTION_AUTHORITY",
    "GENERATED_EVIDENCE",
)

PRIMARY_TARGETS = (
    "scripts/query_governance.py",
    "tools/governance_inventory/__init__.py",
    "tools/governance_inventory/authority_scope_partition.py",
    "scripts/governance/register_q0_authority_scope_partition.py",
    "scripts/global_validate.py",
)

ROLE_TARGET_MAP = {
    "registry/governance_change_ledger.json": "REGISTRY_STATE_AUTHORITY",
    "governance/live/tool_routing_manifest.json": "REGISTRY_STATE_AUTHORITY",
    "governance/core_rules/GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json": "REGISTRY_WRITE_AUTHORITY",
    "governance/authority_partitions/Q0_AUTHORITY_SCOPE_PARTITION_001.json": "REGISTRY_WRITE_AUTHORITY",
    "registry/governance_hash_registry.json": "GENERATED_EVIDENCE",
    "scripts/global_validate.py": "VALIDATION_INVOCATION_AUTHORITY",
    "scripts/query_governance.py": "GENERATED_EVIDENCE",
    "docs/governance/GLOBAL_VALIDATION_ROUTINE.md": "INSTRUCTION_AUTHORITY",
    "AGENTS.md": "INSTRUCTION_AUTHORITY",
    "GEMINI.md": "INSTRUCTION_AUTHORITY",
    "governance/program_task_registry.json": "INSTRUCTION_AUTHORITY",
    "governance/live/master_work_index.json": "GENERATED_EVIDENCE",
}


@dataclass(frozen=True)
class RoleAccessResult:
    role_id: str
    authority_source: str
    authority_effect: str
    decision: str
    reason: str
    evidence_paths: list[str]
    warnings: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "role_id": self.role_id,
            "authority_source": self.authority_source,
            "authority_effect": self.authority_effect,
            "decision": self.decision,
            "reason": self.reason,
            "evidence_paths": self.evidence_paths,
            "warnings": self.warnings,
        }


def _normalize_repo_path(path: str | None) -> str | None:
    if not path:
        return None
    return str(Path(path)).replace("\\", "/")


def load_q0_partition() -> dict[str, Any]:
    return build_q0_authority_scope_partition_bundle()["partition"]


def _role_index(partition: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["role_id"]: entry for entry in partition["authority_roles"]}


def _partition_paths(partition: dict[str, Any], role_id: str) -> list[str]:
    paths: list[str] = []
    if role_id == "REGISTRY_STATE_AUTHORITY":
        paths.extend([
            "registry/governance_change_ledger.json",
            "governance/live/tool_routing_manifest.json",
        ])
    elif role_id == "REGISTRY_WRITE_AUTHORITY":
        for assignment in partition.get("write_owner_assignments", []):
            path = assignment.get("registry_path")
            if path:
                paths.append(_normalize_repo_path(path))
    elif role_id in {"VALIDATION_INVOCATION_AUTHORITY", "VALIDATION_REDUCTION_AUTHORITY"}:
        validation = partition.get("validation_partition", {})
        path = validation.get("terminal_reducer_surface_path")
        if path:
            paths.append(_normalize_repo_path(path))
    elif role_id == "INSTRUCTION_AUTHORITY":
        paths.extend([
            "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
            "AGENTS.md",
            "GEMINI.md",
            "governance/program_task_registry.json",
        ])
    elif role_id == "GENERATED_EVIDENCE":
        paths.extend([
            "registry/governance_hash_registry.json",
            "scripts/query_governance.py",
            "governance/live/master_work_index.json",
        ])
    return [path for path in dict.fromkeys(path for path in paths if path)]


def get_authority_by_role(role_id: str) -> dict[str, Any]:
    partition = load_q0_partition()
    roles = _role_index(partition)
    normalized_role = str(role_id or "").strip().upper()
    if normalized_role not in ROLE_IDS:
        return {
            "role_id": normalized_role or None,
            "decision": "block",
            "reason": "Unknown authority role.",
            "authority_effect": "NONE",
            "authority_source": None,
            "evidence_paths": [],
            "warnings": ["Requested authority role is not part of the Q0 partition."],
        }

    role = roles[normalized_role]
    paths = _partition_paths(partition, normalized_role)
    authority_source = paths[0] if paths else partition["core_rule_reference"]["path"]
    return RoleAccessResult(
        role_id=normalized_role,
        authority_source=authority_source,
        authority_effect=partition["authority_effect"],
        decision="allow",
        reason=role["purpose"],
        evidence_paths=[partition["core_rule_reference"]["path"], *paths],
        warnings=[],
    ).as_dict()


def get_registry_state_authority() -> dict[str, Any]:
    return get_authority_by_role("REGISTRY_STATE_AUTHORITY")


def get_registry_write_authority() -> dict[str, Any]:
    return get_authority_by_role("REGISTRY_WRITE_AUTHORITY")


def get_validation_invocation_authority() -> dict[str, Any]:
    return get_authority_by_role("VALIDATION_INVOCATION_AUTHORITY")


def get_validation_reduction_authority() -> dict[str, Any]:
    return get_authority_by_role("VALIDATION_REDUCTION_AUTHORITY")


def get_instruction_authority() -> dict[str, Any]:
    return get_authority_by_role("INSTRUCTION_AUTHORITY")


def get_generated_evidence() -> dict[str, Any]:
    return get_authority_by_role("GENERATED_EVIDENCE")


def classify_target_role(target: str | None) -> str | None:
    normalized_target = _normalize_repo_path(target)
    if not normalized_target:
        return None
    return ROLE_TARGET_MAP.get(normalized_target)


def resolve_role_aware_authority(role_id: str, target: str | None = None) -> dict[str, Any]:
    result = get_authority_by_role(role_id)
    normalized_target = _normalize_repo_path(target)
    if not normalized_target:
        return result

    target_role = classify_target_role(normalized_target)
    if target_role is None:
        result["decision"] = "defer"
        result["reason"] = "Target is not part of the governed Q0 authority surface."
        result["warnings"] = ["Target was classified as NOT_AUTHORITY_ACCESS for the Q0 partition."]
        result["target"] = normalized_target
        return result

    if target_role != result["role_id"]:
        return {
            "role_id": result["role_id"],
            "target": normalized_target,
            "decision": "block",
            "reason": "Requested authority role does not match the governed target role.",
            "authority_effect": "NONE",
            "authority_source": normalized_target,
            "evidence_paths": [normalized_target, *result["evidence_paths"]],
            "warnings": [f"Target requires {target_role}, not {result['role_id']}."],
        }

    result["target"] = normalized_target
    if normalized_target not in result["evidence_paths"]:
        result["evidence_paths"].append(normalized_target)
    return result


def validate_write_boundary(
    scope_id: str | None,
    operation_type: str | None,
    writer_id: str | None,
    payload: dict[str, Any] | None,
    audit_identity: str | None,
) -> dict[str, Any]:
    partition = load_q0_partition()
    assignments = [
        item for item in partition.get("write_owner_assignments", [])
        if str(item.get("scope_id") or "").strip() == str(scope_id or "").strip()
    ]
    blockers: list[str] = []
    warnings: list[str] = []
    if not scope_id:
        blockers.append("scope_unknown")
    if not operation_type:
        blockers.append("operation_type_missing")
    if not writer_id:
        blockers.append("writer_missing")
    if not audit_identity:
        blockers.append("audit_identity_missing")
    if payload is None or not isinstance(payload, dict):
        blockers.append("schema_invalid_payload")
    if len(assignments) == 0:
        blockers.append("writer_missing")
    if len(assignments) > 1:
        blockers.append("writers_overlap")

    assignment = assignments[0] if len(assignments) == 1 else None
    if assignment is not None:
        allowed = {str(item).strip().upper() for item in assignment.get("allowed_operations", [])}
        normalized_operation = str(operation_type or "").strip().upper()
        if normalized_operation not in allowed:
            blockers.append("operation_outside_writer_contract")
        expected_writer = str(assignment.get("authorized_writer_id") or "").strip()
        if expected_writer and writer_id and str(writer_id).strip() != expected_writer:
            blockers.append("writer_not_authorized")
        if not assignment.get("atomicity_or_rollback_behavior"):
            blockers.append("rollback_missing")
        if not assignment.get("validation_before_write"):
            blockers.append("prewrite_checks_missing")

    return {
        "scope_id": scope_id,
        "operation_type": operation_type,
        "writer_id": writer_id,
        "decision": "allow" if not blockers else "block",
        "blockers": blockers,
        "warnings": warnings,
        "assignment": assignment,
    }


def build_live_authority_access_inventory() -> dict[str, Any]:
    records = [
        {
            "path": "scripts/query_governance.py",
            "classification": "MIXED_ROLE_LOOKUP",
            "behavior": "Resolves and returns authority information across multiple Q0 roles; generic access is now blocked unless a role is declared.",
        },
        {
            "path": "tools/governance_inventory/__init__.py",
            "classification": "INSTRUCTION_AUTHORITY",
            "behavior": "Exports partition builders and inventory helpers without mutating governance state.",
        },
        {
            "path": "tools/governance_inventory/authority_scope_partition.py",
            "classification": "REGISTRY_WRITE_AUTHORITY",
            "behavior": "Defines the governed role partition and exclusive write-owner contracts for Q0 registry state.",
        },
        {
            "path": "scripts/governance/register_q0_authority_scope_partition.py",
            "classification": "REGISTRY_WRITE_AUTHORITY",
            "behavior": "Canonical writer entry point for Q0 partition artifacts, ledger sync, and hash sync.",
        },
        {
            "path": "scripts/global_validate.py",
            "classification": "VALIDATION_INVOCATION_AUTHORITY",
            "behavior": "Canonical governed validation entry point with fail-closed terminal reduction.",
        },
    ]
    return {
        "schema_id": "governance_q0_live_authority_access_inventory_v1",
        "role_ids": list(ROLE_IDS),
        "records": records,
        "primary_targets": list(PRIMARY_TARGETS),
    }


def validate_validator_partition() -> dict[str, Any]:
    partition = load_q0_partition()
    validation = partition.get("validation_partition", {})
    blockers: list[str] = []
    if validation.get("canonical_invocation") != "python -m scripts.global_validate":
        blockers.append("canonical_validation_invocation_missing")
    if validation.get("terminal_reducer_rule_id") != "GOVERNANCE_VALIDATION_FAIL_CLOSED_001":
        blockers.append("terminal_reducer_missing")
    if not validation.get("supporting_validator_ids"):
        blockers.append("supporting_validators_missing")
    return {
        "decision": "allow" if not blockers else "block",
        "blockers": blockers,
        "validation_partition": validation,
    }
