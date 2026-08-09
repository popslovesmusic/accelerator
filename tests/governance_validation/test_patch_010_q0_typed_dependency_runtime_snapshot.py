from ._helpers import load_json, sha256_file


def test_patch_010_records_q0_runtime_snapshot_without_runtime_blockers():
    snapshot = load_json("outputs/governance_inventory/q0_typed_dependency_runtime_snapshot.json")
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_TYPED_DEPENDENCY_RUNTIME_SNAPSHOT_010.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_TYPED_DEPENDENCY_RUNTIME_SNAPSHOT_010"
    assert snapshot["conclusion"]["dependency_chain_blocker_present"] is False
    assert snapshot["conclusion"]["patch_002_preserved_status"] == "PARTIAL"
    assert snapshot["conclusion"]["patch_002_authority_effect"] == "NONE"
    assert snapshot["remaining_edge_summary"]["by_classification"] == {
        "REQUIRES_COMPLETED_PREDECESSOR": 1,
        "REQUIRES_EXISTING_EVIDENCE": 21,
        "REQUIRES_SEMANTIC_RULE": 0,
        "HISTORICAL_LINEAGE_ONLY": 0,
        "UNPROVEN": 0,
    }
    assert snapshot["remaining_edge_summary"]["unsatisfied_edges"] == []
    assert snapshot["remaining_edge_summary"]["runtime_blocking_edges"] == []


def test_patch_010_snapshot_hash_is_registered():
    snapshot = load_json("outputs/governance_inventory/q0_typed_dependency_runtime_snapshot.json")
    patch_009_snapshot = next(
        item for item in snapshot["snapshots"]
        if item["patch_id"] == "PATCH_GOVERNANCE_PATCH_002_TYPED_DEPENDENCY_RUNTIME_009"
    )
    assert patch_009_snapshot["dependency_evaluation"][0] == {
        "patch_id": "PATCH_DB_GOVERNANCE_RUNTIME_004",
        "requirement_type": "REQUIRES_COMPLETED_PREDECESSOR",
        "satisfied": True,
        "dependency_status": "applied",
        "dependency_decision": "defer",
    }

    hash_registry = load_json("registry/governance_hash_registry.json")
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_typed_dependency_runtime_snapshot.json"] == (
        sha256_file("outputs/governance_inventory/q0_typed_dependency_runtime_snapshot.json").upper()
    )
