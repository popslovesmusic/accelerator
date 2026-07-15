from ._helpers import load_json, sha256_file


def test_patch_066_refreshes_remaining_q1_state_without_resolving_new_items():
    patch = load_json("patches/PATCH_GOVERNANCE_Q1_REMAINING_VALIDATION_AUTHORITY_CLUSTER_SELECTION_066.json")
    refresh = load_json("outputs/governance_inventory/q1_remaining_validation_authority_state_refresh.json")
    components = load_json("outputs/governance_inventory/q1_remaining_conflict_components.json")
    selection = load_json("outputs/governance_inventory/q1_next_bounded_cluster_selection.json")
    packet = load_json("outputs/governance_inventory/q1_next_validation_authority_resolution_packet.json")

    assert patch["depends_on"] == ["PATCH_GOVERNANCE_Q1_VALIDATION_INVOCATION_AUTHORITY_BOUNDARY_RESOLUTION_065"]
    assert patch["previous_q1_resolution_patch_verified"] is True
    assert patch["remaining_q1_item_ids"] == [
        "Q1-VAL-001",
        "Q1-VAL-004",
        "Q1-VAL-005",
        "Q1-VAL-006",
        "Q1-VAL-007",
        "Q1-VAL-008",
        "Q1-VAL-009",
    ]
    assert patch["completion_assertions"] == {
        "previous_q1_resolution_verified": True,
        "remaining_q1_items_before_analysis": 7,
        "q1_items_resolved_by_this_patch": 0,
        "selected_next_cluster_item_count": 1,
        "selected_next_cluster_item_ids": ["Q1-VAL-008"],
        "remaining_items_classified_neutralized": 1,
        "remaining_items_classified_obsolete_residue": 2,
        "remaining_items_classified_outside_q1_scope": 3,
        "validation_authority_changed": False,
        "full_project_validation_run": False,
    }

    assert refresh["previous_q1_resolution_patch_verified"] is True
    assert refresh["remaining_q1_item_ids"] == patch["remaining_q1_item_ids"]
    assert refresh["state_counts"] == {
        "LIVE_UNRESOLVED_Q1_AUTHORITY_AMBIGUITY": 1,
        "NEUTRALIZED_BY_EXISTING_GOVERNANCE": 1,
        "OBSOLETE_TEST_OR_CONTEXT_RESIDUE": 2,
        "OUTSIDE_Q1_SCOPE": 3,
        "UNPROVEN": 0,
    }
    states = {item["stable_q1_item_id"]: item["current_state"] for item in refresh["items"]}
    assert states == {
        "Q1-VAL-001": "OUTSIDE_Q1_SCOPE",
        "Q1-VAL-004": "NEUTRALIZED_BY_EXISTING_GOVERNANCE",
        "Q1-VAL-005": "OUTSIDE_Q1_SCOPE",
        "Q1-VAL-006": "OUTSIDE_Q1_SCOPE",
        "Q1-VAL-007": "OBSOLETE_TEST_OR_CONTEXT_RESIDUE",
        "Q1-VAL-008": "LIVE_UNRESOLVED_Q1_AUTHORITY_AMBIGUITY",
        "Q1-VAL-009": "OBSOLETE_TEST_OR_CONTEXT_RESIDUE",
    }

    assert components["component_count"] == 5
    component_map = {component["component_id"]: component["item_ids"] for component in components["components"]}
    assert component_map["Q1-REM-COMP-005"] == ["Q1-VAL-007", "Q1-VAL-008", "Q1-VAL-009"]

    assert selection["selected_component_id"] == "Q1-REM-COMP-005"
    assert selection["selected_cluster_item_ids"] == ["Q1-VAL-008"]
    assert selection["selected_cluster_type"] == "SUPPORTING_VALIDATOR_SCOPE"
    assert selection["current_state_counts"] == {
        "live_unresolved": 1,
        "neutralized": 1,
        "obsolete_residue": 2,
        "outside_q1_scope": 3,
    }

    assert packet["selected_q1_item_ids"] == ["Q1-VAL-008"]
    assert packet["selected_global_ambiguity_ids"] == ["AMB-GOV-SURF-1032"]
    assert packet["candidate_resolution_modes"] == [
        "BOUND_SUPPORTING_VALIDATOR_SCOPE",
        "PROVE_EXISTING_NON_TERMINAL_ROLE",
        "DEFER_PENDING_VALIDATOR_DEPARTMENT_COMPLETION",
    ]
    assert [item["item_id"] for item in packet["non_selected_related_items"]] == ["Q1-VAL-007", "Q1-VAL-009"]


def test_patch_066_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q1_remaining_validation_authority_state_refresh.json"] == (
        sha256_file("outputs/governance_inventory/q1_remaining_validation_authority_state_refresh.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_remaining_conflict_components.json"] == (
        sha256_file("outputs/governance_inventory/q1_remaining_conflict_components.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_next_bounded_cluster_selection.json"] == (
        sha256_file("outputs/governance_inventory/q1_next_bounded_cluster_selection.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_next_validation_authority_resolution_packet.json"] == (
        sha256_file("outputs/governance_inventory/q1_next_validation_authority_resolution_packet.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q1_REMAINING_VALIDATION_AUTHORITY_CLUSTER_SELECTION_066.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q1_REMAINING_VALIDATION_AUTHORITY_CLUSTER_SELECTION_066.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_REMAINING_VALIDATION_AUTHORITY_CLUSTER_SELECTION_066.json"
        ]
        == sha256_file(
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_REMAINING_VALIDATION_AUTHORITY_CLUSTER_SELECTION_066.json"
        ).upper()
    )
