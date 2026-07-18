from __future__ import annotations

from dataclasses import dataclass
import json
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
    "SUPPORTING_VALIDATOR",
    "SCHEMA_CONSTRAINT_SURFACE",
    "ROLE_AWARE_AUTHORITY_QUERY_SURFACE",
)

PROPOSAL_CANDIDATE_PATCH_STATUSES = frozenset(
    {
        "proposed",
        "proposed_for_induction",
        "proposed_personal_cleanup",
        "candidate",
        "registered_late",
    }
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
    "registry/governance/living_falsification_campaign_registry.json": "REGISTRY_STATE_AUTHORITY",
    "governance/core_rules/GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json": "REGISTRY_WRITE_AUTHORITY",
    "governance/authority_partitions/Q0_AUTHORITY_SCOPE_PARTITION_001.json": "REGISTRY_WRITE_AUTHORITY",
    "registry/governance_hash_registry.json": "GENERATED_EVIDENCE",
    "scripts/global_validate.py": "VALIDATION_INVOCATION_AUTHORITY",
    "scripts/query_governance.py": "ROLE_AWARE_AUTHORITY_QUERY_SURFACE",
    "docs/governance/GLOBAL_VALIDATION_ROUTINE.md": "INSTRUCTION_AUTHORITY",
    "AGENTS.md": "INSTRUCTION_AUTHORITY",
    "GEMINI.md": "INSTRUCTION_AUTHORITY",
    "governance/program_task_registry.json": "INSTRUCTION_AUTHORITY",
    "governance/live/master_work_index.json": "GENERATED_EVIDENCE",
    "tests/test_governed_context_capsule_v1.py": "SUPPORTING_VALIDATOR",
    "schemas/governed_context_capsule_v1.schema.json": "SCHEMA_CONSTRAINT_SURFACE",
    "registry/governance/schemas/RUN_MANIFEST_V1.json": "SCHEMA_CONSTRAINT_SURFACE",
}

