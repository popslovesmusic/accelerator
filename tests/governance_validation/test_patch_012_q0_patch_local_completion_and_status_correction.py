from ._helpers import load_json, sha256_file


def test_patch_012_records_forward_completion_and_status_correction():
    evidence = load_json("outputs/governance_inventory/q0_patch_local_completion_and_status_correction_evidence.json")
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_PATCH_LOCAL_COMPLETION_AND_STATUS_CORRECTION_012.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_PATCH_LOCAL_COMPLETION_AND_STATUS_CORRECTION_012"
    assert evidence["completion_assertions"] == {
        "patch_002": "REMAINS_PARTIAL",
        "patch_007": "FORWARD_COMPLETION_RECORDED",
        "patch_008": "STALE_BLOCKER_METADATA_PROSPECTIVELY_CORRECTED",
        "patch_009": "FORWARD_COMPLETION_RECORDED",
        "patch_010": "FORWARD_COMPLETION_RECORDED",
        "full_project_validation": "STILL_SUSPENDED",
    }

    records = {entry["patch_id"]: entry for entry in evidence["patches"]}
    assert records["PATCH_GOVERNANCE_GLOBAL_INVENTORY_002"]["result"] == "TRANSITIONAL_PARTIAL"
    assert records["PATCH_GOVERNANCE_Q0_AUTHORITY_SCOPE_PARTITION_007"]["result"] == "PATCH_LOCAL_COMPLETE"
    assert records["PATCH_GOVERNANCE_MISSING_DEPENDENCY_003_CHAIN_REPAIR_008"]["result"] == (
        "BLOCKER_METADATA_SUPERSEDED_BY_LATER_GOVERNED_EVIDENCE"
    )
    assert records["PATCH_GOVERNANCE_PATCH_002_TYPED_DEPENDENCY_RUNTIME_009"]["result"] == "PATCH_LOCAL_COMPLETE"
    assert records["PATCH_GOVERNANCE_Q0_TYPED_DEPENDENCY_RUNTIME_SNAPSHOT_010"]["result"] == "PATCH_LOCAL_COMPLETE"
    assert evidence["governance_semantics"]["patch_local_complete_does_not_imply_program_complete"] is True
    assert evidence["governance_semantics"]["patch_local_complete_does_not_imply_full_project_validated"] is True


def test_patch_012_evidence_hash_is_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_patch_local_completion_and_status_correction_evidence.json"] == (
        sha256_file("outputs/governance_inventory/q0_patch_local_completion_and_status_correction_evidence.json").upper()
    )
