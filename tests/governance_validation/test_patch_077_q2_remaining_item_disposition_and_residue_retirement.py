from ._helpers import load_json


def test_patch_077_disposes_of_nominal_q2_queue_without_resolving_reclassified_items():
    disposition = load_json("outputs/governance_inventory/q2_remaining_item_disposition_077.json")
    queue = load_json("outputs/governance_inventory/q2_remaining_item_disposition_active_queue_077.json")
    global_updates = load_json("outputs/governance_inventory/q2_remaining_item_disposition_global_updates_077.json")

    assert disposition["q2_count_before"] == 9
    assert disposition["q2_count_after"] == 0
    assert disposition["q2_family_state_after"] == "LOCAL_QUEUE_EXHAUSTED"
    assert disposition["global_blocking_ambiguity_count_before"] == 487
    assert disposition["global_blocking_ambiguity_count_after"] == 484

    assert disposition["executive_disposition"] == {
        "prospectively_closed_item_ids": ["AMB-GOV-SURF-0666"],
        "retired_residue_item_ids": ["AMB-GOV-SURF-0952", "AMB-GOV-SURF-0953"],
        "reclassified_to_q3_item_ids": ["AMB-GOV-SURF-0875"],
        "reclassified_to_q4_item_ids": [
            "AMB-GOV-SURF-0667",
            "AMB-GOV-SURF-0668",
            "AMB-GOV-SURF-0672",
            "AMB-GOV-SURF-0678",
            "AMB-GOV-SURF-0967",
        ],
    }

    items = {item["global_ambiguity_id"]: item for item in disposition["item_by_item_evidence"]}
    assert items["AMB-GOV-SURF-0666"]["global_resolution_status"] == "PROSPECTIVELY_CLOSED"
    assert items["AMB-GOV-SURF-0952"]["global_resolution_status"] == "RETIRED_AS_OBSOLETE_RESIDUE"
    assert items["AMB-GOV-SURF-0953"]["global_resolution_status"] == "RETIRED_AS_OBSOLETE_RESIDUE"
    assert items["AMB-GOV-SURF-0875"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q2"
    assert items["AMB-GOV-SURF-0667"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q2"
    assert items["AMB-GOV-SURF-0668"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q2"
    assert items["AMB-GOV-SURF-0672"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q2"
    assert items["AMB-GOV-SURF-0678"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q2"
    assert items["AMB-GOV-SURF-0967"]["global_resolution_status"] == "UNRESOLVED_RECLASSIFIED_OUT_OF_Q2"

    closure = disposition["supersession_closure_proof"]
    assert closure["global_ambiguity_id"] == "AMB-GOV-SURF-0666"
    assert closure["competing_live_authority_remaining"] is False
    assert closure["runtime_lookup_returns_superseded_surface_as_live"] is False
    assert closure["closure_decision"] == "PROSPECTIVELY_CLOSE"

    residue = {item["global_ambiguity_id"]: item for item in disposition["obsolete_residue_retirement_proof"]["items"]}
    assert residue["AMB-GOV-SURF-0952"]["participates_in_live_control_plane"] is False
    assert residue["AMB-GOV-SURF-0953"]["participates_in_live_control_plane"] is False
    assert residue["AMB-GOV-SURF-0952"]["retirement_decision"] == "RETIRE_AS_OBSOLETE_RESIDUE"
    assert residue["AMB-GOV-SURF-0953"]["retirement_decision"] == "RETIRE_AS_OBSOLETE_RESIDUE"

    assert disposition["q3_reclassification"]["items"] == [
        {
            "global_ambiguity_id": "AMB-GOV-SURF-0875",
            "destination_family": "Q3_LIVE_PROPOSAL_HISTORY_CLASSIFICATION",
            "blocking_status_preserved": True,
            "global_resolution_status": "UNRESOLVED_RECLASSIFIED_OUT_OF_Q2",
        }
    ]

    assert [item["global_ambiguity_id"] for item in disposition["q4_reclassification"]["items"]] == [
        "AMB-GOV-SURF-0667",
        "AMB-GOV-SURF-0668",
        "AMB-GOV-SURF-0672",
        "AMB-GOV-SURF-0678",
        "AMB-GOV-SURF-0967",
    ]
    assert all(item["blocking_status_preserved"] is True for item in disposition["q4_reclassification"]["items"])

    assert queue["queue_counts"] == {"before": 9, "after": 0}
    assert queue["queue"] == []
    assert queue["preservation_assertions"]["reclassified_items_marked_globally_resolved"] is False

    assert global_updates["one_to_one_mapping_verified"] is True
    assert global_updates["count_delta"] == {
        "global_blocking_ambiguity_count_before": 487,
        "resolved_or_retired_in_this_patch": 3,
        "global_blocking_ambiguity_count_after": 484,
        "q2_group_count_before": 9,
        "q2_group_count_after": 0,
    }
    assert sum(1 for update in global_updates["updates"] if update["counts_toward_global_blocking_delta"]) == 3
