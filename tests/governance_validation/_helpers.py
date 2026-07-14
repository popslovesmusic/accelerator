from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_FILE_COUNT_SCANNED = 1017
EXPECTED_SURFACE_COUNT = 1083
EXPECTED_LIVE_AUTHORITY_COUNT = 77
EXPECTED_LIVE_AUTHORITY_DIGEST = "e69d8cd0477cef5fc4b9defc55ca61e7fa5c34945af4ee16e135f72cbe2f6e76"
EXPECTED_LOGICAL_SNAPSHOT_SHA256 = "b50c4526c8ac2a962de5d091714c3ab141f08459bf69275b768cf238690480e8"
EXPECTED_SOURCE_SCOPE = {
    "included_roots": [
        "docs/governance",
        "governance",
        "outputs/audits",
        "outputs/governance",
        "registry/db",
        "registry/governance",
        "reports",
        "scripts/agent_memory",
        "scripts/db",
        "scripts/governance",
        "scripts/provenance",
        "tests",
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
    "explicit_root_files": [
        "AGENTS.md",
        "GEMINI.md",
        "MATH_PROGRAM_NARRATIVE.md",
        "TODO.md",
        "docs/manual_repository_audit_2026_07_13.md",
        "docs/textbook/mono_process_textbook_complete.md",
    ],
}
EXPECTED_SOURCE_SNAPSHOT = {
    "workspace_root_identity": "acellorator@6ebf84a1e",
    "repository_commit": "6ebf84a1e",
    "included_roots": EXPECTED_SOURCE_SCOPE["included_roots"],
    "excluded_roots": EXPECTED_SOURCE_SCOPE["excluded_roots"],
    "explicit_root_files": EXPECTED_SOURCE_SCOPE["explicit_root_files"],
    "file_count_scanned": EXPECTED_FILE_COUNT_SCANNED,
    "surface_count_detected": EXPECTED_SURFACE_COUNT,
    "working_tree_dirty": True,
    "unrelated_changes_preserved": True,
    "inventory_artifact_hashes": {
        "AGENTS.md": "23aef552ee452c45dd60cbbc51f1c2cf5b798b5ea8d16a6ecd9051053da2800f",
        "GEMINI.md": "9f52e7fd83634de5e5d70acdcd83df64e4808d09da034e1bc8425fbbeb1e85a0",
        "MATH_PROGRAM_NARRATIVE.md": "7037938df21f3df2525e836b147ea329595fff548bbb1a962bf1b4680f9d7fdb",
        "TODO.md": "6acfcc7a3f4855159c0f5385227db7af482483b96492c929a90e7205bb93e861",
        "docs/manual_repository_audit_2026_07_13.md": "a16f4997f1ba7b17b11f4e3f188ecf530a38b2d9730052d1eefcb9ca290e30c7",
        "docs/textbook/mono_process_textbook_complete.md": "4a28ab99e7210e1e72605ffa2e46f29f27d5c7d28bdab8db906fd6ade194a787",
    },
    "logical_snapshot_sha256": EXPECTED_LOGICAL_SNAPSHOT_SHA256,
}
EXPECTED_INVENTORY_COUNTS = {
    "total_surfaces": 1083,
    "explicit_live_authorities": 77,
    "proposals": 52,
    "historical_surfaces": 177,
    "generated_views": 587,
    "blocking_ambiguities": 514,
    "conflicts": 0,
    "unknowns": 0,
}
EXPECTED_SUMMARY_COUNTS = {
    "total_surfaces": 1083,
    "explicit_live_authorities": 77,
    "proposals": 52,
    "historical_surfaces": 177,
    "superseded_surfaces": 0,
    "generated_views": 587,
    "implied_authorities": 17,
    "conflicting_authorities": 0,
    "authority_unknown": 0,
    "file_authoritative_candidates": 142,
    "database_authoritative_candidates": 4,
    "duplicate_truth_candidates": 0,
    "staleness_rule_surfaces": 9,
    "data_preservation_rule_surfaces": 13,
    "blocking_ambiguities": 514,
}
EXPECTED_PROVENANCE_RULE_IDS = [
    "GOVERNANCE_INVENTORY_TRANSITIONAL_EVIDENCE_001",
    "GOVERNANCE_VALIDATION_FAIL_CLOSED_001",
]
EXPECTED_ARTIFACT_PATHS = [
    "docs/manual_repository_audit_2026_07_13.md",
    "outputs/governance_inventory/governance_surface_inventory.json",
    "outputs/governance_inventory/governance_authority_relationships.json",
    "outputs/governance_inventory/governance_ambiguity_register.json",
    "outputs/governance_inventory/governance_inventory_summary.json",
]
EXPECTED_AMBIGUITY_RISK_CLASSIFICATION_PATH = "outputs/governance_inventory/governance_ambiguity_risk_classification.json"
EXPECTED_REMEDIATION_QUEUE_PATH = "outputs/governance_inventory/governance_remediation_queue.json"
EXPECTED_REMEDIATION_QUEUE_SUMMARY_PATH = "outputs/governance_inventory/governance_remediation_queue_summary.json"
EXPECTED_REMEDIATION_QUEUE_REVIEW_PATH = "docs/governance/governance_remediation_queue_review.md"
EXPECTED_REMEDIATION_ORDER_RULE_PATH = "governance/core_rules/GOVERNANCE_AMBIGUITY_REMEDIATION_ORDER_001.json"
EXPECTED_REMEDIATION_ORDER_RULE_ID = "GOVERNANCE_AMBIGUITY_REMEDIATION_ORDER_001"
EXPECTED_REMEDIATION_ORDER_RULE_HASH = "4c7354addbfd00e92382db5ea7091e6787004a8036dd64884c73a15ff6a9d18c"
EXPECTED_AMBIGUITY_CLASSIFICATION_LOGICAL_SHA256 = "b8cc2d8bc05c73c9fd10d4f960de261be4cdd806f5af3448f5fe84297165146c"
EXPECTED_REMEDIATION_QUEUE_LOGICAL_SHA256 = "c2c4f16f44f3d61cfd8a85e60146a78c4f3d52edc86039f20753118e83526445"
EXPECTED_REMEDIATION_QUEUE_SUMMARY_LOGICAL_SHA256 = "441e3b8f74e44f12248edbcd722dadd803ea51625d7db0aa822b427fc0daa9fc"
EXPECTED_QUEUE_SOURCE_SNAPSHOT_LOGICAL_SHA256 = "de30368c1b8349a0fdfc83c7a4213c64acc3d90784b5ea5c29e2baa4a27d7ef7"
EXPECTED_AMBIGUITY_RECORD_COUNT = 514
EXPECTED_QUEUE_GROUP_COUNTS = {
    "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS": 21,
    "Q1_VALIDATION_AUTHORITY": 9,
    "Q2_AUTHORITY_LINEAGE": 9,
    "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION": 75,
    "Q4_GENERATED_VIEW_BOUNDARY": 362,
    "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION": 38,
}
EXPECTED_SEVERITY_COUNTS = {
    "CRITICAL": 269,
    "HIGH": 41,
    "MEDIUM": 204,
}
EXPECTED_AMBIGUITY_CLASS_COUNTS = {
    "COMPETING_LIVE_AUTHORITY": 21,
    "VALIDATION_AUTHORITY_UNCLEAR": 9,
    "AUTHORITY_LINEAGE_MISSING": 9,
    "LIVE_VERSUS_PROPOSAL_UNCLEAR": 52,
    "CURRENT_VERSUS_HISTORICAL_UNCLEAR": 23,
    "SOURCE_VERSUS_GENERATED_UNCLEAR": 362,
    "DOCUMENTATION_ONLY": 8,
    "DUPLICATE_IDENTITY_UNCLEAR": 30,
}
EXPECTED_RISK_DIMENSION_COUNTS = {
    "COMPETING_LIVE_AUTHORITY": 21,
    "DUPLICATE_IDENTITY_UNCLEAR": 149,
    "VALIDATION_AUTHORITY_UNCLEAR": 18,
    "WRITE_AUTHORITY_UNCLEAR": 21,
    "AUTHORITY_LINEAGE_MISSING": 36,
    "LIVE_VERSUS_PROPOSAL_UNCLEAR": 52,
    "CURRENT_VERSUS_HISTORICAL_UNCLEAR": 23,
    "SOURCE_VERSUS_GENERATED_UNCLEAR": 362,
    "DOCUMENTATION_ONLY": 8,
}
EXPECTED_RESOLUTION_MODE_COUNTS = {
    "SELECT_CANONICAL_AUTHORITY": 21,
    "PROVE_VALIDATOR_OWNER": 9,
    "ESTABLISH_LINEAGE": 9,
    "CLASSIFY_PROPOSAL": 52,
    "CLASSIFY_HISTORICAL": 23,
    "CLASSIFY_GENERATED_VIEW": 362,
    "DOCUMENT_ONLY": 8,
    "MERGE_IDENTITY_RECORDS": 30,
}
EXPECTED_FULL_PYTEST_COLLECTION_BLOCKER = [
    "typer",
    "rd_moving_boundary_sim_v1",
    "tda_module_v1",
]
EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_ID = "GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001"
EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_PATH = "governance/core_rules/GOVERNANCE_AUTHORITY_SCOPE_PARTITION_001.json"
EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_PARTITION_PATH = (
    "governance/authority_partitions/Q0_AUTHORITY_SCOPE_PARTITION_001.json"
)
EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS = {
    "before": "outputs/governance_inventory/q0_scope_partition_before.json",
    "after": "outputs/governance_inventory/q0_scope_partition_after.json",
    "diff": "outputs/governance_inventory/q0_scope_partition_diff.json",
    "write_owners": "outputs/governance_inventory/q0_exclusive_write_owners.json",
    "validation": "outputs/governance_inventory/q0_validator_authority_partition.json",
    "instruction": "outputs/governance_inventory/q0_instruction_authority_partition.json",
    "queue": "outputs/governance_inventory/q0_scope_partition_queue.json",
    "review": "docs/governance/q0_authority_scope_partition.md",
    "live_access_inventory": "outputs/governance_inventory/q0_live_authority_access_inventory.json",
    "patch": "patches/PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007.json",
}


def load_json(relative_path: str):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def sha256_file(relative_path: str) -> str:
    return hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()


def canonical_sha256(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def expected_artifact_hashes() -> dict[str, str]:
    return {path: sha256_file(path) for path in EXPECTED_ARTIFACT_PATHS}


def deterministic_provenance_id(artifact_path: str, artifact_sha256: str, snapshot_sha256: str) -> str:
    basis = f"{artifact_path}|{artifact_sha256}|{snapshot_sha256}"
    return "GOVINV-PROV-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16].upper()


def live_authority_digest() -> tuple[int, str]:
    inventory = load_json("outputs/governance_inventory/governance_surface_inventory.json")
    live = [record for record in inventory["records"] if record.get("authority_state") == "EXPLICIT_LIVE_AUTHORITY"]
    live = sorted(live, key=lambda record: record.get("surface_id", ""))
    return len(live), canonical_sha256(live)
