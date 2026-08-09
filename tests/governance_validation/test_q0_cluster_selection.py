from ._helpers import load_json, sha256_file
from tools.governance_inventory.q0_cluster_selector import (
    deterministic_q0_cluster_id,
    select_q0_resolution_cluster,
)


EXPECTED_INCLUDED_SURFACE_IDS = [
    "GOV-SURF-0001",
    "GOV-SURF-0002",
    "GOV-SURF-0005",
    "GOV-SURF-0103",
    "GOV-SURF-0123",
    "GOV-SURF-0132",
    "GOV-SURF-0134",
    "GOV-SURF-0881",
    "GOV-SURF-0972",
    "GOV-SURF-0994",
]

EXPECTED_GOVERNED_TARGET_IDS = [
    "GOV-SURF-0972",
    "GOV-SURF-0881",
    "GOV-SURF-0994",
    "GOV-SURF-0005",
    "GOV-SURF-0123",
]

EXPECTED_EXCLUDED_SURFACE_IDS = [
    "GOV-SURF-0006",
    "GOV-SURF-0026",
    "GOV-SURF-0043",
    "GOV-SURF-0113",
    "GOV-SURF-0127",
    "GOV-SURF-0133",
    "GOV-SURF-0986",
    "GOV-SURF-1046",
    "GOV-SURF-1047",
    "GOV-SURF-1050",
    "GOV-SURF-1051",
]

EXPECTED_QUEUE_SOURCE_HASHES = {
    "outputs/governance_inventory/governance_ambiguity_register.json": sha256_file(
        "outputs/governance_inventory/governance_ambiguity_register.json"
    ),
    "outputs/governance_inventory/governance_ambiguity_risk_classification.json": sha256_file(
        "outputs/governance_inventory/governance_ambiguity_risk_classification.json"
    ),
    "outputs/governance_inventory/governance_authority_relationships.json": sha256_file(
        "outputs/governance_inventory/governance_authority_relationships.json"
    ),
    "outputs/governance_inventory/governance_remediation_queue.json": sha256_file(
        "outputs/governance_inventory/governance_remediation_queue.json"
    ),
    "outputs/governance_inventory/governance_surface_inventory.json": sha256_file(
        "outputs/governance_inventory/governance_surface_inventory.json"
    ),
}


def test_q0_cluster_selection_file_has_expected_component():
    cluster = load_json("outputs/governance_inventory/q0_selected_resolution_cluster.json")

    assert cluster["schema_id"] == "governance_q0_resolution_cluster_v1"
    assert cluster["schema_version"] == "1.0.0"
    assert cluster["patch_id"] == "PATCH_GOVERNANCE_Q0_CLUSTER_SELECTION_AND_RESOLUTION_PACKET_006"
    assert cluster["status"] == "SELECTED_FOR_RESOLUTION"
    assert cluster["seed_ambiguity_id"] == "AMB-GOV-SURF-0972"
    assert cluster["queue_group"] == "Q0_COMPETING_AUTHORITY_AND_WRITE_PATHS"
    assert cluster["queue_position_start"] == 1
    assert cluster["selected_q0_count"] == 10
    assert cluster["all_q0_count"] == 21
    assert cluster["excluded_q0_count"] == 11
    assert cluster["recommended_resolution_mode"] == "PROVE_EXCLUSIVE_WRITE_OWNER"
    assert len(select_q0_resolution_cluster()["logical_hash"]) == 64
    assert cluster["cluster_id"] == deterministic_q0_cluster_id(
        cluster["seed_ambiguity_id"],
        cluster["included_ambiguity_ids"],
        cluster["governed_domain"]["domain_id"],
        [target["surface_id"] for target in cluster["governed_targets"]],
    )
    assert cluster["included_ambiguity_ids"] == [f"AMB-{surface_id}" for surface_id in EXPECTED_INCLUDED_SURFACE_IDS]
    assert [target["surface_id"] for target in cluster["governed_targets"]] == EXPECTED_GOVERNED_TARGET_IDS
    assert {record["surface_id"] for record in cluster["excluded_neighbor_records"]} == set(EXPECTED_EXCLUDED_SURFACE_IDS)
    assert cluster["queue_source_hashes"] == EXPECTED_QUEUE_SOURCE_HASHES
    assert cluster["source_snapshot"]["working_tree_dirty"] is True
    assert cluster["source_snapshot"]["unrelated_changes_preserved"] is True
    assert cluster["source_snapshot"]["logical_snapshot_sha256"]
    assert cluster["core_rule_reference"]["hash"] == sha256_file("governance/core_rules/GOVERNANCE_Q0_CLUSTER_COHERENCE_001.json")
    assert len(cluster["coherence_evidence"]) == 10
    assert all(record["strong_coherence_keys"] for record in cluster["coherence_evidence"])
    assert sum(1 for record in cluster["included_records"] if record["write_reachable"]) == 10
    assert sum(1 for record in cluster["included_records"] if record["validation_reachable"]) == 9
    assert sum(1 for record in cluster["included_records"] if record["read_reachable"]) == 10


def test_q0_cluster_selector_is_deterministic():
    first = select_q0_resolution_cluster()
    second = select_q0_resolution_cluster()

    assert first["cluster_id"] == second["cluster_id"]
    assert first["logical_hash"] == second["logical_hash"]
    assert first["included_ambiguity_ids"] == second["included_ambiguity_ids"]
    assert first["excluded_neighbor_records"] == second["excluded_neighbor_records"]
