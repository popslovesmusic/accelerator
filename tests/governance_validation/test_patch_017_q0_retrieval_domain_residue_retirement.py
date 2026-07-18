from ._helpers import load_json, sha256_file


def test_patch_017_retires_only_retrieval_domain_residue_item():
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_RETRIEVAL_DOMAIN_RESIDUE_RETIREMENT_017.json")
    inventory = load_json("outputs/governance_inventory/q0_retrieval_domain_residue_retirement_inventory.json")
    queue = load_json("outputs/governance_inventory/q0_next_bounded_work_queue_active.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_RETRIEVAL_DOMAIN_RESIDUE_RETIREMENT_017"
    assert patch["selected_item_ids"] == ["Q0-OPEN-010"]
    assert patch["retired_item_ids"] == ["Q0-OPEN-010"]
    assert inventory["completion_assertions"] == {
        "historical_records_rewritten": 0,
        "patch_002_status_changed": False,
        "live_authority_assignments_changed": 0,
        "full_project_validation_run": False,
        "selected_item_count": 1,
        "retired_item_count": 1,
        "remaining_active_queue_count": 1,
    }

    assert [entry["retirement_decision"] for entry in inventory["selected_items"]] == [
        "RETIRE_AS_OBSOLETE_RESIDUE",
    ]
    if "closed_work" in queue and queue["closed_work"].get("work_id") == "Q0-NEXT-004":
        assert queue["queue_counts"] == {"before": 2, "after": 1}
        assert queue["closed_work"]["work_id"] == "Q0-NEXT-004"
        assert [entry["work_id"] for entry in queue["queue"]] == [
            "Q0-NEXT-005",
        ]


def test_patch_017_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q0_retrieval_domain_residue_retirement_inventory.json"] == (
        sha256_file("outputs/governance_inventory/q0_retrieval_domain_residue_retirement_inventory.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_next_bounded_work_queue_active.json"] == (
        sha256_file("outputs/governance_inventory/q0_next_bounded_work_queue_active.json").upper()
    )
    assert (
        hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q0_RETRIEVAL_DOMAIN_RESIDUE_RETIREMENT_017.json"]
        == sha256_file("patches/PATCH_GOVERNANCE_Q0_RETRIEVAL_DOMAIN_RESIDUE_RETIREMENT_017.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q0_RETRIEVAL_DOMAIN_RESIDUE_RETIREMENT_017.json"
        ]
        == sha256_file(
            "registry/governance/patches/PATCH_GOVERNANCE_Q0_RETRIEVAL_DOMAIN_RESIDUE_RETIREMENT_017.json"
        ).upper()
    )
