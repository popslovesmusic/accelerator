from ._helpers import load_json, sha256_file


def test_patch_014_closes_only_db_runtime_boundary_items():
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_DB_RUNTIME_BOUNDARY_PROSPECTIVE_CLOSURE_014.json")
    inventory = load_json("outputs/governance_inventory/q0_db_runtime_boundary_closure_inventory.json")
    queue = load_json("outputs/governance_inventory/q0_next_bounded_work_queue_active.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_DB_RUNTIME_BOUNDARY_PROSPECTIVE_CLOSURE_014"
    assert patch["selected_item_ids"] == [
        "Q0-OPEN-002",
        "Q0-OPEN-003",
        "Q0-OPEN-004",
        "Q0-OPEN-005",
    ]
    assert patch["prospectively_closed_item_ids"] == patch["selected_item_ids"]
    assert inventory["completion_assertions"] == {
        "historical_ambiguity_records_rewritten": 0,
        "patch_002_status_changed": False,
        "out_of_scope_items_changed": 0,
        "full_project_validation_run": False,
        "closed_item_count": 4,
        "remaining_q0_item_count": 8,
    }

    assert [entry["closure_decision"] for entry in inventory["selected_items"]] == [
        "PROSPECTIVELY_CLOSED",
        "PROSPECTIVELY_CLOSED",
        "PROSPECTIVELY_CLOSED",
        "PROSPECTIVELY_CLOSED",
    ]
    assert queue["queue_counts"] == {"before": 5, "after": 4}
    assert queue["closed_work"]["work_id"] == "Q0-NEXT-001"
    assert [entry["work_id"] for entry in queue["queue"]] == [
        "Q0-NEXT-002",
        "Q0-NEXT-003",
        "Q0-NEXT-004",
        "Q0-NEXT-005",
    ]


def test_patch_014_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q0_db_runtime_boundary_closure_inventory.json"] == (
        sha256_file("outputs/governance_inventory/q0_db_runtime_boundary_closure_inventory.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_next_bounded_work_queue_active.json"] == (
        sha256_file("outputs/governance_inventory/q0_next_bounded_work_queue_active.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q0_DB_RUNTIME_BOUNDARY_PROSPECTIVE_CLOSURE_014.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q0_DB_RUNTIME_BOUNDARY_PROSPECTIVE_CLOSURE_014.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q0_DB_RUNTIME_BOUNDARY_PROSPECTIVE_CLOSURE_014.json"
        ]
        == sha256_file("registry/governance/patches/PATCH_GOVERNANCE_Q0_DB_RUNTIME_BOUNDARY_PROSPECTIVE_CLOSURE_014.json").upper()
    )
