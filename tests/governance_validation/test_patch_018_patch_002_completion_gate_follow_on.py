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
    assert inventory["inventory_accounting"] == {
        "original_inventory_item_count": 514,
        "q0_original_blocking_ambiguity_count": 21,
        "q0_selected_cluster_count": 10,
        "q0_excluded_neighbor_count": 11,
        "currently_active_unresolved_item_count": 493,
        "prospectively_closed_item_count": 7,
        "retired_obsolete_residue_count": 4,
        "neutralized_but_not_formally_closed_count": 0,
        "items_outside_q0_scope": 493,
        "items_still_unclassified": 493,
        "items_blocked_on_external_gate": 0,
        "accounting_rule": "Current disposition accounting credits all 21 original Q0 ambiguity items with a governed Q0-layer disposition, but no later governed artifact reclassifies the remaining non-Q0 493 ambiguity records as completion-gate-satisfying."
    }
    assert decision["decision"]["q0_open_item_count_before"] == 1
    assert decision["decision"]["q0_open_item_count_after"] == 1
    assert decision["remaining_genuinely_unresolved_inventory_set"]["count"] == 493
    assert decision["remaining_genuinely_unresolved_inventory_set"]["queue_groups"] == {
        "Q1_VALIDATION_AUTHORITY": 9,
        "Q2_AUTHORITY_LINEAGE": 9,
        "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION": 75,
        "Q4_GENERATED_VIEW_BOUNDARY": 362,
        "Q5_DUPLICATE_IDENTITY_AND_DOCUMENTATION": 38,
    }
    assert queue["queue_counts"] == {"before": 1, "after": 1}
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
