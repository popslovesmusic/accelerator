from ._helpers import load_json, sha256_file


def test_patch_013_inventory_counts_and_queue_order_are_deterministic():
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_REMAINING_OPEN_WORK_CLASSIFICATION_013.json")
    inventory = load_json("outputs/governance_inventory/q0_remaining_open_work_inventory.json")
    queue = load_json("outputs/governance_inventory/q0_next_bounded_work_queue.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_REMAINING_OPEN_WORK_CLASSIFICATION_013"
    assert inventory["summary_counts"] == {
        "total_remaining_q0_items": 12,
        "blocked_on_global_inventory": 1,
        "ready_for_bounded_resolution": 0,
        "neutralized_by_later_governance": 7,
        "obsolete_residue": 4,
        "genuinely_unresolved_authority_conflicts": 0,
        "validator_department_gated": 0,
        "unproven": 0,
    }

    items = {entry["item_id"]: entry for entry in inventory["items"]}
    assert items["Q0-OPEN-001"]["classification"] == "BLOCKED_ON_GLOBAL_INVENTORY"
    assert items["Q0-OPEN-002"]["classification"] == "NEUTRALIZED_BY_LATER_GOVERNANCE"
    assert items["Q0-OPEN-009"]["classification"] == "OBSOLETE_RESIDUE"
    assert items["Q0-OPEN-010"]["classification"] == "OBSOLETE_RESIDUE"

    assert [entry["work_id"] for entry in queue["queue"]] == [
        "Q0-NEXT-001",
        "Q0-NEXT-002",
        "Q0-NEXT-003",
        "Q0-NEXT-004",
        "Q0-NEXT-005",
    ]
    assert queue["summary"] == {
        "queue_size": 5,
        "executable_items": 4,
        "deferred_items": 1,
        "ready_for_bounded_resolution": 0,
        "neutralized_by_later_governance": 2,
        "obsolete_residue": 2,
        "blocked_on_global_inventory": 1,
    }


def test_patch_013_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q0_remaining_open_work_inventory.json"] == (
        sha256_file("outputs/governance_inventory/q0_remaining_open_work_inventory.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_next_bounded_work_queue.json"] == (
        sha256_file("outputs/governance_inventory/q0_next_bounded_work_queue.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q0_REMAINING_OPEN_WORK_CLASSIFICATION_013.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q0_REMAINING_OPEN_WORK_CLASSIFICATION_013.json").upper()
    )
    assert (
        hash_registry["hashes"]["registry/governance/patches/PATCH_GOVERNANCE_Q0_REMAINING_OPEN_WORK_CLASSIFICATION_013.json"]
        == sha256_file("registry/governance/patches/PATCH_GOVERNANCE_Q0_REMAINING_OPEN_WORK_CLASSIFICATION_013.json").upper()
    )
