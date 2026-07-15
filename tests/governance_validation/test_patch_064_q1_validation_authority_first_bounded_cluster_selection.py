from ._helpers import load_json, sha256_file


def test_patch_064_q1_inventory_and_cluster_selection_are_bounded():
    patch = load_json("patches/PATCH_GOVERNANCE_Q1_VALIDATION_AUTHORITY_FIRST_BOUNDED_CLUSTER_SELECTION_064.json")
    inventory = load_json("outputs/governance_inventory/q1_validation_authority_item_inventory.json")
    graph = load_json("outputs/governance_inventory/q1_validation_authority_conflict_graph.json")
    selection = load_json("outputs/governance_inventory/q1_first_bounded_cluster_selection.json")
    packet = load_json("outputs/governance_inventory/q1_first_validation_authority_resolution_packet.json")

    assert patch["q1_total_item_count"] == 9
    assert inventory["q1_total_item_count"] == 9
    assert len(inventory["items"]) == 9
    assert inventory["classification_count_by_authority_question"] == {
        "INVOCATION_AUTHORITY_AMBIGUITY": 1,
        "TERMINAL_REDUCTION_AUTHORITY_AMBIGUITY": 0,
        "SUPPORTING_VALIDATOR_SCOPE_AMBIGUITY": 1,
        "SCOPED_VS_COMPLETE_VALIDATION_AMBIGUITY": 0,
        "INSTRUCTION_VS_EXECUTABLE_AUTHORITY_AMBIGUITY": 1,
        "GENERATED_EVIDENCE_AUTHORITY_AMBIGUITY": 3,
        "OUTSIDE_VALIDATION_AUTHORITY_SCOPE": 3,
        "UNPROVEN": 0,
    }
    assert selection["selected_cluster_item_ids"] == ["Q1-VAL-002", "Q1-VAL-003"]
    assert selection["selected_cluster_item_count"] == 2
    assert selection["remaining_q1_item_count"] == 7
    assert packet["selected_item_identifiers"] == ["Q1-VAL-002", "Q1-VAL-003"]
    assert packet["items_resolved"] == 0
    assert packet["validation_authority_changed"] is False
    assert packet["patch_002_changed"] is False
    assert packet["full_project_validation_run"] is False

    cluster_ids = {cluster["cluster_id"] for cluster in graph["bounded_clusters"]}
    assert cluster_ids == {"Q1-CLUSTER-001", "Q1-CLUSTER-002"}


def test_patch_064_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q1_validation_authority_item_inventory.json"] == (
        sha256_file("outputs/governance_inventory/q1_validation_authority_item_inventory.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_validation_authority_conflict_graph.json"] == (
        sha256_file("outputs/governance_inventory/q1_validation_authority_conflict_graph.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_first_bounded_cluster_selection.json"] == (
        sha256_file("outputs/governance_inventory/q1_first_bounded_cluster_selection.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_first_validation_authority_resolution_packet.json"] == (
        sha256_file("outputs/governance_inventory/q1_first_validation_authority_resolution_packet.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q1_VALIDATION_AUTHORITY_FIRST_BOUNDED_CLUSTER_SELECTION_064.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q1_VALIDATION_AUTHORITY_FIRST_BOUNDED_CLUSTER_SELECTION_064.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_VALIDATION_AUTHORITY_FIRST_BOUNDED_CLUSTER_SELECTION_064.json"
        ]
        == sha256_file(
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_VALIDATION_AUTHORITY_FIRST_BOUNDED_CLUSTER_SELECTION_064.json"
        ).upper()
    )
