from ._helpers import load_json, sha256_file


def test_patch_065_resolves_only_the_selected_q1_invocation_boundary_items():
    patch = load_json("patches/PATCH_GOVERNANCE_Q1_VALIDATION_INVOCATION_AUTHORITY_BOUNDARY_RESOLUTION_065.json")
    resolution = load_json("outputs/governance_inventory/q1_validation_invocation_boundary_resolution.json")
    queue = load_json("outputs/governance_inventory/q1_validation_authority_active_queue.json")
    dispositions = load_json("outputs/governance_inventory/q1_validation_invocation_global_disposition_updates.json")

    assert patch["resolved_q1_item_ids"] == ["Q1-VAL-002", "Q1-VAL-003"]
    assert patch["resolved_global_ambiguity_ids"] == ["AMB-GOV-SURF-0665", "AMB-GOV-SURF-0663"]
    assert patch["validation_invocation_authority"] == "scripts/global_validate.py"
    assert patch["validation_invocation_authority_count"] == 1
    assert patch["role_per_candidate_surface"] == {
        "scripts/global_validate.py": "VALIDATION_INVOCATION_AUTHORITY",
        "docs/governance/GLOBAL_VALIDATION_ROUTINE.md": "INSTRUCTION_AUTHORITY",
        "registry/db/migrations/20260703_governance_runtime_authority_resolution_003.sql": "DB_RUNTIME_OWNERSHIP_PROJECTION",
        "registry/db/README.md": "DESCRIPTIVE_RUNTIME_GUIDANCE",
        "scripts/query_governance.py": "ROLE_AWARE_AUTHORITY_QUERY_SURFACE",
    }

    assert resolution["validation_invocation_authority"]["authority_surface"] == "scripts/global_validate.py"
    assert resolution["validation_invocation_authority"]["authority_count"] == 1
    assert resolution["legacy_claim_review"]["result"] == "ACTIVE_LEGACY_CLAIMS_FOUND"
    assert resolution["legacy_claim_review"]["historical_records_rewritten"] is False
    assert resolution["global_inventory_delta"] == {
        "one_to_one_mapping_verified": True,
        "resolved_item_count": 2,
        "global_blocking_ambiguity_count_before": 493,
        "global_blocking_ambiguity_count_after": 491,
        "q1_item_count_before": 9,
        "q1_item_count_after": 7,
    }

    assert queue["queue_counts"] == {"before": 9, "after": 7}
    assert queue["closed_work"]["selected_item_ids"] == ["Q1-VAL-002", "Q1-VAL-003"]
    assert [entry["item_id"] for entry in queue["queue"]] == [
        "Q1-VAL-001",
        "Q1-VAL-004",
        "Q1-VAL-005",
        "Q1-VAL-006",
        "Q1-VAL-007",
        "Q1-VAL-008",
        "Q1-VAL-009",
    ]

    assert dispositions["count_delta"] == {
        "global_blocking_ambiguity_count_before": 493,
        "resolved_in_this_patch": 2,
        "global_blocking_ambiguity_count_after": 491,
        "q1_group_count_before": 9,
        "q1_group_count_after": 7,
    }
    assert [entry["ambiguity_id"] for entry in dispositions["updates"]] == [
        "AMB-GOV-SURF-0665",
        "AMB-GOV-SURF-0663",
    ]
    assert dispositions["patch_002_state"]["changed"] is False


def test_patch_065_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q1_validation_invocation_boundary_resolution.json"] == (
        sha256_file("outputs/governance_inventory/q1_validation_invocation_boundary_resolution.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_validation_authority_active_queue.json"] == (
        sha256_file("outputs/governance_inventory/q1_validation_authority_active_queue.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_validation_invocation_global_disposition_updates.json"] == (
        sha256_file("outputs/governance_inventory/q1_validation_invocation_global_disposition_updates.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q1_VALIDATION_INVOCATION_AUTHORITY_BOUNDARY_RESOLUTION_065.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q1_VALIDATION_INVOCATION_AUTHORITY_BOUNDARY_RESOLUTION_065.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_VALIDATION_INVOCATION_AUTHORITY_BOUNDARY_RESOLUTION_065.json"
        ]
        == sha256_file(
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_VALIDATION_INVOCATION_AUTHORITY_BOUNDARY_RESOLUTION_065.json"
        ).upper()
    )
