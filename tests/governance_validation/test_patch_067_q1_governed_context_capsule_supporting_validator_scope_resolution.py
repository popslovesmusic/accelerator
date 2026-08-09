from ._helpers import load_json, sha256_file
from tools.runtime_authority import build_live_authority_access_inventory, resolve_role_aware_authority


def test_patch_067_resolves_only_q1_val_008_as_bounded_supporting_validator():
    patch = load_json("patches/PATCH_GOVERNANCE_Q1_GOVERNED_CONTEXT_CAPSULE_SUPPORTING_VALIDATOR_SCOPE_RESOLUTION_067.json")
    resolution = load_json("outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_scope_resolution.json")
    queue = load_json("outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_active_queue.json")
    dispositions = load_json("outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_global_disposition_updates.json")

    assert patch["resolved_q1_item_ids"] == ["Q1-VAL-008"]
    assert patch["resolved_global_ambiguity_ids"] == ["AMB-GOV-SURF-1032"]
    assert patch["role_per_candidate_surface"] == {
        "tests/test_governed_context_capsule_v1.py": "SUPPORTING_VALIDATOR",
        "schemas/governed_context_capsule_v1.schema.json": "SCHEMA_CONSTRAINT_SURFACE",
        "scripts/query_governance.py": "ROLE_AWARE_AUTHORITY_QUERY_SURFACE",
    }
    assert patch["live_authority_leakage_found"] is False
    assert patch["counts"] == {
        "q1_count_before": 7,
        "q1_count_after": 6,
        "global_blocking_ambiguity_count_before": 491,
        "global_blocking_ambiguity_count_after": 490,
    }

    assert resolution["state_verification"] == {
        "q1_val_008_still_live_unresolved": True,
        "q1_val_007_still_residue_only": True,
        "q1_val_009_still_residue_only": True,
        "candidate_surface_drift_detected": False,
        "newer_patch_assigns_terminal_or_invocation_authority": False,
        "full_validation_suspension_still_active": True,
    }
    assert resolution["live_authority_leakage_review"]["result"] == "NO_LIVE_AUTHORITY_LEAKAGE"
    assert resolution["q1_item_resolution"]["Q1-VAL-008"]["resolution"] == "RESOLVED_BY_BOUNDED_SUPPORTING_VALIDATOR_SCOPE"

    assert queue["queue_counts"] == {"before": 7, "after": 6}
    assert queue["closed_work"]["selected_item_ids"] == ["Q1-VAL-008"]
    assert [entry["item_id"] for entry in queue["queue"]] == [
        "Q1-VAL-001",
        "Q1-VAL-004",
        "Q1-VAL-005",
        "Q1-VAL-006",
        "Q1-VAL-007",
        "Q1-VAL-009",
    ]
    assert queue["preservation_assertions"]["neighbor_residue_items_closed"] is False

    assert dispositions["one_to_one_mapping_verified"] is True
    assert dispositions["count_delta"] == {
        "global_blocking_ambiguity_count_before": 491,
        "resolved_in_this_patch": 1,
        "global_blocking_ambiguity_count_after": 490,
        "q1_group_count_before": 7,
        "q1_group_count_after": 6,
    }


def test_patch_067_runtime_authority_enforcement_blocks_terminal_or_invocation_collapse():
    supporting = resolve_role_aware_authority(
        "SUPPORTING_VALIDATOR",
        target="tests/test_governed_context_capsule_v1.py",
    )
    assert supporting["decision"] == "allow"

    invocation = resolve_role_aware_authority(
        "VALIDATION_INVOCATION_AUTHORITY",
        target="tests/test_governed_context_capsule_v1.py",
    )
    assert invocation["decision"] == "block"
    assert "SUPPORTING_VALIDATOR" in invocation["warnings"][0]

    reduction = resolve_role_aware_authority(
        "VALIDATION_REDUCTION_AUTHORITY",
        target="tests/test_governed_context_capsule_v1.py",
    )
    assert reduction["decision"] == "block"
    assert "SUPPORTING_VALIDATOR" in reduction["warnings"][0]

    schema = resolve_role_aware_authority(
        "SCHEMA_CONSTRAINT_SURFACE",
        target="schemas/governed_context_capsule_v1.schema.json",
    )
    assert schema["decision"] == "allow"

    query_surface = resolve_role_aware_authority(
        "ROLE_AWARE_AUTHORITY_QUERY_SURFACE",
        target="scripts/query_governance.py",
    )
    assert query_surface["decision"] == "allow"

    inventory = build_live_authority_access_inventory()
    classifications = {record["path"]: record["classification"] for record in inventory["records"]}
    assert classifications["tests/test_governed_context_capsule_v1.py"] == "SUPPORTING_VALIDATOR"
    assert classifications["schemas/governed_context_capsule_v1.schema.json"] == "SCHEMA_CONSTRAINT_SURFACE"
    assert classifications["scripts/query_governance.py"] == "ROLE_AWARE_AUTHORITY_QUERY_SURFACE"


def test_patch_067_hashes_are_registered():
    hash_registry = load_json("registry/governance_hash_registry.json")

    assert hash_registry["hashes"]["outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_scope_resolution.json"] == (
        sha256_file("outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_scope_resolution.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_active_queue.json"] == (
        sha256_file("outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_active_queue.json").upper()
    )
    assert hash_registry["hashes"]["outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_global_disposition_updates.json"] == (
        sha256_file("outputs/governance_inventory/q1_governed_context_capsule_supporting_validator_global_disposition_updates.json").upper()
    )
    assert hash_registry["hashes"]["patches/PATCH_GOVERNANCE_Q1_GOVERNED_CONTEXT_CAPSULE_SUPPORTING_VALIDATOR_SCOPE_RESOLUTION_067.json"] == (
        sha256_file("patches/PATCH_GOVERNANCE_Q1_GOVERNED_CONTEXT_CAPSULE_SUPPORTING_VALIDATOR_SCOPE_RESOLUTION_067.json").upper()
    )
    assert (
        hash_registry["hashes"][
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_GOVERNED_CONTEXT_CAPSULE_SUPPORTING_VALIDATOR_SCOPE_RESOLUTION_067.json"
        ]
        == sha256_file(
            "registry/governance/patches/PATCH_GOVERNANCE_Q1_GOVERNED_CONTEXT_CAPSULE_SUPPORTING_VALIDATOR_SCOPE_RESOLUTION_067.json"
        ).upper()
    )
