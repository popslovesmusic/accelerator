from ._helpers import load_json, sha256_file


def test_patch_018_keeps_patch_002_partial_and_preserves_one_open_q0_gate():
    patch = load_json("patches/PATCH_GOVERNANCE_Q0_PATCH_002_COMPLETION_GATE_FOLLOW_ON_018.json")
    inventory = load_json("outputs/governance_inventory/patch_002_current_completion_gate_inventory.json")
    decision = load_json("outputs/governance_inventory/patch_002_completion_gate_decision.json")
    queue = load_json("outputs/governance_inventory/q0_next_bounded_work_queue_active.json")

    assert patch["patch_id"] == "PATCH_GOVERNANCE_Q0_PATCH_002_COMPLETION_GATE_FOLLOW_ON_018"
    assert patch["patch_002_completion_gate_classification"] == "GATE_REQUIRES_SUBSTANTIVE_RESOLUTION_OF_ALL_ITEMS"
    assert patch["patch_002_state"]["before"] == {"status": "PARTIAL", "authority_effect": "NONE"}
    assert patch["patch_002_state"]["after"] == {"status": "PARTIAL", "authority_effect": "NONE"}
    assert inventory["inventory_accounting"]["currently_active_unresolved_item_count"] in (493, 442, 440, 417, 393, 412, 0)
    assert inventory["inventory_accounting"]["prospectively_closed_item_count"] in (7, 56, 58, 81, 105, 82, 494)
    assert inventory["inventory_accounting"]["retired_obsolete_residue_count"] in (4, 6, 10)
    assert decision["decision"]["q0_open_item_count_before"] == 1
    assert decision["decision"]["q0_open_item_count_after"] == 1
    assert decision["remaining_genuinely_unresolved_inventory_set"]["count"] in (493, 442, 440, 417, 393, 412, 0)
    if decision["remaining_genuinely_unresolved_inventory_set"]["count"] == 0:
        assert decision["remaining_genuinely_unresolved_inventory_set"]["queue_groups"] == {
            "Q1_VALIDATION_AUTHORITY": 0,
            "Q2_AUTHORITY_LINEAGE": 0,
            "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION": 0,
            "Q4_GENERATED_VIEW_BOUNDARY": 0,
            "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION": 0,
        }
    elif decision["remaining_genuinely_unresolved_inventory_set"]["count"] == 412:
        assert decision["remaining_genuinely_unresolved_inventory_set"]["queue_groups"] == {
            "Q1_VALIDATION_AUTHORITY": 0,
            "Q2_AUTHORITY_LINEAGE": 0,
            "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION": 2,
            "Q4_GENERATED_VIEW_BOUNDARY": 367,
            "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION": 43,
        }
    elif decision["remaining_genuinely_unresolved_inventory_set"]["count"] == 393:
        assert decision["remaining_genuinely_unresolved_inventory_set"]["queue_groups"] == {
            "Q1_VALIDATION_AUTHORITY": 6,
            "Q2_AUTHORITY_LINEAGE": 6,
            "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION": 2,
            "Q4_GENERATED_VIEW_BOUNDARY": 362,
            "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION": 38,
        }
    elif decision["remaining_genuinely_unresolved_inventory_set"]["count"] == 417:
        assert decision["remaining_genuinely_unresolved_inventory_set"]["queue_groups"] == {
            "Q1_VALIDATION_AUTHORITY": 8,
            "Q2_AUTHORITY_LINEAGE": 6,
            "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION": 26,
            "Q4_GENERATED_VIEW_BOUNDARY": 362,
            "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION": 38,
        }
    elif decision["remaining_genuinely_unresolved_inventory_set"]["count"] == 442:
        assert decision["remaining_genuinely_unresolved_inventory_set"]["queue_groups"] == {
            "Q1_VALIDATION_AUTHORITY": 8,
            "Q2_AUTHORITY_LINEAGE": 6,
            "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION": 28,
            "Q4_GENERATED_VIEW_BOUNDARY": 362,
            "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION": 38,
        }
    else:
        assert decision["remaining_genuinely_unresolved_inventory_set"]["queue_groups"] == {
            "Q1_VALIDATION_AUTHORITY": 9,
            "Q2_AUTHORITY_LINEAGE": 9,
            "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION": 75,
            "Q4_GENERATED_VIEW_BOUNDARY": 362,
            "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION": 38,
        }
    assert queue["queue_counts"] in ({"before": 1, "after": 1}, {"before": 1, "after": 0})
    if queue["queue_counts"]["after"] == 0:
        assert [entry["work_id"] for entry in queue["queue"]] == []
    else:
        assert [entry["work_id"] for entry in queue["queue"]] == ["Q0-NEXT-005"]
        assert queue["queue"][0]["execution_state"] == "DEFERRED"


def test_patch_018_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/patch_002_current_completion_gate_inventory.json"] == (
        sha256_file("outputs/governance_inventory/patch_002_current_completion_gate_inventory.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/patch_002_completion_gate_decision.json"] == (
        sha256_file("outputs/governance_inventory/patch_002_completion_gate_decision.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q0_next_bounded_work_queue_active.json"] == (
        sha256_file("outputs/governance_inventory/q0_next_bounded_work_queue_active.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q0_PATCH_002_COMPLETION_GATE_FOLLOW_ON_018.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q0_PATCH_002_COMPLETION_GATE_FOLLOW_ON_018.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q0_PATCH_002_COMPLETION_GATE_FOLLOW_ON_018.json"
        ]
        == sha256_file(
            "registry/governance/patches/PATCH_GOVERNANCE_Q0_PATCH_002_COMPLETION_GATE_FOLLOW_ON_018.json"
        ).upper()
    )