SUPPLEMENTAL_ROLE_DEFINITIONS = {
    "SUPPORTING_VALIDATOR": {
        "authority_source": "tests/test_governed_context_capsule_v1.py",
        "authority_effect": "NONE",
        "reason": (
            "Bounded supporting validator for governed-context-capsule schema conformance, cache contract, "
            "and payload invariant checks. It may emit supporting test evidence only."
        ),
        "evidence_paths": [
            "governance/core_rules/GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json",
            "governance/authority_partitions/Q0_AUTHORITY_SCOPE_PARTITION_001.json",
            "tests/test_governed_context_capsule_v1.py",
            "schemas/governed_context_capsule_v1.schema.json",
            "scripts/query_governance.py",
        ],
    },
    "SCHEMA_CONSTRAINT_SURFACE": {
        "authority_source": "schemas/governed_context_capsule_v1.schema.json",
        "authority_effect": "NONE",
        "reason": (
            "Schema constraint surface defining governed structural contracts. "
            "It constrains admissible shape and content but does not invoke, reduce, or write live governance state."
        ),
        "evidence_paths": [
            "schemas/governed_context_capsule_v1.schema.json",
            "registry/governance/schemas/RUN_MANIFEST_V1.json",
            "registry/governance/living_falsification_campaign_registry.json",
            "tests/test_governed_context_capsule_v1.py",
            "scripts/query_governance.py",
        ],
    },
    "ROLE_AWARE_AUTHORITY_QUERY_SURFACE": {
        "authority_source": "scripts/query_governance.py",
        "authority_effect": "NONE",
        "reason": (
            "Role-aware authority query surface that resolves governed authority information but cannot "
            "become validation invocation, terminal reduction, or registry write authority by itself."
        ),
        "evidence_paths": [
            "scripts/query_governance.py",
            "governance/core_rules/GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json",
            "governance/authority_partitions/Q0_AUTHORITY_SCOPE_PARTITION_001.json",
        ],
    },
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


def classify_patch_record_lifecycle(target: str | None) -> dict[str, Any] | None:
    normalized_target = _normalize_repo_path(target)
    if not normalized_target:
        return None

    patch_path = Path(normalized_target)
    if not patch_path.suffix.lower() == ".json":
        return None
    if not (
        normalized_target.startswith("registry/governance/patches/")
        or normalized_target == "governance/artifact_hygiene_governance_patch_v1.json"
    ):
        return None

    file_path = Path.cwd() / patch_path
    if not file_path.exists():
        return None

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    status = payload.get("status")
    patch_id = payload.get("patch_id")
    lifecycle_scope = "patch_record"
    if status is None and normalized_target == "governance/artifact_hygiene_governance_patch_v1.json":
        governance_patch = payload.get("governance_patch", {})
        status = governance_patch.get("status")
        patch_id = governance_patch.get("id")
        lifecycle_scope = "governance_patch"

    normalized_status = str(status or "").strip().lower()
    if normalized_status not in PROPOSAL_CANDIDATE_PATCH_STATUSES:
        return None

    lifecycle_class = "CANDIDATE" if normalized_status in {"candidate", "registered_late"} else "PROPOSAL"
    return {
        "target": normalized_target,
        "patch_id": patch_id,
        "status": status,
        "normalized_status": normalized_status,
        "lifecycle_scope": lifecycle_scope,
        "lifecycle_class": lifecycle_class,
        "live_lookup_eligible": False,
    }


def classify_patch_record_explicit_none_authority_effect(target: str | None) -> dict[str, Any] | None:
    normalized_target = _normalize_repo_path(target)
    if not normalized_target or not normalized_target.startswith("registry/governance/patches/"):
        return None

    patch_path = Path(normalized_target)
    if patch_path.suffix.lower() != ".json":
        return None

    file_path = Path.cwd() / patch_path
    if not file_path.exists():
        return None

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    authority_effect = payload.get("authority_effect")
    if isinstance(authority_effect, dict):
        classification = str(authority_effect.get("classification") or "").strip().upper()
    else:
        classification = str(authority_effect or "").strip().upper()
    if classification != "NONE":
        return None

    return {
        "target": normalized_target,
        "patch_id": payload.get("patch_id"),
        "status": payload.get("status"),
        "authority_effect": authority_effect,
        "authority_effect_classification": classification,
        "live_lookup_eligible": False,
    }


def classify_patch_record_closeout_work_package(target: str | None) -> dict[str, Any] | None:
    normalized_target = _normalize_repo_path(target)
    if normalized_target != "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json":
        return None

    patch_path = Path(normalized_target)
    file_path = Path.cwd() / patch_path
    if not file_path.exists():
        return None

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    files_changed = payload.get("files_changed")
    if not isinstance(files_changed, list) or not files_changed:
        return None
    if "reports/inference-conservation-final-audit.json" not in files_changed:
        return None
    if "registry/governance/patches/PATCH_ACCELERATOR_INFERENCE_CONSERVATION_CLOSEOUT_055.json" not in files_changed:
        return None
    if "scripts/global_validate.py" in files_changed:
        return None
    if payload.get("status") != "PARTIAL":
        return None
    if payload.get("closeout_recommendation") != "PARTIAL":
        return None
    if payload.get("authority_effect") is not None:
        return None
    predecessor_patches = payload.get("predecessor_patches")
    patches_verified = payload.get("patches_verified")
    validation_results = payload.get("validation_results")
    if not isinstance(predecessor_patches, list) or len(predecessor_patches) != 5:
        return None
    if not isinstance(patches_verified, dict) or not isinstance(validation_results, dict):
        return None

    return {
        "target": normalized_target,
        "patch_id": payload.get("patch_id"),
        "status": payload.get("status"),
        "closeout_recommendation": payload.get("closeout_recommendation"),
        "predecessor_patches": predecessor_patches,
        "patches_verified": patches_verified,
        "validation_results": validation_results,
        "live_lookup_eligible": False,
    }


def classify_patch_record_deterministic_routing_component(target: str | None) -> dict[str, Any] | None:
    normalized_target = _normalize_repo_path(target)
    if normalized_target not in {
        "registry/governance/patches/PATCH_ACCELERATOR_DETERMINISTIC_DECISION_CACHE_053.json",
        "registry/governance/patches/PATCH_ACCELERATOR_DETERMINISTIC_ROUTING_AND_CANDIDATE_BOUNDING_054.json",
    }:
        return None

    patch_path = Path(normalized_target)
    file_path = Path.cwd() / patch_path
    if not file_path.exists():
        return None

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    patch_id = payload.get("patch_id")
    status = payload.get("status")

    if status != "PASS":
        return None

    return {
        "target": normalized_target,
        "patch_id": patch_id,
        "status": status,
        "live_lookup_eligible": False,
    }


def classify_patch_record_historical_applied(target: str | None) -> dict[str, Any] | None:
    normalized_target = _normalize_repo_path(target)
    if not normalized_target:
        return None

    patch_path = Path(normalized_target)
    if not patch_path.suffix.lower() == ".json":
        return None
    if not normalized_target.startswith("registry/governance/patches/"):
        return None

    file_path = Path.cwd() / patch_path
    if not file_path.exists():
        return None

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    patch_id = payload.get("patch_id")
    status = payload.get("status")

    if not status:
        return None

    normalized_status = str(status).strip().lower()
    if normalized_status not in {"applied"}:
        return None

    return {
        "target": normalized_target,
        "patch_id": patch_id,
        "status": status,
        "live_lookup_eligible": False,
    }


def classify_generated_view_component(target: str | None) -> dict[str, Any] | None:
    normalized_target = _normalize_repo_path(target)
    if not normalized_target:
        return None

    if normalized_target.startswith("outputs/"):
        return {
            "target": normalized_target,
            "live_lookup_eligible": False,
            "decision": "defer",
            "reason": "Generated output views and campaign reports are not eligible for live authority lookup.",
            "authority_owner": "generated_view",
        }

    if normalized_target in {
        "registry/db/migrations/20260703_governance_runtime_context_capsule_006.sql",
        "registry/db/migrations/20260703_governance_runtime_current_state_002.sql",
        "registry/db/migrations/20260703_governance_runtime_freshness_gate_010.sql",
        "registry/db/schema.sql",
        "scripts/db/orientation_scoring.py",
    }:
        if normalized_target in {
            "registry/db/migrations/20260703_governance_runtime_context_capsule_006.sql",
            "registry/db/migrations/20260703_governance_runtime_current_state_002.sql",
            "registry/db/migrations/20260703_governance_runtime_freshness_gate_010.sql",
        }:
            return {
                "target": normalized_target,
                "live_lookup_eligible": False,
                "decision": "allow",
                "reason": "Live DB runtime migrations are allowed runtime surfaces under the DB runtime gate.",
                "authority_owner": "db_runtime",
            }
        else:
            return {
                "target": normalized_target,
                "live_lookup_eligible": False,
                "decision": "defer",
                "reason": "DB schema definitions and scoring utilities are not eligible for live authority lookup.",
                "authority_owner": "db_runtime",
            }

    return None


def classify_duplicate_identity_component(target: str | None) -> dict[str, Any] | None:
    normalized_target = _normalize_repo_path(target)
    if not normalized_target:
        return None

    if "::" in normalized_target or normalized_target.endswith(".pyc") or normalized_target in {
        "scripts/db/db_health_check.py",
        "scripts/provenance/provenance_packet_builder.py",
        "scripts/db/build_supersession_edges.py",
    }:
        return {
            "target": normalized_target,
            "live_lookup_eligible": False,
            "decision": "defer",
            "reason": "Database schema components, bytecode cache files, and utility scripts are not eligible for live authority lookup.",
            "authority_owner": "duplicate_identity_or_doc",
        }

    return None


def classify_patch_record_executed_pass_boundary(target: str | None) -> dict[str, Any] | None:
    normalized_target = _normalize_repo_path(target)
    if not normalized_target:
        return None

    patch_path = Path(normalized_target)
    if not patch_path.suffix.lower() == ".json":
        return None
    if not (
        normalized_target.startswith("registry/governance/patches/")
        or normalized_target == "governance/artifact_hygiene_governance_patch_v1.json"
    ):
        return None

    file_path = Path.cwd() / patch_path
    if not file_path.exists():
        return None

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    patch_id = payload.get("patch_id")
    status = payload.get("status")

    if patch_id in {
        "PATCH_ACCELERATOR_DETERMINISTIC_DECISION_CACHE_053",
        "PATCH_ACCELERATOR_DETERMINISTIC_ROUTING_AND_CANDIDATE_BOUNDING_054",
    }:
        return None

    normalized_status = str(status or "").strip().upper()
    if normalized_status in {"APPLIED", "ACTIVE", "APPROVED"}:
        return None

    validation_dict = payload.get("validation")
    val_result = ""
    if isinstance(validation_dict, dict):
        val_result = str(validation_dict.get("result") or "").strip().upper()

    is_executed_or_pass = (
        normalized_status in {"EXECUTED", "PASS", "PASS_WITH_WARNINGS"}
        or val_result in {"PASS", "PASS_WITH_WARNINGS"}
    )
    if not is_executed_or_pass:
        return None

    # Check for explicit governed transition
    authority_effect = payload.get("authority_effect")
    if authority_effect is not None:
        return None

    return {
        "target": normalized_target,
        "patch_id": patch_id,
        "status": status,
        "normalized_status": normalized_status,
        "live_lookup_eligible": False,
    }



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
            "governance/live/master_work_index.json",
        ])
    elif role_id == "SUPPORTING_VALIDATOR":
        paths.extend([
            "tests/test_governed_context_capsule_v1.py",
            "schemas/governed_context_capsule_v1.schema.json",
            "scripts/query_governance.py",
        ])
    elif role_id == "SCHEMA_CONSTRAINT_SURFACE":
        paths.extend([
            "schemas/governed_context_capsule_v1.schema.json",
            "registry/governance/schemas/RUN_MANIFEST_V1.json",
            "registry/governance/living_falsification_campaign_registry.json",
            "tests/test_governed_context_capsule_v1.py",
            "scripts/query_governance.py",
        ])
    elif role_id == "ROLE_AWARE_AUTHORITY_QUERY_SURFACE":
        paths.extend([
            "scripts/query_governance.py",
            "governance/core_rules/GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json",
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

    if normalized_role in SUPPLEMENTAL_ROLE_DEFINITIONS:
        definition = SUPPLEMENTAL_ROLE_DEFINITIONS[normalized_role]
        return RoleAccessResult(
            role_id=normalized_role,
            authority_source=definition["authority_source"],
            authority_effect=definition["authority_effect"],
            decision="allow",
            reason=definition["reason"],
            evidence_paths=list(definition["evidence_paths"]),
            warnings=[],
        ).as_dict()

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
    result["authority_source"] = normalized_target
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
            "classification": "ROLE_AWARE_AUTHORITY_QUERY_SURFACE",
            "behavior": "Resolves governed authority information through explicit role-aware lookup and cannot become terminal validation authority by itself.",
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
        {
            "path": "tests/test_governed_context_capsule_v1.py",
            "classification": "SUPPORTING_VALIDATOR",
            "behavior": "Bounded supporting validator for governed-context-capsule schema, cache, and contract checks only.",
        },
        {
            "path": "schemas/governed_context_capsule_v1.schema.json",
            "classification": "SCHEMA_CONSTRAINT_SURFACE",
            "behavior": "Schema contract surface used by governed-context-capsule builders and supporting validators.",
        },
        {
            "path": "registry/governance/schemas/RUN_MANIFEST_V1.json",
            "classification": "SCHEMA_CONSTRAINT_SURFACE",
            "behavior": "Canonical run-manifest schema that constrains falsification-run structure without becoming live campaign-state authority.",
        },
        {
            "path": "registry/governance/living_falsification_campaign_registry.json",
            "classification": "REGISTRY_STATE_AUTHORITY",
            "behavior": "Living falsification campaign state registry preserving current governed campaign status independently of run-manifest schema conformance.",
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
