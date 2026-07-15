from ._helpers import load_json, sha256_file


def test_patch_011_classifies_q0_partial_status_intent_without_mutation():
    inventory = load_json("outputs/governance_inventory/q0_partial_status_intent_inventory.json")
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_PARTIAL_STATUS_INTENT_CLASSIFICATION_011.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_PARTIAL_STATUS_INTENT_CLASSIFICATION_011"
    assert inventory["summary"]["classification_counts"] == {
        "INTENTIONALLY_TRANSITIONAL": 1,
        "IMPLEMENTED_BUT_COMPLETION_RECORD_MISSING": 3,
        "FORWARD_COMPLETION_PATCH_REQUIRED": 0,
        "BLOCKED_BY_EXTERNAL_PROGRAM_GATE": 0,
        "STATUS_METADATA_STALE": 1,
        "UNPROVEN": 0,
    }

    records = {entry["patch_id"]: entry for entry in inventory["patches"]}
    assert records["PATCH_GOVERNANCE_GLOBAL_INVENTORY_002"]["classification"] == "INTENTIONALLY_TRANSITIONAL"
    assert records["PATCH_GOVERNANCE_GLOBAL_INVENTORY_002"]["recommended_status_action"] == "KEEP_PARTIAL"
    assert records["PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007"]["classification"] == (
        "IMPLEMENTED_BUT_COMPLETION_RECORD_MISSING"
    )
    assert records["PATCH_GOVERNANCE_MISSING_DEPENDENCY_003_CHAIN_REPAIR_008"]["classification"] == (
        "STATUS_METADATA_STALE"
    )
    assert records["PATCH_GOVERNANCE_PATCH_002_TYPED_DEPENDENCY_RUNTIME_009"]["classification"] == (
        "IMPLEMENTED_BUT_COMPLETION_RECORD_MISSING"
    )
    assert records["PATCH_GOVERNANCE_Q0_TYPED_DEPENDENCY_RUNTIME_SNAPSHOT_010"]["classification"] == (
        "IMPLEMENTED_BUT_COMPLETION_RECORD_MISSING"
    )


def test_patch_011_inventory_hash_is_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_partial_status_intent_inventory.json"] == (
        sha256_file("outputs/governance_inventory/q0_partial_status_intent_inventory.json").upper()
    )
