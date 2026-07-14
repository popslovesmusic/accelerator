from ._helpers import load_json, sha256_file


def test_patch_008_repairs_missing_patch_003_dependency_without_fabrication():
    inventory = load_json("outputs/governance_inventory/fail_closed_semantic_authority_inventory.json")
    patch = load_json("patches/PATCH_GOVERNANCE_MISSING_DEPENDENCY_003_CHAIN_REPAIR_008.json")

    assert inventory["classification"] == "SEMANTICS_SURVIVE_ELSEWHERE"
    assert inventory["historical_reference"] == {
        "patch_id": "PATCH_GOVERNANCE_STATUS_SEMANTICS_AND_BLOCKING_REDUCTION_003",
        "git_history_status": "NO_MATCHING_COMMITTED_HISTORY_FOUND",
        "canonical_artifact_found": False,
        "live_dependency_allowed": False,
        "interpretation": "Absent historical dependency reference; not recoverable as canonical artifact.",
    }
    assert [record["semantic_rule_id"] for record in inventory["surviving_semantic_authorities"][:3]] == [
        "GOVERNANCE_VALIDATION_FAIL_CLOSED_001",
        "GOVERNANCE_VALIDATION_FAIL_CLOSED_001",
        "GOVERNANCE_VALIDATION_FAIL_CLOSED_001",
    ]

    assert patch["patch_id"] == "PATCH_GOVERNANCE_MISSING_DEPENDENCY_003_CHAIN_REPAIR_008"
    assert patch["classification_result"] == "SEMANTICS_SURVIVE_ELSEWHERE"
    assert patch["repair_outcome"] == "HISTORICAL_REFERENCE_UNMATERIALIZED_LIVE_DEPENDENCY_REPAIRED"
    assert patch["historical_reference"]["recreated"] is False
    assert patch["updated_artifacts"][0] == "outputs/governance_inventory/fail_closed_semantic_authority_inventory.json"

    for rel in [
        "patches/PATCH_GOVERNANCE_INVENTORY_PROVENANCE_AND_ADDITIVE_AUTHORITY_004.json",
        "patches/PATCH_GOVERNANCE_AMBIGUITY_RISK_CLASSIFICATION_AND_REMEDIATION_QUEUE_005.json",
        "patches/PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006.json",
        "patches/PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007.json",
    ]:
        record = load_json(rel)
        assert "PATCH_GOVERNANCE_STATUS_SEMANTICS_AND_BLOCKING_REDUCTION_003" not in record["depends_on"]
        assert record["live_semantic_dependencies"]["classification"] == "SEMANTICS_SURVIVE_ELSEWHERE"
        assert record["live_semantic_dependencies"]["historical_reference"]["status"] == (
            "UNMATERIALIZED_HISTORICAL_REFERENCE"
        )

    canonical_q0 = load_json("registry/governance/patches/PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007.json")
    assert "PATCH_GOVERNANCE_STATUS_SEMANTICS_AND_BLOCKING_REDUCTION_003" not in canonical_q0["depends_on"]
    assert canonical_q0["live_semantic_dependencies"]["classification"] == "SEMANTICS_SURVIVE_ELSEWHERE"

    hash_registry = load_json("registry/governance_hash_registry.json")
    assert hash_registry["hashes"]["outputs/governance_inventory/fail_closed_semantic_authority_inventory.json"] == (
        sha256_file("outputs/governance_inventory/fail_closed_semantic_authority_inventory.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_MISSING_DEPENDENCY_003_CHAIN_REPAIR_008.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_MISSING_DEPENDENCY_003_CHAIN_REPAIR_008.json").upper()
    )
