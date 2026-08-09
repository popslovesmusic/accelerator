from ._helpers import load_json, sha256_file


def test_patch_015_closes_only_live_command_boundary_items():
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_LIVE_COMMAND_BOUNDARY_PROSPECTIVE_CLOSURE_015.json")
    inventory = load_json("outputs/governance_inventory/q0_live_command_boundary_closure_inventory.json")
    queue = load_json("outputs/governance_inventory/q0_next_bounded_work_queue_active.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_LIVE_COMMAND_BOUNDARY_PROSPECTIVE_CLOSURE_015"
    assert patch["selected_item_ids"] == [
        "Q0-OPEN-006",
        "Q0-OPEN-007",
        "Q0-OPEN-008",
    ]
    assert patch["prospectively_closed_item_ids"] == patch["selected_item_ids"]
    assert inventory["completion_assertions"] == {
        "historical_ambiguity_records_rewritten": 0,
        "patch_002_status_changed": False,
        "out_of_scope_items_changed": 0,
        "full_project_validation_run": False,
        "selected_item_count": 3,
        "prospectively_closed_item_count": 3,
        "remaining_q0_item_count": 5,
    }

    surface_map = {entry["path"]: entry["classification"] for entry in inventory["live_command_surfaces"]}
    assert surface_map["scripts/global_validate.py"] == "CANONICAL_ENTRY_POINT"
    assert surface_map["scripts/validate_governance_surface.py"] == "ROLE_AWARE_SUPPORTING_COMMAND"
    assert surface_map["scripts/query_governance.py"] == "ROLE_AWARE_SUPPORTING_COMMAND"

    assert [entry["closure_decision"] for entry in inventory["selected_items"]] == [
        "PROSPECTIVELY_CLOSED",
        "PROSPECTIVELY_CLOSED",
        "PROSPECTIVELY_CLOSED",
    ]
    if "closed_work" in queue and queue["closed_work"].get("work_id") == "Q0-NEXT-002":
        assert queue["queue_counts"] == {"before": 4, "after": 3}
        assert queue["closed_work"]["work_id"] == "Q0-NEXT-002"
        assert [entry["work_id"] for entry in queue["queue"]] == [
            "Q0-NEXT-003",
            "Q0-NEXT-004",
            "Q0-NEXT-005",
        ]


def test_patch_015_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q0_live_command_boundary_closure_inventory.json"] == (
        sha256_file("outputs/governance_inventory/q0_live_command_boundary_closure_inventory.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_next_bounded_work_queue_active.json"] == (
        sha256_file("outputs/governance_inventory/q0_next_bounded_work_queue_active.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q0_LIVE_COMMAND_BOUNDARY_PROSPECTIVE_CLOSURE_015.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q0_LIVE_COMMAND_BOUNDARY_PROSPECTIVE_CLOSURE_015.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q0_LIVE_COMMAND_BOUNDARY_PROSPECTIVE_CLOSURE_015.json"
        ]
        == sha256_file(
            "registry/governance/patches/PATCH_GOVERNANCE_Q0_LIVE_COMMAND_BOUNDARY_PROSPECTIVE_CLOSURE_015.json"
        ).upper()
    )
