from ._helpers import (
    EXPECTED_FULL_PYTEST_COLLECTION_BLOCKER,
    EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS,
    EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_PARTITION_PATH,
    EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_ID,
    EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_PATH,
    load_json,
    sha256_file,
)


def test_q0_authority_scope_partition_completion_record_captures_registered_artifacts():
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007"
    assert patch["title"] == "Q0 Authority Scope Partition and Enforcement"
    assert patch["status"] == "PARTIAL"
    assert patch["mode"] == "additive"
    assert patch["depends_on"] == [
        "PATCH_GOVERNANCE_GLOBAL_INVENTORY_002",
        "PATCH_GOVERNANCE_INVENTORY_PROVENANCE_AND_ADDITIVE_AUTHORITY_004",
        "PATCH_GOVERNANCE_AMBIGUITY_RISK_CLASSIFICATION_AND_REMEDIATION_QUEUE_005",
        "PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006",
    ]
    assert patch["live_semantic_dependencies"]["classification"] == "SEMANTICS_SURVIVE_ELSEWHERE"
    assert patch["live_semantic_dependencies"]["historical_reference"]["patch_id"] == (
        "PATCH_GOVERNANCE_STATUS_SEMANTICS_AND_BLOCKING_REDUCTION_003"
    )
    assert "replaces_blocked_attempt" not in patch

    assert patch["core_rule"] == {
        "rule_id": EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_ID,
        "path": EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_PATH,
        "hash": sha256_file(EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_PATH),
        "status": "LIVE",
        "authority_effect": "LIVE_SCOPE_CONSTRAINT",
    }

    assert patch["selection_summary"]["cluster_id"] == "Q0-CLUSTER-D3129CA0B3C98DED"
    assert patch["selection_summary"]["resolved_record_count"] == 10
    assert patch["selection_summary"]["resolved_question_count"] == 12
    assert patch["selection_summary"]["remaining_blocking_ambiguities"] == 504
    assert patch["selection_summary"]["completion_mode"] == "SEPARATE_NON_OVERLAPPING_SCOPES"

    assert patch["artifact_bundle"]["core_rule"]["hash"] == sha256_file(EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_PATH)
    assert patch["artifact_bundle"]["partition"]["hash"] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_PARTITION_PATH
    )
    assert patch["artifact_bundle"]["before_state"]["hash"] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["before"]
    )
    assert patch["artifact_bundle"]["after_state"]["hash"] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["after"]
    )
    assert patch["artifact_bundle"]["diff"]["hash"] == sha256_file(EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["diff"])
    assert patch["artifact_bundle"]["write_owners"]["hash"] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["write_owners"]
    )
    assert patch["artifact_bundle"]["validation"]["hash"] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["validation"]
    )
    assert patch["artifact_bundle"]["instruction"]["hash"] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["instruction"]
    )
    assert patch["artifact_bundle"]["queue"]["hash"] == sha256_file(EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["queue"])
    assert patch["artifact_bundle"]["review"]["hash"] == sha256_file(EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["review"])
    assert patch["artifact_bundle"]["live_authority_access_inventory"]["hash"] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["live_access_inventory"]
    )

    assert patch["validation_results"]["focused_governance_validation"]["status"] == "pass"
    assert patch["validation_results"]["focused_governance_validation"]["failed"] == 0
    assert patch["validation_results"]["governance_only_validator"]["status"] == "pass"
    assert patch["validation_results"]["full_pytest_collection"]["status"] == "blocked"
    assert patch["validation_results"]["full_pytest_collection"]["missing_modules"] == EXPECTED_FULL_PYTEST_COLLECTION_BLOCKER

    ledger = load_json("registry/governance_change_ledger.json")
    patch_entry = next(entry for entry in ledger["entries"] if entry["patch_id"] == patch["patch_id"])
    assert patch_entry["diff_report"] == EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["patch"]

    hash_registry = load_json("registry/governance_hash_registry.json")
    assert hash_registry["hashes"][EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_PATH] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_RULE_PATH
    ).upper()
    assert hash_registry["hashes"][EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_PARTITION_PATH] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_PARTITION_PATH
    ).upper()
    assert hash_registry["hashes"][EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["queue"]] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["queue"]
    ).upper()
    assert hash_registry["hashes"][EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["live_access_inventory"]] == sha256_file(
        EXPECTED_Q0_AUTHORITY_SCOPE_PARTITION_OUTPUTS["live_access_inventory"]
    ).upper()

    assert patch["unrelated_changes_preserved"] is True
