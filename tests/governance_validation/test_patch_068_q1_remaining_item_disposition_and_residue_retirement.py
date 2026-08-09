from ._helpers import load_json, sha256_file


def test_patch_068_exhausts_local_q1_queue_without_resolving_reclassified_items():
    patch = load_json("patches/PATCH_GOVERNANCE_Q1_REMAINING_ITEM_DISPOSITION_AND_RESIDUE_RETIREMENT_068.json")
    disposition = load_json("outputs/governance_inventory/q1_remaining_item_disposition.json")
    queue = load_json("outputs/governance_inventory/q1_remaining_item_disposition_active_queue.json")
    global_updates = load_json("outputs/governance_inventory/q1_remaining_item_disposition_global_updates.json")

    assert patch["depends_on"] == ["PATCH_GOVERNANCE_Q1_GOVERNED_CONTEXT_CAPSULE_SUPPORTING_VALIDATOR_SCOPE_RESOLUTION_067"]
    assert patch["prospectively_closed_item_ids"] == ["Q1-VAL-004"]
    assert patch["retired_residue_item_ids"] == ["Q1-VAL-007", "Q1-VAL-009"]
    assert patch["reclassified_item_ids"] == ["Q1-VAL-001", "Q1-VAL-005", "Q1-VAL-006"]
    assert patch["destination_family_per_reclassified_item"] == {
        "Q1-VAL-001": "UNASSIGNED_PENDING_CLASSIFICATION",
        "Q1-VAL-005": "UNASSIGNED_PENDING_CLASSIFICATION",
        "Q1-VAL-006": "UNASSIGNED_PENDING_CLASSIFICATION",
    }
    assert patch["counts"] == {
        "q1_count_before": 6,
        "q1_count_after": 0,
        "global_blocking_ambiguity_count_before": 490,
        "global_blocking_ambiguity_count_after": 487,
    }

    assert disposition["q1_count_before"] == 6
    assert disposition["q1_count_after"] == 0
    assert disposition["q1_family_state_after"] == "LOCAL_QUEUE_EXHAUSTED"
    assert disposition["summary"] == {
        "prospectively_closed_item_ids": ["Q1-VAL-004"],
        "retired_residue_item_ids": ["Q1-VAL-007", "Q1-VAL-009"],
        "reclassified_item_ids": ["Q1-VAL-001", "Q1-VAL-005", "Q1-VAL-006"],
        "destination_family_per_reclassified_item": {
            "Q1-VAL-001": "UNASSIGNED_PENDING_CLASSIFICATION",
            "Q1-VAL-005": "UNASSIGNED_PENDING_CLASSIFICATION",
            "Q1-VAL-006": "UNASSIGNED_PENDING_CLASSIFICATION",
        },
    }

    items = {item["q1_item_id"]: item for item in disposition["items"]}
    assert items["Q1-VAL-004"]["global_resolution_status"] == "PROSPECTIVELY_CLOSED"
    assert items["Q1-VAL-007"]["global_resolution_status"] == "RETIRED_AS_OBSOLETE_RESIDUE"
    assert items["Q1-VAL-009"]["global_resolution_status"] == "RETIRED_AS_OBSOLETE_RESIDUE"
    assert items["Q1-VAL-001"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q1"
    assert items["Q1-VAL-005"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q1"
    assert items["Q1-VAL-006"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q1"

    assert queue["queue_counts"] == {"before": 6, "after": 0}
    assert queue["queue"] == []
    assert queue["preservation_assertions"]["reclassified_items_marked_globally_resolved"] is False

    assert global_updates["one_to_one_mapping_verified"] is True
    assert global_updates["count_delta"] == {
        "global_blocking_ambiguity_count_before": 490,
        "resolved_or_retired_in_this_patch": 3,
        "global_blocking_ambiguity_count_after": 487,
        "q1_group_count_before": 6,
        "q1_group_count_after": 0,
    }
    assert sum(1 for update in global_updates["updates"] if update["counts_toward_global_blocking_delta"]) == 3


def test_patch_068_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q1_remaining_item_disposition.json"] == (
        sha256_file("outputs/governance_inventory/q1_remaining_item_disposition.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_remaining_item_disposition_active_queue.json"] == (
        sha256_file("outputs/governance_inventory/q1_remaining_item_disposition_active_queue.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_remaining_item_disposition_global_updates.json"] == (
        sha256_file("outputs/governance_inventory/q1_remaining_item_disposition_global_updates.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q1_REMAINING_ITEM_DISPOSITION_AND_RESIDUE_RETIREMENT_068.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q1_REMAINING_ITEM_DISPOSITION_AND_RESIDUE_RETIREMENT_068.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_REMAINING_ITEM_DISPOSITION_AND_RESIDUE_RETIREMENT_068.json"
        ]
        == sha256_file(
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_REMAINING_ITEM_DISPOSITION_AND_RESIDUE_RETIREMENT_068.json"
        ).upper()
    )
